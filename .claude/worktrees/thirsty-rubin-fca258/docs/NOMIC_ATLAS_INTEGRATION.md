# Nomic Atlas Integration for Knowledge Tree Visualization

**Status**: Aspirational Feature / Research Phase
**Priority**: High Impact, Medium Term (Phase 3-4)
**Added**: 2025-10-04

---

## Why Nomic Atlas?

Nomic Atlas is the world's most powerful unstructured data interaction platform, purpose-built for exactly what we need:

1. **Hierarchical Topic Modeling** - Native support for multi-level topic hierarchies (2-3 levels)
2. **Semantic Embeddings** - Generate embeddings for concepts to find natural relationships
3. **Interactive Visualization** - Web-based maps showing concept relationships
4. **Vector Search** - Find similar concepts and prerequisites automatically
5. **Python API** - Seamless integration with our existing Claude-based agents

### The Vision

Instead of manually asking Claude "What must I know before X?" for every concept, we could:

1. **Embed all mathematical/scientific concepts** into Nomic Atlas
2. **Automatically discover prerequisite relationships** via semantic similarity
3. **Visualize the entire knowledge graph** interactively in the browser
4. **Cache prerequisite trees** for instant reuse across users
5. **Find optimal learning paths** by analyzing the graph structure

---

## How It Would Work

### Current Approach (Manual Recursion)
```
User: "Explain cosmology"
  v
Claude: "Prerequisites: GR, Hubble's Law, Redshift..."
  v
Claude: "For GR, prerequisites: SR, diff geometry..."
  v
Claude: "For SR, prerequisites: Galilean relativity..."
  v
[3-4 API calls, ~30-60 seconds]
```

### With Nomic Atlas (Semantic Graph)
```
User: "Explain cosmology"
  v
Atlas: Query "cosmology" embedding -> retrieve cached prerequisite tree
  v
[Instant response, pre-computed graph]
```

**Benefits**:
- [FAST] **Instant prerequisite lookup** (no repeated Claude calls)
- [WEB] **Shared knowledge graph** (everyone benefits from improvements)
- [SEARCH] **Discover unexpected connections** (e.g., "topology prerequisite for QFT")
- [STATS] **Visualize learning paths** (show users their progress)
- [COST] **Massive cost savings** (cache all prerequisite queries)

---

## Architecture Integration

### Phase 1: Concept Embedding (Foundation)

```python
from nomic import embed, AtlasDataset
import json

# Define our domain of concepts (physics, math, CS)
concepts = [
    "quantum mechanics", "special relativity", "general relativity",
    "linear algebra", "calculus", "differential equations",
    "fourier analysis", "topology", "group theory",
    # ... hundreds more
]

# Generate semantic embeddings
embeddings = embed.text(
    texts=concepts,
    model='nomic-embed-text-v1.5',
    task_type='clustering'  # We want to cluster related concepts
)

# Create Atlas dataset
dataset = AtlasDataset('math-to-manim-knowledge-graph')
dataset.add_data(
    embeddings=embeddings['embeddings'],
    data=[{"concept": c} for c in concepts]
)

# Create interactive map
atlas_map = dataset.create_index()
print(f"View your knowledge graph: {atlas_map.map_link}")
```

### Phase 2: Prerequisite Discovery (Enhanced)

Instead of asking Claude every time, we can use semantic similarity:

```python
from nomic import AtlasDataset

# Load our knowledge graph
dataset = AtlasDataset('math-to-manim-knowledge-graph')

# Find concepts similar to "cosmology" (likely prerequisites)
results = dataset.vector_search(
    query="cosmology",
    k=10,  # Top 10 most similar concepts
    fields=["concept", "depth", "domain"]
)

# Results might include: general relativity, hubble's law, redshift
# These are semantically close -> likely prerequisites or related concepts
```

**Hybrid Approach** (Best of Both Worlds):
1. Use Atlas for **fast initial lookup** of likely prerequisites
2. Use Claude to **validate and order** the prerequisites pedagogically
3. Store Claude's decisions back in Atlas for future reuse

### Phase 3: Topic Hierarchy Modeling

Nomic Atlas has built-in hierarchical topic modeling:

```python
# Access the natural topic hierarchy Atlas discovered
topics = dataset.topics

# Iterate through the hierarchy
for topic_name, topic_data in topics.items():
    print(f"Topic: {topic_name}")
    print(f"  Depth: {topic_data['depth']}")
    print(f"  Subtopics: {topic_data['subtopics']}")
    print(f"  Concepts: {topic_data['datum_ids']}")
```

This could automatically organize concepts into:
- **Foundation** (depth 0): Basic algebra, geometry, calculus
- **Intermediate** (depth 1): Linear algebra, differential equations
- **Advanced** (depth 2): Topology, abstract algebra, functional analysis
- **Research** (depth 3): Quantum field theory, category theory

### Phase 4: Interactive Visualization

```python
# Create a map filtered to specific learning path
physics_path = dataset.create_index(
    name="Physics Learning Path: Basics -> QFT",
    colorable_fields=["domain", "depth"],
    id_field="concept"
)

# Users can explore this interactively in their browser
# Click on "quantum mechanics" -> see all prerequisites highlighted
# See the entire path from "basic algebra" -> "quantum field theory"
```

---

## Implementation Plan

### Stage 1: Proof of Concept (1-2 weeks)

**Goal**: Demonstrate Atlas can represent our knowledge tree

1. Create small dataset (50-100 core concepts)
2. Use `AtlasClient.upsert_concepts()` to embed and upload concepts
3. Manually tag prerequisites for validation (stored in concept metadata)
4. Create interactive map via `AtlasClient.create_map()`
5. Test semantic search accuracy

**Deliverable**: Interactive map showing physics/math concept relationships

### Stage 2: Integration with PrerequisiteExplorer (2-3 weeks)

**Goal**: Hybrid Claude + Atlas system

1. Call `PrerequisiteExplorer.enable_atlas_integration("math-to-manim-knowledge-graph")`
2. Use Atlas cache for initial prerequisite lookup
3. Fallback to Claude/DeepSeek to validate and order results
4. Store validated prerequisites back to Atlas for future reuse
5. Implement caching and telemetry around Atlas usage

**Deliverable**: 10x faster prerequisite discovery with same accuracy

### Stage 3: Knowledge Graph Enrichment (4-6 weeks)

**Goal**: Build comprehensive concept database

1. Systematically embed 500+ concepts across domains (batch uploads via `AtlasClient`)
2. Run PrerequisiteExplorer across the catalog to build prerequisite edges
3. Validate with domain experts and annotate disagreements
4. Leverage `AtlasClient.list_topics()` for automatic hierarchies
5. Generate "learning path" visualizations directly from Atlas maps

**Deliverable**: Shareable knowledge graph for STEM education

### Stage 4: Community Features (2-3 months)

**Goal**: Let users contribute and explore

1. User-submitted concepts via Atlas-backed queues
2. Voting on prerequisite relationships (stored in concept metadata)
3. Alternative learning paths using custom Atlas maps
4. Progress tracking (highlight mastered concepts)
5. Export to other formats (Neo4j, Obsidian, etc.)

**Deliverable**: Public knowledge graph platform

---

## Technical Setup

### Installation

```bash
pip install nomic

# Authenticate
nomic login
# This will open browser for API key setup
```

### Environment Variables

Add to `.env`:
```bash
NOMIC_API_KEY=your_nomic_api_key_here
```

Get API key from: https://atlas.nomic.ai/

### Basic Example

```python
from src.agents import AtlasClient, AtlasConcept


client = AtlasClient(dataset_name="test-knowledge-graph")
client.ensure_dataset()

client.upsert_concepts(
    [
        AtlasConcept("calculus", {"domain": "mathematics"}),
        AtlasConcept("linear algebra", {"domain": "mathematics"}),
        AtlasConcept("topology", {"domain": "mathematics"}),
    ]
)

map_obj = client.create_map(name="Foundational Math Concepts")
print(f"Explore at: {map_obj.map_link}")
```

---

## API Reference Summary

### Key Classes

#### `embed.text()`
Generate semantic embeddings for text

**Parameters**:
- `texts`: List of strings to embed
- `model`: `'nomic-embed-text-v1.5'` (latest)
- `task_type`: `'search_document'`, `'search_query'`, `'clustering'`, `'classification'`

**Returns**: Dictionary with `'embeddings'` key (numpy array)

#### `AtlasDataset(name)`
Create or load a dataset

**Methods**:
- `add_data(embeddings, data)` - Add embeddings with metadata
- `create_index(name, colorable_fields, id_field)` - Generate interactive map
- `vector_search(query, k, fields)` - Semantic search
- `.topics` - Access hierarchical topic structure

#### `vector_search()`
Find semantically similar items

**Parameters**:
- `query`: String (will be embedded) or embedding vector
- `k`: Number of results
- `fields`: Metadata fields to return

**Returns**: List of similar items with scores

---

## Use Cases for Math-To-Manim

### 1. Prerequisite Cache
**Problem**: Asking Claude "what before X?" is slow and costly
**Solution**: Query Atlas first, use Claude only for novel concepts

### 2. Learning Path Visualization
**Problem**: Users can't see the full journey (algebra -> QFT)
**Solution**: Interactive map showing all prerequisite chains

### 3. Concept Discovery
**Problem**: Missing unexpected prerequisites
**Solution**: Semantic search finds related concepts we didn't consider

### 4. Community Knowledge
**Problem**: Every user rebuilds the same prerequisite trees
**Solution**: Shared knowledge graph everyone contributes to

### 5. Quality Metrics
**Problem**: No way to measure "completeness" of animations
**Solution**: Check if all prerequisite concepts are covered

---

## Example: Cosmology Knowledge Graph

```python
from nomic import AtlasDataset, embed
import json

# Load prerequisite tree from our explorer
with open('knowledge_tree_cosmology.json') as f:
    tree = json.load(f)

# Extract all concepts from the tree
def extract_concepts(node, concepts=None):
    if concepts is None:
        concepts = []
    concepts.append({
        "name": node['concept'],
        "depth": node['depth'],
        "is_foundation": node['is_foundation']
    })
    for prereq in node['prerequisites']:
        extract_concepts(prereq, concepts)
    return concepts

all_concepts = extract_concepts(tree)

# Embed them
concept_names = [c['name'] for c in all_concepts]
embeddings = embed.text(
    texts=concept_names,
    model='nomic-embed-text-v1.5',
    task_type='clustering'
)

# Create Atlas dataset
dataset = AtlasDataset('cosmology-prerequisite-tree')
dataset.add_data(
    embeddings=embeddings['embeddings'],
    data=all_concepts
)

# Generate map colored by depth
map_obj = dataset.create_index(
    name="Cosmology Learning Path",
    colorable_fields=["depth", "is_foundation"],
    id_field="name"
)

print(f"View your cosmology knowledge tree: {map_obj.map_link}")
# This creates an INTERACTIVE web visualization!
```

---

## Research Questions

Before full implementation, we should investigate:

1. **Embedding Quality**: Do semantic embeddings accurately capture prerequisite relationships?
   - Test: Does "general relativity" cluster near "special relativity"?
   - Metric: Precision@k for prerequisite prediction

2. **Topic Hierarchy Alignment**: Does Atlas's automatic topic modeling match human curriculum design?
   - Test: Compare Atlas topics to university course sequences
   - Metric: Agreement with expert-curated learning paths

3. **Scalability**: Can we embed all of mathematics/physics/CS?
   - Test: Performance with 10K+ concepts
   - Metric: Search speed, storage costs

4. **Claude Integration**: What's the optimal hybrid strategy?
   - Test: Atlas-only vs. Claude-only vs. hybrid
   - Metric: Speed, accuracy, cost

---

## Cost Considerations

### Nomic Atlas Pricing
- **Free Tier**: 50,000 embeddings/month, 5 maps
- **Pro Tier**: $20/month - 500,000 embeddings, unlimited maps
- **Enterprise**: Custom pricing

### Cost Comparison

**Current (Claude-only)**:
- Prerequisite discovery: ~10 API calls per concept tree
- Cost: ~$0.05 per concept (assuming 4-level tree)
- For 1000 concepts: ~$50

**With Atlas**:
- Initial embedding: 1000 concepts × $0.0001 = $0.10
- Prerequisite lookup: Free (cached)
- Claude validation: ~2 calls per concept = $0.01 per concept
- For 1000 concepts: ~$10.10

**Savings**: 80% reduction in API costs

---

## Next Steps

### Immediate Actions (This Week)

1. **Create Nomic account** and get API key
2. **Run proof-of-concept** with 50 core concepts
3. **Share interactive map** in project README
4. **Gather feedback** from community

### Short Term (1 Month)

1. **Build integration** with PrerequisiteExplorer
2. **Embed 200+ concepts** across physics/math/CS
3. **Validate** against expert curriculum design
4. **Document API** usage patterns

### Long Term (3-6 Months)

1. **Public knowledge graph** with 1000+ concepts
2. **Community contributions** (user-submitted concepts)
3. **Learning path export** (to Obsidian, Anki, etc.)
4. **Research paper** on semantic prerequisite discovery

---

## Resources

- **Nomic Atlas Docs**: https://docs.nomic.ai/
- **Python SDK**: https://github.com/nomic-ai/nomic
- **API Reference**: https://docs.nomic.ai/reference/python-api/
- **Embeddings Guide**: https://docs.nomic.ai/atlas/capabilities/embeddings
- **Topic Modeling**: https://docs.nomic.ai/atlas/capabilities/topics
- **Vector Search**: https://docs.nomic.ai/atlas/data-maps/guides/vector-search-over-your-data

---

## Questions?

See [ROADMAP.md](../ROADMAP.md) for how this fits into overall development plan.

**Last Updated**: 2025-10-04
**Status**: Research & Planning
**Owner**: @HarleyCoops
