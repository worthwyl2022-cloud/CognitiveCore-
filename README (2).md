# Product API surface

Minimal **Creative OS** boundary for a studio / writer product:

| API | Purpose |
|-----|---------|
| `createProject` | Isolated workspace |
| `addPrinciple` / `constitution` | Creative Constitution editor data |
| `addCanonFact` | Immutable canon lane feed |
| `quarantineInbox` / `approve` / `reject` | Human gate |
| `auditLog` / `exportProject` | Provenance + diligence export |

## Isolation

Each `Project` has its own constitution, canon, quarantine, and provenance.  
Wire one `SubstrateCore` (or field) per `substrateKey` so memory does not cross projects.

## Persistence

`InMemoryProjectRepository` is the default. Implement `ProjectRepository` with Room / files / Postgres for durability.

## UI mapping

1. Constitution editor → `addPrinciple` / list `constitution`
2. Corpus ingest → `addCanonFact` + substrate inject
3. Quarantine inbox → `quarantineInbox` + approve/reject
4. Why blocked? → `auditLog` filter `protect_block`
