# Knowledge Graph Visualization Designs

**Date**: 2025-11-11
**Status**: Concept Phase
**Purpose**: Design interactive visualizations for Second Brain system

---

## 1. Brain Space Dashboard

### Concept
A single-page HTML dashboard showing knowledge distribution, growth trends, and hub concepts.

### Layout
```
┌────────────────────────────────────────────────────────┐
│  🧠 Second Brain Dashboard - November 2025            │
├────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Total Time  │  │  Entities   │  │    Areas    │  │
│  │  187 hours  │  │     342     │  │      12     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
├────────────────────────────────────────────────────────┤
│  Time Distribution by Area (Treemap)                  │
│  ┌──────────────────────────────────────────────────┐ │
│  │ ┌───────────┬───────────┬──────────────────────┐ │ │
│  │ │Technology │  History  │       Language       │ │ │
│  │ │  120h     │   45h     │         22h          │ │ │
│  │ │           ├───────────┴──────────────────────┤ │ │
│  │ │           │       Other Areas (8h)           │ │ │
│  │ └───────────┴──────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────┤
│  Growth Trends (Line Chart)                           │
│  Entity Count Over Time                                │
│  400│                                              ●   │
│  300│                                         ●    │   │
│  200│                                ●    ●       │   │
│  100│                       ●    ●               │   │
│    0└──────┬──────┬──────┬──────┬──────┬──────┘   │
│       Nov 1   Nov 8  Nov 15 Nov 22 Nov 30          │
├────────────────────────────────────────────────────────┤
│  Hub Entities (Most Connected)                        │
│  ┌────────────────┬──────────────┬─────────────┐    │
│  │ FastAPI        │ 23 links     │ Technology  │    │
│  │ Neo4j          │ 18 links     │ Technology  │    │
│  │ Python         │ 45 links     │ Technology  │    │
│  │ Chinese Gr...  │ 12 links     │ Language    │    │
│  │ Bronze Age     │ 8 links      │ History     │    │
│  └────────────────┴──────────────┴─────────────┘    │
└────────────────────────────────────────────────────────┘
```

### Technologies

**Option A: D3.js (Static HTML)**
```html
<!-- brain-space-dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Brain Space Dashboard</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #1e1e1e; color: #d4d4d4; }
        .metric-card { background: #2d2d2d; padding: 20px; border-radius: 8px; }
        .treemap rect { stroke: #fff; stroke-width: 1px; }
    </style>
</head>
<body>
    <div id="dashboard">
        <h1>🧠 Second Brain Dashboard</h1>
        <div id="metrics"></div>
        <div id="treemap"></div>
        <div id="trends"></div>
        <div id="hubs"></div>
    </div>

    <script>
        // Load data from JSON
        d3.json("brain-space-data.json").then(data => {
            renderMetrics(data.metrics);
            renderTreemap(data.time_distribution);
            renderTrends(data.growth_trends);
            renderHubs(data.hub_entities);
        });

        function renderTreemap(data) {
            const width = 800;
            const height = 400;

            const treemap = d3.treemap()
                .size([width, height])
                .paddingInner(2);

            const root = d3.hierarchy({children: data})
                .sum(d => d.time_hours);

            treemap(root);

            const svg = d3.select("#treemap")
                .append("svg")
                .attr("width", width)
                .attr("height", height);

            const cell = svg.selectAll("g")
                .data(root.leaves())
                .join("g")
                .attr("transform", d => `translate(${d.x0},${d.y0})`);

            cell.append("rect")
                .attr("width", d => d.x1 - d.x0)
                .attr("height", d => d.y1 - d.y0)
                .attr("fill", d => d.data.color);

            cell.append("text")
                .attr("x", 5)
                .attr("y", 20)
                .text(d => d.data.name)
                .style("font-size", "14px")
                .style("fill", "#fff");
        }

        // Similar functions for trends and hubs...
    </script>
</body>
</html>
```

**Option B: Obsidian Canvas**
```json
{
  "nodes": [
    {
      "id": "node-fastapi",
      "type": "text",
      "text": "**FastAPI**\n23 connections\n120 hours",
      "x": 100,
      "y": 100,
      "width": 200,
      "height": 100,
      "color": "3"
    },
    {
      "id": "node-neo4j",
      "type": "text",
      "text": "**Neo4j**\n18 connections\n80 hours",
      "x": 400,
      "y": 150,
      "width": 200,
      "height": 100,
      "color": "3"
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "fromNode": "node-fastapi",
      "toNode": "node-neo4j",
      "label": "INTEGRATES_WITH"
    }
  ]
}
```

**Recommendation**: Start with Option B (Obsidian Canvas) for MVP, upgrade to Option A for richer interactivity

---

## 2. Knowledge Graph 3D Viewer

### Concept
Interactive 3D force-directed graph of entities and relationships

### Features
- **Zoom/Pan/Rotate**: Navigate the knowledge space
- **Node Sizing**: Size by connection count
- **Color Coding**: By entity type or area
- **Click to Focus**: Click node to see details
- **Search**: Find specific entities
- **Time Slider**: Scrub through knowledge evolution

### Technologies

**Force-Directed Graph with D3.js**
```javascript
// knowledge-graph-3d.html
const data = {
    nodes: [
        {id: "FastAPI", group: "technology", value: 23},
        {id: "Neo4j", group: "technology", value: 18},
        {id: "Python", group: "language", value: 45},
        {id: "Chinese Grammar", group: "language-concept", value: 12},
        // ... all entities
    ],
    links: [
        {source: "FastAPI", target: "Python", type: "BUILT_WITH"},
        {source: "FastAPI", target: "Neo4j", type: "INTEGRATES_WITH"},
        // ... all relationships
    ]
};

const simulation = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.links).id(d => d.id))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2));

// Color by group
const color = d3.scaleOrdinal()
    .domain(["technology", "language", "history", "culture"])
    .range(["#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]);

const svg = d3.select("#graph")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

const link = svg.append("g")
    .selectAll("line")
    .data(data.links)
    .join("line")
    .attr("stroke", "#999")
    .attr("stroke-width", 1);

const node = svg.append("g")
    .selectAll("circle")
    .data(data.nodes)
    .join("circle")
    .attr("r", d => Math.sqrt(d.value) * 3)
    .attr("fill", d => color(d.group))
    .call(drag(simulation));

// Labels
const label = svg.append("g")
    .selectAll("text")
    .data(data.nodes)
    .join("text")
    .text(d => d.id)
    .attr("font-size", 10)
    .attr("dx", 12)
    .attr("dy", 4);

simulation.on("tick", () => {
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

    label
        .attr("x", d => d.x)
        .attr("y", d => d.y);
});

// Click to focus
node.on("click", (event, d) => {
    showEntityDetails(d);
});

function showEntityDetails(entity) {
    // Display sidebar with:
    // - Entity name and type
    // - All observations
    // - Connected entities
    // - Related conversations
    // - Time spent
}
```

### Alternative: Cytoscape.js
```javascript
// More powerful for large graphs
const cy = cytoscape({
    container: document.getElementById('cy'),
    elements: {
        nodes: neo4jNodes,
        edges: neo4jRelationships
    },
    style: [
        {
            selector: 'node',
            style: {
                'background-color': 'data(color)',
                'label': 'data(name)',
                'width': 'data(size)',
                'height': 'data(size)'
            }
        },
        {
            selector: 'edge',
            style: {
                'width': 2,
                'line-color': '#ccc',
                'target-arrow-color': '#ccc',
                'target-arrow-shape': 'triangle',
                'label': 'data(type)'
            }
        }
    ],
    layout: {
        name: 'cose',  // Force-directed layout
        animate: true
    }
});

// Drill-down on click
cy.on('tap', 'node', function(evt){
    const node = evt.target;
    loadEntityDetails(node.data('id'));
});
```

---

## 3. Tag Hierarchy Tree Viewer

### Concept
Collapsible tree showing full tag taxonomy with statistics

### Layout
```
📁 Technology (185 hours, 234 entities)
├─ 📁 Programming (145 hours, 187 entities)
│  ├─ 📁 Languages (120 hours, 156 entities)
│  │  ├─ 📄 Python (85 hours, 98 entities) ⭐ Hub
│  │  │  ├─ 📁 Frameworks
│  │  │  │  ├─ 📁 Web
│  │  │  │  │  ├─ 📄 FastAPI (45 hours, 23 entities)
│  │  │  │  │  ├─ 📄 Django (15 hours, 12 entities)
│  │  │  │  │  └─ 📄 Flask (8 hours, 8 entities)
│  │  │  │  └─ 📁 ML
│  │  │  │     ├─ 📄 PyTorch (12 hours, 15 entities)
│  │  │  │     └─ 📄 TensorFlow (8 hours, 10 entities)
│  │  ├─ 📄 JavaScript (25 hours, 35 entities)
│  │  │  └─ 📁 Frameworks
│  │  │     ├─ 📄 React (15 hours, 20 entities)
│  │  │     └─ 📄 Vue (5 hours, 8 entities)
│  │  └─ ...
│  └─ 📁 Concepts (25 hours, 31 entities)
│     ├─ 📄 Async Programming (12 hours, 15 entities)
│     └─ ...
├─ 📁 Data (40 hours, 47 entities)
│  └─ 📁 Databases
│     ├─ 📄 Neo4j (25 hours, 28 entities) ⭐ Hub
│     └─ 📄 PostgreSQL (15 hours, 19 entities)
└─ ...

📁 Language (45 hours, 38 entities)
├─ 📁 Chinese (40 hours, 32 entities)
│  ├─ 📁 Grammar (30 hours, 22 entities)
│  │  ├─ 📄 Chinese Grammar (18 hours, 12 entities)
│  │  └─ 📁 Rules
│  │     └─ 📄 Time Expressions (8 hours, 6 entities)
│  └─ 📁 Writing Systems (10 hours, 10 entities)
│     ├─ 📄 Pinyin (6 hours, 6 entities)
│     └─ 📄 Hanzi (4 hours, 4 entities)
└─ ...

📁 History (28 hours, 18 entities)
└─ 📁 Ancient (28 hours, 18 entities)
   └─ 📁 Bronze Age (28 hours, 18 entities)
      └─ 📁 Mesopotamia
         ├─ 📄 Notable Figures
         │  └─ 📄 Ea-nasir (8 hours, 3 entities)
         └─ 📁 Trade
            ├─ 📄 Mesopotamian Trade (12 hours, 8 entities)
            └─ 📁 Organizations
               └─ 📄 Dilmun Trading Guild (5 hours, 4 entities)
```

### Implementation

**Obsidian File Explorer (Native)**
- Just organize tag notes by taxonomy path
- Obsidian shows them as tree
- No custom code needed

**Custom HTML Tree Viewer**
```javascript
// tree-viewer.html
function renderTree(data, parentElement) {
    const ul = document.createElement('ul');

    for (const [key, value] of Object.entries(data)) {
        const li = document.createElement('li');

        if (typeof value === 'object' && !Array.isArray(value)) {
            // Folder
            li.className = 'folder';
            li.innerHTML = `
                <span class="folder-icon">📁</span>
                <span class="folder-name">${key}</span>
                <span class="stats">(${value.time_hours}h, ${value.entity_count} entities)</span>
            `;

            // Recursive for children
            if (value.children) {
                li.appendChild(renderTree(value.children, li));
            }

            // Toggle collapse on click
            li.querySelector('.folder-name').addEventListener('click', () => {
                li.classList.toggle('collapsed');
            });
        } else {
            // File (tag note)
            li.className = 'file';
            li.innerHTML = `
                <span class="file-icon">📄</span>
                <a href="${value.path}">${key}</a>
                <span class="stats">(${value.time_hours}h, ${value.entity_count} entities)</span>
            `;
        }

        ul.appendChild(li);
    }

    parentElement.appendChild(ul);
    return ul;
}

// Load taxonomy data
fetch('_system/taxonomy-tree-data.json')
    .then(r => r.json())
    .then(data => {
        renderTree(data, document.getElementById('tree-root'));
    });
```

---

## 4. Conversation Timeline

### Concept
Chronological view of all conversations with quick navigation

### Layout
```
┌─────────────────────────────────────────────────────┐
│  November 2025                                      │
├─────────────────────────────────────────────────────┤
│  Week of Nov 1                                      │
│  ├─ Nov 1, 15:30 (9 min)                           │
│  │  📝 Chinese Grammar Basics                      │
│  │  Tags: chinese-grammar, pinyin, language        │
│  │                                                   │
│  ├─ Nov 2, 10:00 (45 min)                          │
│  │  🏺 Bronze Age Trade Networks                   │
│  │  Tags: ea-nasir, mesopotamia, copper-trade      │
│  │                                                   │
│  └─ Nov 3, 14:00 (16 min)                          │
│     ⚙️ FastAPI + Neo4j Integration                │
│     Tags: fastapi, neo4j, python, jwt              │
│                                                   │
│  Week of Nov 8                                      │
│  ├─ Nov 8, 18:00 (32 min)                          │
│  │  🔍 Second Brain Setup                          │
│  │  Tags: obsidian, neo4j, mcp, automation         │
│  │                                                   │
│  └─ ...                                             │
└─────────────────────────────────────────────────────┘
```

### Features
- Group by week/month
- Search/filter by tag
- Jump to conversation
- Show duration and entity count
- Color-code by primary domain (Tech=blue, Language=green, History=red)

### Implementation

**Simple Markdown Generator**
```python
# scripts/generate_timeline.py
def generate_timeline(vault_path):
    conversations = glob(vault_path / "00-Inbox" / "processed" / "*.md")

    timeline = {}
    for conv_path in conversations:
        metadata = extract_frontmatter(conv_path)
        date = metadata['created']
        week = get_week_of(date)

        if week not in timeline:
            timeline[week] = []

        timeline[week].append({
            'title': metadata['title'],
            'date': date,
            'duration': metadata['metrics']['duration_minutes'],
            'tags': metadata['tags'],
            'file': conv_path.name
        })

    # Generate markdown
    md = "# Conversation Timeline\n\n"
    for week, convs in sorted(timeline.items(), reverse=True):
        md += f"## Week of {week}\n\n"
        for conv in convs:
            md += f"- **{conv['date']}** ({conv['duration']}min) - [[{conv['file']}|{conv['title']}]]\n"
            md += f"  Tags: {', '.join(conv['tags'])}\n\n"

    with open(vault_path / "conversation-timeline.md", "w") as f:
        f.write(md)
```

---

## 5. Semantic Similarity Network

### Concept
Visualize semantic connections between notes (beyond explicit relationships)

### How It Works
1. Get embeddings for all tag notes from Smart Connections
2. Calculate cosine similarity matrix
3. Draw edges for similarity > 0.7 threshold
4. Reveal unexpected connections

### Example Insights
```
Unexpected high similarity (0.82):
  "FastAPI" ←→ "Chinese Time Expressions"

Why? Both involve:
- Ordering/sequencing concepts
- Syntax before semantics
- Rule-based structures

This might suggest:
- Programming languages share patterns with natural languages
- Temporal logic is universal
- Syntax-first approaches work across domains
```

### Visualization
```
Network diagram with:
- Nodes: All tag notes
- Edges: Semantic similarity > 0.7
- Colors: By domain (tech/language/history)
- Clusters: Automatically grouped by similarity

User can:
- Click edge to see "Why similar?"
- Filter by similarity threshold
- Hide/show domains
- Export clusters for analysis
```

---

## 6. Implementation Priority

### Phase 1: MVP (Next 2 weeks)
1. **Obsidian Canvas for knowledge graph** (4-6h)
   - Auto-generate .canvas from Neo4j
   - Position nodes by relationship
   - Update monthly

2. **Simple Timeline Markdown** (2-3h)
   - Generate from processed conversations
   - Group by week
   - Regenerate daily

3. **Treemap for time distribution** (3-4h)
   - Static HTML with D3.js
   - Show area time allocation
   - Update weekly

### Phase 2: Enhancements (Month 2)
4. **Interactive knowledge graph** (8-12h)
   - D3.js force-directed
   - Click to drill down
   - Search and filter

5. **Hierarchical tree viewer** (6-8h)
   - Collapsible taxonomy
   - Click to view tag note
   - Show statistics inline

### Phase 3: Advanced (Month 3+)
6. **Semantic similarity network** (12-16h)
   - Embedding calculation
   - Similarity matrix
   - Unexpected connections

7. **Time-series animation** (8-10h)
   - Scrub timeline
   - Watch knowledge grow
   - Identify growth spurts

---

## 7. Data Export Scripts

All visualizations need data extraction:

```python
# scripts/export_brain_space_data.py
def export_dashboard_data():
    """Export all metrics for dashboard"""

    data = {
        "metrics": {
            "total_time_hours": calculate_total_time(),
            "total_entities": count_neo4j_entities(),
            "total_areas": count_areas(),
            "total_conversations": count_conversations()
        },
        "time_distribution": aggregate_time_by_area(),
        "growth_trends": calculate_growth_trends(),
        "hub_entities": find_hub_entities(),
        "recent_activity": get_recent_conversations(limit=10)
    }

    with open("_system/brain-space-data.json", "w") as f:
        json.dump(data, f, indent=2)

# Run daily or on-demand
export_dashboard_data()
```

---

**Status**: Design Complete ✅
**Next**: Implement Phase 1 (Canvas + Timeline + Treemap)
**Estimated Time**: 10-15 hours total
