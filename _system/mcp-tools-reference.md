---
type: reference
title: MCP Tools Reference for Processing Pipeline Agent
version: 1.0
created: 2025-11-09
---

# MCP Tools Reference

Complete reference of all MCP tools available to the processing-pipeline-agent for Neo4j graph operations and Smart Connections semantic search.

---

## Neo4j MCP Tools

### `mcp__neo4j__create_entities`

**Purpose**: Create new entity nodes in the Neo4j knowledge graph

**Parameters**:
```json
{
  "entities": [
    {
      "name": "string (required) - Unique entity name",
      "type": "string (required) - Entity type: technology, skill, project, concept, person",
      "observations": ["array of strings - Facts about this entity"]
    }
  ]
}
```

**Returns**:
```json
{
  "result": [
    {"name": "EntityName", "type": "technology", "observations": ["fact1", "fact2"]}
  ]
}
```

**Example**:
```javascript
mcp__neo4j__create_entities({
  entities: [
    {
      name: "FastAPI",
      type: "technology",
      observations: [
        "Python web framework",
        "Async support",
        "Auto-generated API docs"
      ]
    },
    {
      name: "PostgreSQL",
      type: "technology",
      observations: [
        "Relational database",
        "ACID compliant",
        "Advanced query capabilities"
      ]
    }
  ]
})
```

**When to Use**: Stage 1 (Entity Extraction) - After extracting entities from conversation

**Error Handling**: If entity already exists, observations are merged (not duplicated)

---

### `mcp__neo4j__create_relations`

**Purpose**: Create relationships between existing entities in the graph

**Parameters**:
```json
{
  "relations": [
    {
      "source": "string (required) - Source entity name (must exist)",
      "target": "string (required) - Target entity name (must exist)",
      "relationType": "string (required) - Relationship type (uppercase, e.g., USES, BUILT_WITH)"
    }
  ]
}
```

**Returns**:
```json
{
  "result": [
    {"source": "FastAPI", "target": "Python", "relationType": "BUILT_WITH"}
  ]
}
```

**Example**:
```javascript
mcp__neo4j__create_relations({
  relations: [
    {source: "FastAPI", target: "Python", relationType: "BUILT_WITH"},
    {source: "FastAPI", target: "PostgreSQL", relationType: "INTEGRATES_WITH"},
    {source: "FastAPI", target: "Authentication", relationType: "IMPLEMENTS"}
  ]
})
```

**When to Use**:
- Stage 1 (Entity Extraction) - After creating entities, create relationships between them
- Stage 7 (Node Updates) - Link conversation to entities

**Error Handling**: If source or target doesn't exist, relationship creation fails

**Common Relationship Types**:
- `BUILT_WITH` - Technology built with another
- `USES` - Technology uses another
- `INTEGRATES_WITH` - Technologies that integrate
- `IMPLEMENTS` - Implements a concept/pattern
- `DISCUSSES` - Conversation discusses entity
- `RELATED_TO` - General relationship

---

### `mcp__neo4j__read_graph`

**Purpose**: Read the entire knowledge graph (entities + relationships)

**Parameters**: None

**Returns**:
```json
{
  "entities": [
    {"name": "Entity1", "type": "technology", "observations": ["fact1"]},
    {"name": "Entity2", "type": "skill", "observations": ["fact2"]}
  ],
  "relations": [
    {"source": "Entity1", "target": "Entity2", "relationType": "USES"}
  ]
}
```

**Example**:
```javascript
mcp__neo4j__read_graph()
```

**When to Use**:
- Verify entities were created successfully
- Debug graph state
- Count total entities before/after processing

**Note**: Returns ALL entities and relationships. For large graphs, use search instead.

---

### `mcp__neo4j__search_memories`

**Purpose**: Semantic search for similar entities in the graph

**Parameters**:
```json
{
  "query": "string (required) - Natural language search query",
  "limit": "integer (optional, default: 10) - Max results"
}
```

**Returns**:
```json
{
  "entities": [
    {
      "name": "SimilarEntity",
      "type": "technology",
      "observations": ["fact1"],
      "similarity": 0.85
    }
  ],
  "relations": []
}
```

**Example**:
```javascript
// Search for similar technologies
mcp__neo4j__search_memories({
  query: "python web framework",
  limit: 5
})

// Result might include: FastAPI, Django, Flask
```

**When to Use**:
- **Stage 2 (Tag Assignment)** - CRITICAL for finding similar existing entities
- Check if entity already exists before creating
- Find similarity scores for tag matching

**Similarity Thresholds**:
- `>= 0.85`: Use existing tag (high confidence match)
- `0.60-0.85`: Ask user for confirmation
- `< 0.60`: Propose as new tag

---

### `mcp__neo4j__find_memories_by_name`

**Purpose**: Find specific entities by exact name match

**Parameters**:
```json
{
  "names": ["array of entity names to find"]
}
```

**Returns**:
```json
{
  "entities": [
    {"name": "FastAPI", "type": "technology", "observations": ["fact1", "fact2"]}
  ],
  "relations": []
}
```

**Example**:
```javascript
mcp__neo4j__find_memories_by_name({
  names: ["FastAPI", "PostgreSQL", "Docker"]
})
```

**When to Use**:
- Verify specific entities exist
- Get full details about known entities
- Check observations on existing entities

---

### `mcp__neo4j__add_observations`

**Purpose**: Add new facts/observations to existing entities

**Parameters**:
```json
{
  "observations": [
    {
      "entityName": "string (required) - Entity to update",
      "observations": ["array of new facts to add"]
    }
  ]
}
```

**Returns**:
```json
{
  "result": ["Details about added observations"]
}
```

**Example**:
```javascript
mcp__neo4j__add_observations({
  observations: [
    {
      entityName: "FastAPI",
      observations: [
        "Used in production at large scale",
        "Supports WebSockets"
      ]
    }
  ]
})
```

**When to Use**:
- Stage 7 (Node Updates) - Add new information to existing entities
- Update entities with conversation-specific context

---

### `mcp__neo4j__delete_entities`

**Purpose**: Delete entities and all their relationships

**Parameters**:
```json
{
  "entityNames": ["array of entity names to delete"]
}
```

**Returns**:
```json
{
  "result": "Success confirmation message"
}
```

**Example**:
```javascript
mcp__neo4j__delete_entities({
  entityNames: ["ObsoleteEntity", "DuplicateEntity"]
})
```

**When to Use**:
- Cleanup duplicate entities
- Remove incorrectly extracted entities
- **Rarely used** - deletion should be manual

---

### `mcp__neo4j__delete_observations`

**Purpose**: Delete specific observations from entities

**Parameters**:
```json
{
  "deletions": [
    {
      "entityName": "string",
      "observations": ["array of exact observation strings to delete"]
    }
  ]
}
```

**When to Use**: Remove incorrect facts, rarely needed

---

### `mcp__neo4j__delete_relations`

**Purpose**: Delete specific relationships between entities

**Parameters**:
```json
{
  "relations": [
    {
      "source": "EntityA",
      "target": "EntityB",
      "relationType": "RELATIONSHIP_TYPE"
    }
  ]
}
```

**When to Use**: Remove incorrect relationships, rarely needed

---

## Smart Connections MCP Tools

### `mcp__smart-connections__semantic_search`

**Purpose**: Search Obsidian vault using semantic similarity (not keyword matching)

**Parameters**:
```json
{
  "query": "string (required) - Natural language query",
  "limit": "integer (optional, default: 10) - Max results",
  "min_similarity": "float (optional, default: 0.3) - Min similarity threshold (0-1)"
}
```

**Returns**:
```json
{
  "query": "machine learning concepts",
  "results_count": 3,
  "results": [
    {
      "path": "Technology/AI/Machine Learning Basics.md",
      "score": 0.87,
      "text": "Excerpt from the note..."
    }
  ]
}
```

**Example**:
```javascript
// Find notes related to a concept
mcp__smart-connections__semantic_search({
  query: "authentication and security patterns",
  limit: 5,
  min_similarity: 0.6
})
```

**When to Use**:
- **Stage 7 (Node Updates)** - Find related existing notes
- Discover notes to link to new conversation
- Find similar past conversations

**Note**: Only returns results for notes that have been embedded. New notes won't appear until embedding script runs.

---

### `mcp__smart-connections__find_related`

**Purpose**: Find notes related to a specific file (like Smart Connections sidebar)

**Parameters**:
```json
{
  "file_path": "string (required) - Relative path from vault root",
  "limit": "integer (optional, default: 10) - Max results"
}
```

**Returns**:
```json
{
  "results": [
    {
      "path": "Related/Note.md",
      "score": 0.82
    }
  ]
}
```

**Example**:
```javascript
mcp__smart-connections__find_related({
  file_path: "00-Inbox/processed/conversation_20251109_001.md",
  limit: 5
})
```

**When to Use**:
- Find notes similar to newly created conversation
- Suggest backlinks
- Discover related conversations

---

### `mcp__smart-connections__get_context_blocks`

**Purpose**: Get most relevant text blocks for a query (for RAG/context building)

**Parameters**:
```json
{
  "query": "string (required) - Query to find context for",
  "max_blocks": "integer (optional, default: 5) - Max blocks to return"
}
```

**Returns**:
```json
{
  "blocks": [
    {
      "path": "Note.md",
      "text": "Relevant text block...",
      "score": 0.89
    }
  ]
}
```

**Example**:
```javascript
mcp__smart-connections__get_context_blocks({
  query: "how to implement JWT authentication",
  max_blocks: 3
})
```

**When to Use**:
- Get specific text excerpts for context
- Build knowledge base for answering questions
- Extract relevant information from vault

---

## Usage in Processing Pipeline

### Stage 1: Entity Extraction
```javascript
// 1. Extract entities from conversation
entities = extract_entities_from_conversation(conversation)

// 2. Create entities in Neo4j
mcp__neo4j__create_entities({entities: entities})

// 3. Create relationships
relationships = determine_relationships(entities)
mcp__neo4j__create_relations({relations: relationships})

// 4. Verify creation
graph = mcp__neo4j__read_graph()
console.log(`Entities in graph: ${graph.entities.length}`)
```

### Stage 2: Tag Assignment
```javascript
// For each extracted entity
for (entity of entities) {
  // Search for similar existing entities
  similar = mcp__neo4j__search_memories({
    query: entity.name,
    limit: 5
  })

  if (similar.entities.length > 0 && similar.entities[0].similarity > 0.85) {
    // Use existing tag
    tag = similar.entities[0].name
  } else if (similar.entities.length > 0 && similar.entities[0].similarity > 0.60) {
    // Ask user for confirmation
    approved_tag = ask_user_for_approval(entity.name, similar.entities)
  } else {
    // New tag - definitely needs approval
    approved_tag = ask_user_to_approve_new_tag(entity.name)
  }
}
```

### Stage 7: Node Updates
```javascript
// Link conversation to entities
conversation_entity = {
  name: conversation_id,
  type: "conversation",
  observations: [summary, date, duration]
}

mcp__neo4j__create_entities({entities: [conversation_entity]})

// Create relationships
for (entity of extracted_entities) {
  mcp__neo4j__create_relations({
    relations: [{
      source: conversation_id,
      target: entity.name,
      relationType: "DISCUSSES"
    }]
  })
}

// Find related notes
related = mcp__smart-connections__semantic_search({
  query: conversation_summary,
  limit: 5,
  min_similarity: 0.7
})

// Add backlinks to related notes (optional)
for (note of related.results) {
  if (note.score > 0.75) {
    add_backlink_to_note(note.path, conversation_id)
  }
}
```

---

## Error Handling Best Practices

### Always wrap MCP calls in try-catch:
```javascript
try {
  result = mcp__neo4j__create_entities({entities: entities})
  console.log(`✓ Created ${result.result.length} entities`)
} catch (error) {
  console.error(`✗ Neo4j error: ${error}`)
  // Fallback: Document entities in note instead
  document_entities_in_note(entities)
}
```

### Verify operations completed:
```javascript
// After creating entities, verify they exist
mcp__neo4j__create_entities({entities: [...]})

// Verify
graph = mcp__neo4j__read_graph()
if (graph.entities.length >= expected_count) {
  console.log("✓ Entities verified")
} else {
  console.error("✗ Entity creation may have failed")
}
```

### Handle empty results gracefully:
```javascript
similar = mcp__neo4j__search_memories({query: "unknown term"})

if (similar.entities.length === 0) {
  // No similar entities - definitely a new tag
  propose_new_tag(entity_name)
} else {
  // Check similarity of best match
  best_match = similar.entities[0]
  if (best_match.similarity > 0.85) {
    use_existing_tag(best_match.name)
  }
}
```

---

## Testing MCP Tools

### Test Neo4j Connection:
```javascript
// Simple test
graph = mcp__neo4j__read_graph()
console.log(`Graph has ${graph.entities.length} entities`)
```

### Test Entity Creation:
```javascript
// Create test entity
mcp__neo4j__create_entities({
  entities: [{
    name: "TestEntity",
    type: "test",
    observations: ["This is a test"]
  }]
})

// Verify
test = mcp__neo4j__find_memories_by_name({names: ["TestEntity"]})
console.log(test.entities.length > 0 ? "✓ Test passed" : "✗ Test failed")

// Cleanup
mcp__neo4j__delete_entities({entityNames: ["TestEntity"]})
```

### Test Smart Connections:
```javascript
// Search for known note
results = mcp__smart-connections__semantic_search({
  query: "second brain system",
  limit: 3
})

console.log(`Found ${results.results_count} related notes`)
```

---

## Performance Tips

1. **Batch entity creation**: Create all entities in one call, not individually
2. **Batch relationship creation**: Create all relationships together
3. **Cache search results**: Don't search for same entity multiple times
4. **Limit search results**: Use appropriate `limit` values (5-10 usually enough)
5. **Use exact name lookup when possible**: `find_memories_by_name` is faster than `search_memories`

---

**Version**: 1.0
**Last Updated**: 2025-11-09
**For**: processing-pipeline-agent
