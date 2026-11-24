import { createHash } from 'node:crypto'
import { lstatSync, readFileSync } from 'node:fs'
import { dirname, isAbsolute, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const sha256 = bytes => createHash('sha256').update(bytes).digest('hex')
const schemaPath = 'resources/contracts/fpga-protocol/control.schema.json'

export function verifyNativeContracts(receipt, expectedSha256) {
  if (!receipt || !isAbsolute(receipt) || !/^[a-f0-9]{64}$/.test(expectedSha256 ?? '') || !lstatSync(receipt).isFile()) {
    throw new Error('Select an absolute native Contracts receipt and its reviewed SHA-256.')
  }
  const bytes = readFileSync(receipt)
  if (sha256(bytes) !== expectedSha256) throw new Error('Native Contracts receipt SHA-256 mismatch.')
  const bundle = JSON.parse(bytes)
  if (bundle.schemaVersion !== 1 || bundle.component !== 'cirnet-contracts' ||
      !/^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/.test(bundle.version ?? '') ||
      !(bundle.revision === null || /^[a-f0-9]{40}$/.test(bundle.revision ?? '')) ||
      !/^[a-f0-9]{64}$/.test(bundle.sourceSha256 ?? '') ||
      !Array.isArray(bundle.files)) throw new Error('Expected a native Contracts producer receipt.')

  function resource(name) {
    const entries = bundle.files.filter(record => record.path === name)
    const path = resolve(dirname(receipt), name)
    if (entries.length !== 1 || !lstatSync(path).isFile()) throw new Error(`Missing native Contracts resource: ${name}`)
    const data = readFileSync(path)
    if (data.length !== entries[0].size || sha256(data) !== entries[0].sha256) {
      throw new Error(`Selected native Contracts resource differs from the receipt: ${name}`)
    }
    return data
  }

  const registry = JSON.parse(resource('resources/contracts/manifest.json'))
  const schema = resource(schemaPath)
  if (!registry.contracts?.some(record => record.id === 'FpgaControlScaffold' && record.version === '1.0-scaffold') ||
      JSON.parse(schema).properties?.protocol_version?.const !== '1.0-scaffold') {
    throw new Error('Selected native Contracts logical FPGA protocol is incompatible.')
  }
  return { version: bundle.version, revision: bundle.revision, sourceSha256: bundle.sourceSha256, manifestSha256: expectedSha256, schemaSha256: sha256(schema) }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    console.log(JSON.stringify(verifyNativeContracts(process.argv[2], process.argv[3])))
  } catch (error) {
    console.error(error.message)
    process.exitCode = 1
  }
}
