# Reverse Knowledge Tree Algorithm

The Reverse Knowledge Tree is the core innovation that eliminates the need for training data in generating educational animations.

## The Core Insight

Traditional approaches require training on example animations. This system instead uses pure reasoning:

**For any concept X, recursively ask: "What must I understand BEFORE X?"**

This builds a Directed Acyclic Graph (DAG) of knowledge dependencies that naturally produces pedagogically sound content.

## Algorithm Details

### Data Structure: KnowledgeNode

```python
@dataclass
class KnowledgeNode:
    concept: str           # The concept name
    depth: int             # 0 = target, higher = more foundational
    is_foundation: bool    # True if no further prerequisites needed
    prerequisites: List['KnowledgeNode']  # Child nodes

    # Added by enrichment agents
    equations: Optional[List[str]]        # LaTeX equations
    definitions: Optional[Dict[str, str]] # Variable definitions
    visual_spec: Optional[Dict]           # Animation specifications
    narrative: Optional[str]              # Scene description
```

### Exploration Process

```python
async def explore(concept: str, depth: int = 0) -> KnowledgeNode:
    # Check termination conditions
    if depth >= max_depth or is_foundation(concept):
        return KnowledgeNode(
            concept=concept,
            depth=depth,
            is_foundation=True,
            prerequisites=[]
        )

    # Discover prerequisites via LLM
    prerequisites = await discover_prerequisites(concept)

    # Recursively explore each prerequisite
    child_nodes = []
    for prereq in prerequisites:
        child_nodes.append(await explore(prereq, depth + 1))

    return KnowledgeNode(
        concept=concept,
        depth=depth,
        is_foundation=False,
        prerequisites=child_nodes
    )
```

### Foundation Detection

A concept is foundational if a typical high school graduate would understand it without further explanation.

**Examples of foundation concepts:**
- velocity, distance, time, acceleration
- force, mass, energy
- waves, frequency, wavelength
- numbers, addition, multiplication
- basic geometry (points, lines, angles)
- functions, graphs

**Examples of non-foundation concepts:**
- Lorentz transformations
- gauge theory
- differential geometry
- tensor calculus
- quantum operators
- Hilbert spaces

### Prerequisite Discovery Prompt

```
You are an expert educator and curriculum designer.

Your task is to identify the ESSENTIAL prerequisite concepts someone must
understand BEFORE they can grasp a given concept.

Rules:
1. Only list concepts that are NECESSARY for understanding (not just helpful)
2. Order from most to least important
3. Assume high school education as baseline
4. Focus on concepts that enable understanding, not historical context
5. Be specific - prefer "special relativity" over "relativity"
6. Limit to 3-5 prerequisites maximum

Return ONLY a JSON array of concept names.
```

## Caching Strategy

To avoid redundant API calls:
1. **In-memory cache**: Store discovered prerequisites by concept name
2. **Optional Atlas integration**: Use Nomic Atlas for semantic caching and search

```python
async def lookup_prerequisites(concept: str) -> List[str]:
    # Check cache first
    if concept in cache:
        return cache[concept]

    # Check Atlas if enabled
    if atlas_client:
        results = atlas_client.search_similar(concept)
        if exact_match_found(results):
            return results[0].prerequisites

    # Discover via LLM
    prerequisites = await discover_prerequisites(concept)

    # Cache results
    cache[concept] = prerequisites
    if atlas_client:
        atlas_client.store(concept, prerequisites)

    return prerequisites
```

## Tree Traversal for Animation

After building the tree, traverse from leaves (foundations) to root (target):

### Topological Sort

```python
def topological_sort(root: KnowledgeNode) -> List[KnowledgeNode]:
    visited = set()
    result = []

    def dfs(node):
        if node.concept in visited:
            return
        visited.add(node.concept)

        # Visit prerequisites first (foundations)
        for prereq in node.prerequisites:
            dfs(prereq)

        # Then add this node
        result.append(node)

    dfs(root)
    return result  # Foundation -> Target order
```

This ensures:
- Foundation concepts appear first in animation
- Each concept builds on previously explained ones
- Viewers have necessary background before advanced topics

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_depth` | 4 | Maximum tree depth before forcing foundation |
| `max_prerequisites` | 5 | Maximum prerequisites per concept |
| `cache_enabled` | True | Use in-memory caching |
| `atlas_enabled` | False | Use Nomic Atlas for persistent caching |

## Example Tree

**Input**: "Explain quantum tunneling"

**Generated Tree**:
```
quantum tunneling (depth 0)
├─ wave-particle duality (depth 1)
│   ├─ de Broglie wavelength (depth 2) [FOUNDATION]
│   └─ Heisenberg uncertainty principle (depth 2)
│       └─ wave function (depth 3) [FOUNDATION]
├─ Schrödinger equation (depth 1)
│   ├─ wave function (depth 2) [FOUNDATION]
│   └─ potential energy (depth 2) [FOUNDATION]
└─ potential barriers (depth 1) [FOUNDATION]
```

**Animation Order** (after topological sort):
1. de Broglie wavelength
2. wave function
3. Heisenberg uncertainty principle
4. wave-particle duality
5. potential energy
6. potential barriers
7. Schrödinger equation
8. quantum tunneling

Each concept builds on what came before, creating a natural learning progression.
