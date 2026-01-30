# Migration Kit Architecture

## System Components

1.  **Brain**: `migration-orchestrator` (The Manager)
2.  **Eyes**: `vb6-analyst` (The Reader)
3.  **Hands**: `angular-architect` & `backend-engineer` (The Builders)
4.  **Foundation**: `data-migrator` (The Mover)

## Execution Layers

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| **L0** | Rules | The Law. Immutable constraints (e.g., No 'any'). |
| **L1** | Workflows | The Process. Sequences of steps (e.g. /audit). |
| **L2** | Agents | The Intelligence. Reasoning within a step. |
| **L3** | Skills | The Knowledge. Specific patterns & practices. |
| **L4** | Scripts | The Muscle. Deterministic file operations. |

## Dependency Graph

*   `angular-architect` DEPENDS ON `vb6-analyst` (Needs specs).
*   `backend-engineer` DEPENDS ON `data-migrator` (Needs DB Schema).
*   `orchestrator` DEPENDS ON `ALL`.
