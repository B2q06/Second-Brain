---
type: meta
title: Master Tag Taxonomy
version: 1.0
last_updated: 2025-11-07
auto_update: true
---

# Tag Taxonomy

> **Purpose**: Controlled vocabulary for consistent AI tagging
> **Rules**:
> - AI must use existing tags when confidence > 0.85
> - New tags require 3+ potential uses
> - Propose new tags in [[Tag Review Queue]]

---

## HIERARCHICAL STRUCTURE

Tags use `/` separator for hierarchy:
- `category/subcategory/specific`
- Example: `tech/programming/python`

---

## PRIMARY CATEGORIES

### 1. TECH (Technology & Tools)
**Subcategories:**
- `tech/programming` - Languages, frameworks, coding
- `tech/infrastructure` - DevOps, servers, deployment
- `tech/databases` - SQL, NoSQL, data storage
- `tech/tools` - CLIs, editors, utilities
- `tech/cloud` - AWS, Azure, GCP, serverless

### 2. LEARNING (Education & Skill Development)
**Subcategories:**
- `learning/course` - Formal courses, tutorials
- `learning/book` - Technical books
- `learning/practice` - Hands-on learning
- `learning/research` - Exploring new topics

### 3. PROJECT (Project-Related)
**Subcategories:**
- `project/planning` - Design, architecture planning
- `project/development` - Active coding
- `project/debugging` - Troubleshooting, fixing bugs
- `project/deployment` - Shipping, hosting, CI/CD
- `project/maintenance` - Updates, refactoring

### 4. DOMAIN (Field/Industry)
**Subcategories:**
- `domain/web` - Web development
- `domain/mobile` - Mobile apps
- `domain/data` - Data science, ML, analytics
- `domain/systems` - Systems programming, OS
- `domain/security` - InfoSec, pentesting

### 5. SKILL (Skill Areas)
**Subcategories:**
- `skill/backend` - Server-side development
- `skill/frontend` - Client-side development
- `skill/fullstack` - Both ends
- `skill/devops` - Operations, deployment
- `skill/testing` - QA, test automation

---

## SPECIFIC TAGS (Flat Tags)=

### Programming Languages
```yaml
python:
  aliases: [py, python3]
  category: tech/programming
  description: Python programming language

javascript:
  aliases: [js, node, nodejs]
  category: tech/programming
  description: JavaScript/Node.js

typescript:
  aliases: [ts]
  category: tech/programming
  description: TypeScript language

rust:
  aliases: [rs]
  category: tech/programming
  description: Rust language

go:
  aliases: [golang]
  category: tech/programming
  description: Go language

java:
  aliases: []
  category: tech/programming
  description: Java language

csharp:
  aliases: [c#, dotnet]
  category: tech/programming
  description: C# and .NET

cpp:
  aliases: [c++, cplusplus]
  category: tech/programming
  description: C++ language

c:
  aliases: []
  category: tech/programming
  description: C language

bash:
  aliases: [shell, sh]
  category: tech/programming
  description: Bash scripting
```

### Frameworks & Libraries
```yaml
fastapi:
  aliases: [fast-api]
  category: tech/programming
  parent: python
  description: FastAPI Python web framework

react:
  aliases: [reactjs]
  category: tech/programming
  parent: javascript
  description: React library

django:
  aliases: []
  category: tech/programming
  parent: python
  description: Django web framework

nextjs:
  aliases: [next, next.js]
  category: tech/programming
  parent: [javascript, react]
  description: Next.js React framework

flask:
  aliases: []
  category: tech/programming
  parent: python
  description: Flask web framework

express:
  aliases: [expressjs]
  category: tech/programming
  parent: javascript
  description: Express.js framework

vue:
  aliases: [vuejs]
  category: tech/programming
  parent: javascript
  description: Vue.js framework

angular:
  aliases: []
  category: tech/programming
  parent: javascript
  description: Angular framework

svelte:
  aliases: []
  category: tech/programming
  parent: javascript
  description: Svelte framework

pytorch:
  aliases: []
  category: tech/programming
  parent: python
  description: PyTorch ML framework

tensorflow:
  aliases: [tf]
  category: tech/programming
  parent: python
  description: TensorFlow ML framework
```

### Infrastructure & Tools
```yaml
docker:
  aliases: [containers]
  category: tech/infrastructure
  description: Docker containerization

kubernetes:
  aliases: [k8s]
  category: tech/infrastructure
  description: Kubernetes orchestration

git:
  aliases: [github, gitlab, gitea]
  category: tech/tools
  description: Version control

nginx:
  aliases: []
  category: tech/infrastructure
  description: Nginx web server

apache:
  aliases: []
  category: tech/infrastructure
  description: Apache web server

terraform:
  aliases: []
  category: tech/infrastructure
  description: Terraform IaC

ansible:
  aliases: []
  category: tech/infrastructure
  description: Ansible automation

ci-cd:
  aliases: [cicd, ci/cd, continuous-integration]
  category: tech/infrastructure
  description: CI/CD pipelines

linux:
  aliases: [unix]
  category: tech/tools
  description: Linux operating system

windows:
  aliases: []
  category: tech/tools
  description: Windows operating system

macos:
  aliases: [mac, osx]
  category: tech/tools
  description: macOS operating system
```

### Databases
```yaml
postgres:
  aliases: [postgresql, psql]
  category: tech/databases
  description: PostgreSQL database

mysql:
  aliases: []
  category: tech/databases
  description: MySQL database

mongodb:
  aliases: [mongo]
  category: tech/databases
  description: MongoDB NoSQL database

redis:
  aliases: []
  category: tech/databases
  description: Redis in-memory store

sqlite:
  aliases: []
  category: tech/databases
  description: SQLite embedded database

neo4j:
  aliases: []
  category: tech/databases
  description: Neo4j graph database

elasticsearch:
  aliases: [elastic]
  category: tech/databases
  description: Elasticsearch search engine

dynamodb:
  aliases: []
  category: tech/databases
  description: AWS DynamoDB
```

### Cloud Providers
```yaml
aws:
  aliases: [amazon-web-services]
  category: tech/cloud
  description: Amazon Web Services

azure:
  aliases: [microsoft-azure]
  category: tech/cloud
  description: Microsoft Azure

gcp:
  aliases: [google-cloud, google-cloud-platform]
  category: tech/cloud
  description: Google Cloud Platform

digitalocean:
  aliases: [do]
  category: tech/cloud
  description: DigitalOcean

vercel:
  aliases: []
  category: tech/cloud
  description: Vercel hosting

netlify:
  aliases: []
  category: tech/cloud
  description: Netlify hosting

heroku:
  aliases: []
  category: tech/cloud
  description: Heroku platform
```

### Development Phases
```yaml
debugging:
  category: project/debugging
  description: Troubleshooting issues

testing:
  category: project/development
  description: Writing tests

refactoring:
  category: project/maintenance
  description: Code improvement

architecture:
  category: project/planning
  description: System design

optimization:
  category: project/maintenance
  description: Performance tuning

documentation:
  category: project/maintenance
  description: Writing docs

code-review:
  category: project/development
  description: Reviewing code
```

### Development Concepts
```yaml
api:
  aliases: [rest-api, rest, restful]
  category: domain/web
  description: API development

authentication:
  aliases: [auth]
  category: domain/security
  description: Authentication systems

authorization:
  aliases: []
  category: domain/security
  description: Authorization/permissions

database-design:
  aliases: [data-modeling]
  category: tech/databases
  description: Database schema design

async:
  aliases: [asynchronous, async-await]
  category: tech/programming
  description: Asynchronous programming

microservices:
  aliases: []
  category: project/planning
  description: Microservices architecture

monolith:
  aliases: [monolithic]
  category: project/planning
  description: Monolithic architecture

serverless:
  aliases: []
  category: tech/cloud
  description: Serverless computing

websockets:
  aliases: []
  category: domain/web
  description: WebSocket connections

graphql:
  aliases: []
  category: domain/web
  description: GraphQL API

grpc:
  aliases: []
  category: domain/web
  description: gRPC protocol
```

---

## CANONICAL FORMS (For Entity Resolution)

**Purpose**: When AI encounters variations, resolve to canonical form

| Variations | Canonical | Entity Type |
|------------|-----------|-------------|
| fast-api, fast_api, FastApi | fastapi | framework |
| node, nodejs, node.js | javascript | language |
| k8s, kubernetes | kubernetes | infrastructure |
| gpt, chatgpt, openai | openai | service |
| typescript, ts | typescript | language |
| postgres, postgresql, psql | postgres | database |
| mongo, mongodb | mongodb | database |
| react, reactjs, react.js | react | framework |
| vue, vuejs, vue.js | vue | framework |
| tf, tensorflow | tensorflow | framework |
| py, python3 | python | language |
| js, javascript | javascript | language |
| c#, csharp, dotnet | csharp | language |
| c++, cpp | cpp | language |
| aws, amazon-web-services | aws | cloud |
| gcp, google-cloud, google-cloud-platform | gcp | cloud |
| ci-cd, cicd, ci/cd | ci-cd | infrastructure |

---

## TAG GROWTH RULES

### Adding New Tags
1. **Threshold**: 3+ items would use this tag
2. **Check aliases**: Is this just another name for existing tag?
3. **Check hierarchy**: Does it fit in existing categories?
4. **Propose in**: [[Tag Review Queue]]

### AI Tagging Algorithm
```
For each entity in conversation:
  1. Check exact match in taxonomy
  2. Check aliases
  3. Calculate semantic similarity with existing tags
  4. If similarity > 0.85: Use existing tag
  5. If similarity 0.60-0.85: Flag for human review
  6. If similarity < 0.60: Propose new tag
```

### Semantic Similarity Examples
- "FastAPI framework" → fastapi (exact match)
- "fast-api" → fastapi (alias match)
- "async patterns in Python" → python + async (multi-tag)
- "kubernetes cluster setup" → kubernetes + infrastructure (category + specific)

---

## TAG MAINTENANCE

### Monthly Review Tasks
- [ ] Identify duplicate/similar tags
- [ ] Merge low-usage tags (< 3 items)
- [ ] Update aliases based on AI proposals
- [ ] Check for orphaned tags (no items using)
- [ ] Update canonical forms

### Automated Checks
- Generate tag frequency report
- Find semantic clusters (similar tags)
- List proposed tags awaiting review

---

## USAGE EXAMPLES

### Example 1: Web Development Conversation
**Conversation about**: Building a FastAPI REST API with PostgreSQL

**AI Tagging Process**:
1. Detect entities: "FastAPI", "REST API", "PostgreSQL"
2. Resolve: fastapi (exact), api (concept), postgres (canonical)
3. Infer categories: tech/programming, domain/web, skill/backend
4. Final tags: `[python, fastapi, api, postgres, backend, web]`

### Example 2: Learning New Skill
**Conversation about**: First time using Docker for containerization

**AI Tagging Process**:
1. Detect: "Docker", "containerization", "learning"
2. Resolve: docker (exact), containers (alias → docker)
3. Content type: learning/practice
4. Final tags: `[docker, infrastructure, learning]`

### Example 3: Debugging Session
**Conversation about**: Troubleshooting async/await issues in JavaScript

**AI Tagging Process**:
1. Detect: "async/await", "JavaScript", "troubleshooting"
2. Resolve: async (canonical), javascript (exact), debugging (phase)
3. Final tags: `[javascript, async, debugging, troubleshooting]`

---

## CUSTOMIZATION GUIDE

### Adding Your Tech Stack
Replace or add to the "Specific Tags" section based on what YOU actually use:

**If you work with:**
- **Mobile**: Add Swift, Kotlin, React Native, Flutter
- **Data Science**: Add Pandas, NumPy, Jupyter, Scikit-learn
- **Game Dev**: Add Unity, Unreal, Godot
- **Embedded**: Add Arduino, Raspberry Pi, C, Assembly

**Example custom additions**:
```yaml
flutter:
  aliases: []
  category: tech/programming
  parent: [mobile, dart]
  description: Flutter mobile framework

pandas:
  aliases: []
  category: tech/programming
  parent: python
  description: Pandas data analysis
```

### Growing Your Taxonomy Organically
1. **Start minimal** - Use the core tags above
2. **Track proposals** - Let AI suggest new tags via Tag Review Queue
3. **Review monthly** - Approve/merge/reject proposed tags
4. **Keep it lean** - Resist tag explosion, prefer existing tags
5. **Update aliases** - Add variations as you encounter them

---

## NOTES FOR AI AGENTS

When processing conversations:
1. **Load this taxonomy first** before tagging
2. **Check canonical forms** for entity resolution
3. **Use aliases** to match variations
4. **Calculate semantic similarity** for uncertain matches
5. **Propose to Tag Review Queue** when confidence < 0.60
6. **Apply hierarchical tags** (category + specific)
7. **Prefer existing tags** over creating new ones
8. **Link to Graphiti entities** for cross-referencing

Remember: **Consistency > Completeness**. Better to use fewer tags consistently than many tags inconsistently.

---

## BATCH PROCESSING GUIDANCE

### When Processing Large Data Dumps

**Batch mode** is triggered when:
- 5+ files are processed at once, OR
- Single file > 100,000 characters, OR
- Total batch > 500,000 characters

### Modified Tagging Strategy for Batches

**Standard Process** (single file):
1. Extract entities from conversation
2. Assign tags immediately
3. Match to existing areas
4. Process next file

**Batch Process** (5+ files):
1. **Extract entities from ALL files first**
2. **Assign tags to all files**
3. **THEN analyze all tags together** to discover areas
4. Match files to discovered areas
5. Process normally

**Why batch differently?**
- Better area discovery (sees full picture)
- More accurate tag clustering
- Prevents fragmenting related knowledge across multiple areas

### Tag Frequency Analysis (Batch Mode)

**In batch mode, track tag frequency**:
```
python: 45 occurrences
fastapi: 23 occurrences
neo4j: 18 occurrences
authentication: 15 occurrences
...
```

**Use frequency for**:
- Identifying major themes (high-frequency tags)
- Discovering new areas (clusters of related tags)
- Prioritizing which tags get specialized sub-areas

### Example Batch Processing

**Scenario**: 50 conversation files imported from ChatGPT history

**Step 1**: Tag all 50 files
```
File 1: [python, web-dev, fastapi]
File 2: [python, data-science, pandas]
File 3: [javascript, react, frontend]
...
File 50: [python, automation, scripting]
```

**Step 2**: Analyze tag distribution
```
python: 38/50 files (76%)
javascript: 12/50 files (24%)
web-dev: 20/50 files (40%)
data-science: 10/50 files (20%)
...
```

**Step 3**: Discover area clusters
```
Cluster 1: [python, web-dev, fastapi, django, backend]
  → Suggests area: "Technology > Programming > Python > Web Development"

Cluster 2: [python, data-science, pandas, numpy, ml]
  → Suggests area: "Technology > Data Science > Python Tools"

Cluster 3: [javascript, react, frontend, components, ui]
  → Suggests area: "Technology > Programming > Web Development > Frontend"
```

**Step 4**: Create areas (with human approval)
- Propose 3 new areas to new-areas-queue.md
- Wait for approval
- Assign files to approved areas

### Benefits of Batch Processing

✅ **More accurate** area discovery
✅ **Prevents duplication** (sees all related content at once)
✅ **Better clustering** (statistical significance with more data)
✅ **Faster** (batch operations more efficient than sequential)
✅ **Holistic view** (understands relationships between topics)

### Single File Processing

**Use when**:
- 1-4 files at a time
- Regular conversation captures
- Ongoing knowledge capture

**Simpler workflow**:
1. Tag file
2. Match to existing areas
3. Done

**No global analysis needed** for small batches.

---

## NOTES FOR BATCH IMPORTS

### Preparing Large Dumps

**Before importing 100s of conversations**:

1. **Clean the data** (remove duplicates, fix formatting)
2. **Split if needed** (if >1000 files, process in chunks of 200-300)
3. **Backup** current taxonomy (in case you need to revert)
4. **Expect new areas** (large dumps often reveal new knowledge areas)

### Post-Batch Review

**After processing a large batch**:

1. **Review new areas queue** (likely 5-15 new areas proposed)
2. **Check tag frequency** (identify most common tags)
3. **Refine taxonomy** (merge similar tags, update aliases)
4. **Validate areas** (ensure new areas make sense)
5. **Run brain space calculation** (recalculate with new data)

### Incremental Batches

**For ongoing imports** (e.g., weekly ChatGPT exports):

- Smaller batches (10-50 files) process quickly
- Area discovery more incremental
- Less disruptive to existing taxonomy
- Easier to review and approve changes

**Recommended approach**: Import in weekly/monthly batches rather than one massive dump.
