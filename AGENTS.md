# Embedded Hardware repository work

- Keep task plans in `.superpowers/plans/` and corresponding specs, acceptance criteria and checklists in `.superpowers/specs/`. Use `- [ ]` for open work and `- [x]` after verification.
- Search existing documentation before adding anything. Update the authoritative page, consolidate duplication and verify references. Update paired [English](docs/en/index.md) and [Vietnamese](docs/vi/index.md) pages and the applicable [changelog](docs/changelogs/README.md).
- Preserve canonical RTL interfaces, both behavioral markers, the toolchain selection and safety permits. Contracts owns the logical schema, Hardware owns private transport, and Remote owns system release selection.
- Distinguish TARGET, IMPLEMENTED, TESTED, VERIFIED, RELEASED, UNAVAILABLE and BLOCKED. Keep physical firmware and transport UNAVAILABLE pending board-specific qualification.
- Verify with the shared allocator outside checkouts and Git directories. Use Python for isolated verification and Node for source packaging.
- Review status, diff and ignored outputs. Stage, commit, tag or push only on request.
