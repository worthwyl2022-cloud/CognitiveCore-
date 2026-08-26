package com.example.core.product

import java.util.UUID

/**
 * Thin product surface: multi-project isolation + Creative Constitution +
 * quarantine inbox + provenance stubs.
 *
 * Persistence is intentionally a simple in-memory store with export hooks.
 * Swap [ProjectRepository] for Room/SQL/filesystem without changing API.
 */

data class Principle(
    val id: String = UUID.randomUUID().toString(),
    val text: String,
    val locked: Boolean = true,
    val createdAt: Long = System.currentTimeMillis(),
    val createdBy: String = "human",
    val note: String = "",
    val version: Int = 1
)

data class ProvenanceEvent(
    val id: String = UUID.randomUUID().toString(),
    val at: Long = System.currentTimeMillis(),
    val actor: String,
    val action: String, // seed_principle | inject | generate | protect_block | approve | reject
    val detail: String,
    val atomId: String? = null,
    val principleId: String? = null
)

data class QuarantineItem(
    val atomId: String,
    val content: String,
    val evalScores: Map<String, Double> = emptyMap(),
    val directivesAtBirth: List<String> = emptyList(),
    val createdAt: Long = System.currentTimeMillis(),
    val generator: String = ""
)

data class Project(
    val id: String = UUID.randomUUID().toString(),
    val name: String,
    val createdAt: Long = System.currentTimeMillis(),
    val constitution: MutableList<Principle> = mutableListOf(),
    val canonFacts: MutableList<String> = mutableListOf(),
    val quarantine: MutableList<QuarantineItem> = mutableListOf(),
    val provenance: MutableList<ProvenanceEvent> = mutableListOf(),
    /** Opaque handle to substrate instance — caller owns lifecycle. */
    var substrateKey: String = id
)

interface ProjectRepository {
    fun list(): List<Project>
    fun get(id: String): Project?
    fun save(project: Project)
    fun delete(id: String)
}

class InMemoryProjectRepository : ProjectRepository {
    private val map = linkedMapOf<String, Project>()
    override fun list(): List<Project> = map.values.toList()
    override fun get(id: String): Project? = map[id]
    override fun save(project: Project) {
        map[project.id] = project
    }
    override fun delete(id: String) {
        map.remove(id)
    }
}

/**
 * Product API façade — what a studio UI or HTTP layer should call.
 */
class CreativeOsApi(
    private val repo: ProjectRepository = InMemoryProjectRepository()
) {

    fun createProject(name: String, seedPrinciples: List<String> = emptyList()): Project {
        val p = Project(name = name)
        seedPrinciples.forEach { text ->
            val pr = Principle(text = text, locked = true, createdBy = "human")
            p.constitution.add(pr)
            p.provenance.add(
                ProvenanceEvent(
                    actor = "human",
                    action = "seed_principle",
                    detail = text.take(200),
                    principleId = pr.id
                )
            )
        }
        repo.save(p)
        return p
    }

    fun listProjects(): List<Project> = repo.list()

    fun getProject(id: String): Project? = repo.get(id)

    fun addPrinciple(projectId: String, text: String, locked: Boolean = true, by: String = "human"): Principle? {
        val p = repo.get(projectId) ?: return null
        val pr = Principle(text = text, locked = locked, createdBy = by)
        p.constitution.add(pr)
        p.provenance.add(
            ProvenanceEvent(actor = by, action = "seed_principle", detail = text.take(200), principleId = pr.id)
        )
        repo.save(p)
        return pr
    }

    fun addCanonFact(projectId: String, fact: String): Boolean {
        val p = repo.get(projectId) ?: return false
        if (fact !in p.canonFacts) {
            p.canonFacts.add(fact)
            p.provenance.add(
                ProvenanceEvent(actor = "human", action = "seed_canon", detail = fact.take(200))
            )
            repo.save(p)
        }
        return true
    }

    fun constitution(projectId: String): List<Principle> =
        repo.get(projectId)?.constitution?.toList() ?: emptyList()

    fun enqueueQuarantine(projectId: String, item: QuarantineItem): Boolean {
        val p = repo.get(projectId) ?: return false
        p.quarantine.add(item)
        p.provenance.add(
            ProvenanceEvent(
                actor = item.generator.ifBlank { "generator" },
                action = "generate",
                detail = "quarantine ${item.atomId}",
                atomId = item.atomId
            )
        )
        repo.save(p)
        return true
    }

    fun quarantineInbox(projectId: String): List<QuarantineItem> =
        repo.get(projectId)?.quarantine?.toList() ?: emptyList()

    /**
     * Human gate: approve removes from quarantine list (substrate promote is caller's job).
     */
    fun approve(projectId: String, atomId: String, by: String = "human"): QuarantineItem? {
        val p = repo.get(projectId) ?: return null
        val item = p.quarantine.firstOrNull { it.atomId == atomId } ?: return null
        p.quarantine.removeAll { it.atomId == atomId }
        p.provenance.add(
            ProvenanceEvent(actor = by, action = "approve", detail = "approved $atomId", atomId = atomId)
        )
        repo.save(p)
        return item
    }

    fun reject(projectId: String, atomId: String, by: String = "human", reason: String = ""): Boolean {
        val p = repo.get(projectId) ?: return false
        val before = p.quarantine.size
        p.quarantine.removeAll { it.atomId == atomId }
        if (p.quarantine.size == before) return false
        p.provenance.add(
            ProvenanceEvent(
                actor = by,
                action = "reject",
                detail = reason.ifBlank { "rejected $atomId" },
                atomId = atomId
            )
        )
        repo.save(p)
        return true
    }

    fun recordProtect(projectId: String, detail: String, atomId: String? = null) {
        val p = repo.get(projectId) ?: return
        p.provenance.add(
            ProvenanceEvent(actor = "system", action = "protect_block", detail = detail, atomId = atomId)
        )
        repo.save(p)
    }

    fun auditLog(projectId: String): List<ProvenanceEvent> =
        repo.get(projectId)?.provenance?.toList() ?: emptyList()

    /** JSON-ish export for diligence / backup (no secrets). */
    fun exportProject(projectId: String): Map<String, Any?> {
        val p = repo.get(projectId) ?: return emptyMap()
        return mapOf(
            "id" to p.id,
            "name" to p.name,
            "createdAt" to p.createdAt,
            "constitution" to p.constitution.map {
                mapOf(
                    "id" to it.id,
                    "text" to it.text,
                    "locked" to it.locked,
                    "createdBy" to it.createdBy,
                    "version" to it.version
                )
            },
            "canonFacts" to p.canonFacts.toList(),
            "quarantineCount" to p.quarantine.size,
            "provenance" to p.provenance.map {
                mapOf(
                    "at" to it.at,
                    "actor" to it.actor,
                    "action" to it.action,
                    "detail" to it.detail
                )
            }
        )
    }
}
