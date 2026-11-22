/** Deterministic source-only FPGA candidate packaging. */
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { closeSync, existsSync, lstatSync, openSync, readdirSync, readFileSync, realpathSync, unlinkSync, writeFileSync } from 'node:fs'
import { basename, dirname, extname, isAbsolute, join, relative, resolve, sep } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { parseArgs } from 'node:util'
import { gzipSync } from 'node:zlib'
import { verifyNativeContracts } from './native-contracts.mjs'

const root = realpathSync(resolve(dirname(fileURLToPath(import.meta.url)), '..'))
const repository = 'https://github.com/cirnetlab/cirnet-embedded-hardware.git'
const allowed = new Set(['.json', '.md', '.v', '.sv', '.vh', '.svh', '.tcl'])
const sha256 = data => createHash('sha256').update(data).digest('hex')
const sortedNames = files => [...files.keys()].sort((a, b) => Buffer.compare(Buffer.from(a), Buffer.from(b)))
const unsafePart = part => /[<>:"\\|?*\x00-\x1f]|[. ]$/.test(part) ||
  /^(?:\.git|CON|PRN|AUX|NUL|COM[1-9Â¹Â²Â³]|LPT[1-9Â¹Â²Â³])(?:\.|$)/i.test(part)
const inside = (base, file) => {
  const path = relative(base, file)
  return path !== '..' && !path.startsWith('..' + sep) && !isAbsolute(path)
}

function selectedSource(path) {
  const source = { repository, revision: null, uncommittedMigration: true }
  if (path) {
    const supplied = JSON.parse(readFileSync(path, 'utf8'))
    if (supplied.repository !== repository ||
        !(supplied.revision === null || /^[a-f0-9]{40}$/.test(supplied.revision ?? '')) ||
        !/^[a-f0-9]{64}$/.test(supplied.sourceSha256 ?? '') ||
        typeof supplied.uncommittedMigration !== 'boolean') {
      throw new Error('Invalid Embedded Hardware source provenance.')
    }
    Object.assign(source, {revision: supplied.revision, sourceSha256: supplied.sourceSha256,
      uncommittedMigration: supplied.uncommittedMigration})
  }
  if (existsSync(join(root, '.git'))) {
    const env = { ...process.env }
    for (const key of Object.keys(env)) {
      if (['GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'].includes(key.toUpperCase())) delete env[key]
    }
    const git = (...args) => execFileSync('git', ['--no-optional-locks', '-C', root, ...args], { encoding: 'utf8', env }).trim()
    source.revision = git('rev-parse', '--verify', 'HEAD')
    source.uncommittedMigration = Boolean(git('status', '--porcelain=v1', '--untracked-files=all'))
  }
  return source
}

function sourceFiles() {
  const files = new Map()
  const spelling = new Set()
  let size = 0
  function add(name) {
    const parts = name.split('/')
    if (parts.some(unsafePart)) {
      throw new Error(`Unsafe source path: ${name}`)
    }
    const key = name.toLowerCase()
    if (spelling.has(key)) throw new Error(`Case-colliding source path: ${name}`)
    spelling.add(key)
    const path = join(root, ...parts)
    const stat = lstatSync(path)
    if (stat.isSymbolicLink() || realpathSync(path) !== path) throw new Error(`Source aliases are unsupported: ${name}`)
    if (stat.isDirectory()) {
      for (const entry of readdirSync(path)) add(`${name}/${entry}`)
      return
    }
    if (!stat.isFile() || (parts.length > 1 && !allowed.has(extname(name)) && basename(name) !== '.gitkeep')) {
      throw new Error(`Unexpected product source file: ${name}`)
    }
    size += stat.size
    if (size > 127 * 1024 * 1024 || files.size >= 9_999) throw new Error('FPGA source exceeds archive limits.')
    const bytes = readFileSync(path)
    if (bytes.length !== stat.size) throw new Error(`Source changed while packaging: ${name}`)
    files.set(name, bytes)
  }

  for (const name of ['LICENSE', 'README.md', 'VERSION', 'rtl', 'verification', 'docs', 'integration']) add(name)
  for (const required of ['rtl/experiment-controller/top.v', 'rtl/instrument/top.v',
    'verification/rtl/tb_lab_first_control.v', 'verification/rtl/tb_permit_matrix.v']) {
    if (!files.has(required)) throw new Error(`Missing required source: ${required}`)
  }
  return files
}

function tarGzip(files) {
  const records = []
  for (const name of sortedNames(files)) {
    const data = files.get(name)
    const header = Buffer.alloc(512)
    if (Buffer.byteLength(name) > 100) throw new Error(`FPGA archive path exceeds 100 UTF-8 bytes: ${name}`)
    header.write(name, 0, 100)
    const octal = (value, offset, width) => header.write(value.toString(8).padStart(width - 1, '0'), offset)
    octal(0o644, 100, 8)
    octal(0, 108, 8)
    octal(0, 116, 8)
    octal(data.length, 124, 12)
    octal(0, 136, 12)
    header.fill(0x20, 148, 156)
    header.write('0', 156)
    header.write('ustar\0' + '00', 257)
    const checksum = header.reduce((sum, byte) => sum + byte, 0)
    header.write(checksum.toString(8).padStart(6, '0') + '\0 ', 148)
    records.push(header, data, Buffer.alloc((512 - data.length % 512) % 512))
  }
  records.push(Buffer.alloc(1024))
  return gzipSync(Buffer.concat(records), { level: 9 })
}

async function build(output, provenance, allocatorPath, allocatorSha256, contractsReceipt, contractsSha256) {
  if (!isAbsolute(output)) throw new Error('Source archive output must be absolute and allocator-owned.')
  if (inside(root, resolve(output))) throw new Error('Source archive output cannot be inside product source.')
  if (!output.endsWith('.tar.gz') || unsafePart(basename(output))) throw new Error('Expected a safe .tar.gz source archive name.')
  const native = verifyNativeContracts(contractsReceipt, contractsSha256)
  if (!allocatorPath || !isAbsolute(allocatorPath) || !/^[a-f0-9]{64}$/.test(allocatorSha256 ?? '')) {
    throw new Error('Select an absolute DEV allocator and its reviewed SHA-256.')
  }
  const modulePath = realpathSync(allocatorPath)
  if (sha256(readFileSync(modulePath)) !== allocatorSha256) throw new Error('DEV allocator SHA-256 differs from selection.')
  const allocator = await import(pathToFileURL(modulePath).href)
  const inherited = process.env.CIRNET_ARTIFACTS_SESSION
  if (!inherited) throw new Error('Set CIRNET_ARTIFACTS_SESSION to a pinned allocator-owned external session.')
  const session = allocator.getArtifactDirectory()
  const parent = allocator.validateArtifactDirectory(dirname(output))
  if (!inside(session, parent) || inside(root, parent)) throw new Error('Source archive output must stay inside the owned session and outside product source.')
  const destination = join(parent, basename(output))
  const source = selectedSource(provenance)
  const files = sourceFiles()
  const version = files.get('VERSION').toString().trim()
  if (!/^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/.test(version)) throw new Error('Unsupported scaffold source version.')
  const filename = `cirnet-embedded-hardware-${version}-native-source.tar.gz`
  if (basename(destination) !== filename) throw new Error(`Expected candidate archive name ${filename}.`)
  const hashes = Object.fromEntries(sortedNames(files).map(name => [name, sha256(files.get(name))]))
  const fingerprint = sha256(Object.entries(hashes).map(([name, digest]) => `${digest}  ${name}\n`).join(''))
  const identity = { schemaVersion: 1, name: 'cirnet-embedded-hardware', version, kind: 'source',
    contractsVersion: native.version, contracts: native,
    logicalProtocolVersion: '1.0-scaffold', registerMapVersion: '1.0-reserved',
    physicalAvailable: false, source, files: hashes, sourceFingerprint: fingerprint }
  const metadata = Buffer.from(JSON.stringify(identity, null, 2) + '\n')
  if (metadata.length > 1024 * 1024) throw new Error('FPGA source identity exceeds archive limits.')
  files.set('fpga-artifact.json', metadata)
  const bytes = tarGzip(files)
  if (bytes.length > 128 * 1024 * 1024) throw new Error('FPGA source exceeds compressed archive limits.')
  const handle = openSync(destination, 'wx')
  try {
    try { writeFileSync(handle, bytes) } finally { closeSync(handle) }
  } catch (error) {
    unlinkSync(destination)
    throw error
  }
  return { schemaVersion: 1, version, source: { path: destination, filename, size: bytes.length, sha256: sha256(bytes) },
    sourceFingerprint: fingerprint,
    revision: source.revision, uncommittedMigration: source.uncommittedMigration, target: 'portable-source',
    toolchain: { node: process.version, zlib: process.versions.zlib } }
}

try {
  const { values } = parseArgs({ options: {
    output: { type: 'string' }, provenance: { type: 'string' }, allocator: { type: 'string' },
    'contracts-receipt': { type: 'string' }, 'contracts-sha256': { type: 'string' },
    'allocator-sha256': { type: 'string' },
  } })
  if (!values.output) {
    throw new Error('Usage: node scripts/build-source.mjs --output ABSOLUTE_ARCHIVE --contracts-receipt FILE --contracts-sha256 HASH [--provenance FILE] [--allocator FILE --allocator-sha256 HASH]')
  }
  const allocator = values.allocator ?? process.env.CIRNET_ARTIFACTS_CLI
  console.log(JSON.stringify(await build(values.output, values.provenance, allocator,
    values['allocator-sha256'] ?? process.env.CIRNET_ARTIFACTS_CLI_SHA256,
    values['contracts-receipt'], values['contracts-sha256']), null, 2))
} catch (error) {
  console.error(`build-source: ${error.message}`)
  process.exitCode = 1
}
