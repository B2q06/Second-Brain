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
  canonical: "python"
  aliases: [py, python3]
  parent_tags: [programming-languages, programming]
  root: Technology
  category: tech/programming
  depth: 3
  path: "Technology > Programming > Languages > Python"
  description: Python programming language

javascript:
  canonical: "javascript"
  aliases: [js, node, nodejs]
  parent_tags: [programming-languages, programming]
  root: Technology
  category: tech/programming
  depth: 3
  path: "Technology > Programming > Languages > JavaScript"
  description: JavaScript/Node.js

typescript:
  canonical: "typescript"
  aliases: [ts]
  parent_tags: [programming-languages, programming, javascript]
  root: Technology
  category: tech/programming
  depth: 4
  path: "Technology > Programming > Languages > JavaScript > TypeScript"
  description: TypeScript language

rust:
  canonical: "rust"
  aliases: [rs]
  parent_tags: [programming-languages, programming]
  root: Technology
  category: tech/programming
  depth: 3
  path: "Technology > Programming > Languages > Rust"
  description: Rust language

go:
  canonical: "go"
  aliases: [golang]
  parent_tags: [programming-languages, programming]
  root: Technology
  category: tech/programming
  depth: 3
  path: "Technology > Programming > Languages > Go"
  description: Go language

java:
  canonical: "java"
  aliases: []
  parent_tags: [programming-languages, programming]
  root: Technology
  category: tech/programming
  depth: 3
  path: "Technology > Programming > Languages > Java"
  description: Java language

csharp:
  canonical: "csharp"
  aliases: [c#, dotnet]
  parent_tags: [programming-languages, programming]
  root: Technology
  category: tech/programming
  depth: 3
  path: "Technology > Programming > Languages > C#"
  description: C# and .NET

cpp:
  canonical: "cpp"
  aliases: [c++, cplusplus]
  parent_tags: [programming-languages, programming]
  root: Technology
  category: tech/programming
  depth: 3
  path: "Technology > Programming > Languages > C++"
  description: C++ language

c:
  canonical: "c"
  aliases: []
  parent_tags: [programming-languages, programming]
  root: Technology
  category: tech/programming
  depth: 3
  path: "Technology > Programming > Languages > C"
  description: C language

bash:
  canonical: "bash"
  aliases: [shell, sh]
  parent_tags: [programming-languages, scripting, programming]
  root: Technology
  category: tech/programming
  depth: 4
  path: "Technology > Programming > Scripting > Shell > Bash"
  description: Bash scripting
```

### Frameworks & Libraries
```yaml
fastapi:
  canonical: "fastapi"
  aliases: [fast-api]
  parent_tags: [python, web-frameworks, frameworks]
  root: Technology
  category: tech/programming
  depth: 5
  path: "Technology > Programming > Languages > Python > Frameworks > Web > FastAPI"
  description: FastAPI Python web framework

react:
  canonical: "react"
  aliases: [reactjs]
  parent_tags: [javascript, frontend-frameworks, frameworks]
  root: Technology
  category: tech/programming
  depth: 5
  path: "Technology > Programming > Languages > JavaScript > Frameworks > Frontend > React"
  description: React library

django:
  canonical: "django"
  aliases: []
  parent_tags: [python, web-frameworks, frameworks]
  root: Technology
  category: tech/programming
  depth: 5
  path: "Technology > Programming > Languages > Python > Frameworks > Web > Django"
  description: Django web framework

nextjs:
  canonical: "nextjs"
  aliases: [next, next.js]
  parent_tags: [javascript, react, frontend-frameworks, frameworks]
  root: Technology
  category: tech/programming
  depth: 6
  path: "Technology > Programming > Languages > JavaScript > Frameworks > Frontend > React > Next.js"
  description: Next.js React framework

flask:
  canonical: "flask"
  aliases: []
  parent_tags: [python, web-frameworks, frameworks]
  root: Technology
  category: tech/programming
  depth: 5
  path: "Technology > Programming > Languages > Python > Frameworks > Web > Flask"
  description: Flask web framework

express:
  canonical: "express"
  aliases: [expressjs]
  parent_tags: [javascript, backend-frameworks, frameworks]
  root: Technology
  category: tech/programming
  depth: 5
  path: "Technology > Programming > Languages > JavaScript > Frameworks > Backend > Express"
  description: Express.js framework

vue:
  canonical: "vue"
  aliases: [vuejs]
  parent_tags: [javascript, frontend-frameworks, frameworks]
  root: Technology
  category: tech/programming
  depth: 5
  path: "Technology > Programming > Languages > JavaScript > Frameworks > Frontend > Vue"
  description: Vue.js framework

angular:
  canonical: "angular"
  aliases: []
  parent_tags: [javascript, frontend-frameworks, frameworks]
  root: Technology
  category: tech/programming
  depth: 5
  path: "Technology > Programming > Languages > JavaScript > Frameworks > Frontend > Angular"
  description: Angular framework

svelte:
  canonical: "svelte"
  aliases: []
  parent_tags: [javascript, frontend-frameworks, frameworks]
  root: Technology
  category: tech/programming
  depth: 5
  path: "Technology > Programming > Languages > JavaScript > Frameworks > Frontend > Svelte"
  description: Svelte framework

pytorch:
  canonical: "pytorch"
  aliases: []
  parent_tags: [python, ml-frameworks, frameworks, machine-learning]
  root: Technology
  category: tech/programming
  depth: 6
  path: "Technology > Programming > Languages > Python > Frameworks > Machine Learning > PyTorch"
  description: PyTorch ML framework

tensorflow:
  canonical: "tensorflow"
  aliases: [tf]
  parent_tags: [python, ml-frameworks, frameworks, machine-learning]
  root: Technology
  category: tech/programming
  depth: 6
  path: "Technology > Programming > Languages > Python > Frameworks > Machine Learning > TensorFlow"
  description: TensorFlow ML framework
```

### Infrastructure & Tools
```yaml
docker:
  canonical: "docker"
  aliases: [containers]
  parent_tags: [containerization, infrastructure, devops]
  root: Technology
  category: tech/infrastructure
  depth: 4
  path: "Technology > Infrastructure > DevOps > Containerization > Docker"
  description: Docker containerization

kubernetes:
  canonical: "kubernetes"
  aliases: [k8s]
  parent_tags: [orchestration, containerization, infrastructure, devops]
  root: Technology
  category: tech/infrastructure
  depth: 5
  path: "Technology > Infrastructure > DevOps > Containerization > Orchestration > Kubernetes"
  description: Kubernetes orchestration

git:
  canonical: "git"
  aliases: [github, gitlab, gitea]
  parent_tags: [version-control, tools, devops]
  root: Technology
  category: tech/tools
  depth: 4
  path: "Technology > Tools > DevOps > Version Control > Git"
  description: Version control

nginx:
  canonical: "nginx"
  aliases: []
  parent_tags: [web-servers, infrastructure, servers]
  root: Technology
  category: tech/infrastructure
  depth: 4
  path: "Technology > Infrastructure > Servers > Web Servers > Nginx"
  description: Nginx web server

apache:
  canonical: "apache"
  aliases: []
  parent_tags: [web-servers, infrastructure, servers]
  root: Technology
  category: tech/infrastructure
  depth: 4
  path: "Technology > Infrastructure > Servers > Web Servers > Apache"
  description: Apache web server

terraform:
  canonical: "terraform"
  aliases: []
  parent_tags: [iac, infrastructure, devops]
  root: Technology
  category: tech/infrastructure
  depth: 4
  path: "Technology > Infrastructure > DevOps > IaC > Terraform"
  description: Terraform IaC

ansible:
  canonical: "ansible"
  aliases: []
  parent_tags: [automation, infrastructure, devops]
  root: Technology
  category: tech/infrastructure
  depth: 4
  path: "Technology > Infrastructure > DevOps > Automation > Ansible"
  description: Ansible automation

ci-cd:
  canonical: "ci-cd"
  aliases: [cicd, ci/cd, continuous-integration]
  parent_tags: [automation, devops, infrastructure]
  root: Technology
  category: tech/infrastructure
  depth: 4
  path: "Technology > Infrastructure > DevOps > Automation > CI/CD"
  description: CI/CD pipelines

linux:
  canonical: "linux"
  aliases: [unix]
  parent_tags: [operating-systems, tools]
  root: Technology
  category: tech/tools
  depth: 3
  path: "Technology > Tools > Operating Systems > Linux"
  description: Linux operating system

windows:
  canonical: "windows"
  aliases: []
  parent_tags: [operating-systems, tools]
  root: Technology
  category: tech/tools
  depth: 3
  path: "Technology > Tools > Operating Systems > Windows"
  description: Windows operating system

macos:
  canonical: "macos"
  aliases: [mac, osx]
  parent_tags: [operating-systems, tools]
  root: Technology
  category: tech/tools
  depth: 3
  path: "Technology > Tools > Operating Systems > macOS"
  description: macOS operating system
```

### Databases
```yaml
postgres:
  canonical: "postgres"
  aliases: [postgresql, psql]
  parent_tags: [relational-databases, databases, data-storage]
  root: Technology
  category: tech/databases
  depth: 4
  path: "Technology > Data > Databases > Relational > PostgreSQL"
  description: PostgreSQL database

mysql:
  canonical: "mysql"
  aliases: []
  parent_tags: [relational-databases, databases, data-storage]
  root: Technology
  category: tech/databases
  depth: 4
  path: "Technology > Data > Databases > Relational > MySQL"
  description: MySQL database

mongodb:
  canonical: "mongodb"
  aliases: [mongo]
  parent_tags: [nosql-databases, databases, data-storage]
  root: Technology
  category: tech/databases
  depth: 5
  path: "Technology > Data > Databases > NoSQL > Document > MongoDB"
  description: MongoDB NoSQL database

redis:
  canonical: "redis"
  aliases: []
  parent_tags: [nosql-databases, databases, data-storage, caching]
  root: Technology
  category: tech/databases
  depth: 5
  path: "Technology > Data > Databases > NoSQL > Key-Value > Redis"
  description: Redis in-memory store

sqlite:
  canonical: "sqlite"
  aliases: []
  parent_tags: [relational-databases, databases, data-storage, embedded]
  root: Technology
  category: tech/databases
  depth: 5
  path: "Technology > Data > Databases > Relational > Embedded > SQLite"
  description: SQLite embedded database

neo4j:
  canonical: "neo4j"
  aliases: []
  parent_tags: [graph-databases, nosql-databases, databases, data-storage]
  root: Technology
  category: tech/databases
  depth: 5
  path: "Technology > Data > Databases > NoSQL > Graph > Neo4j"
  description: Neo4j graph database

elasticsearch:
  canonical: "elasticsearch"
  aliases: [elastic]
  parent_tags: [search-engines, nosql-databases, databases, data-storage]
  root: Technology
  category: tech/databases
  depth: 5
  path: "Technology > Data > Databases > NoSQL > Search > Elasticsearch"
  description: Elasticsearch search engine

dynamodb:
  canonical: "dynamodb"
  aliases: []
  parent_tags: [nosql-databases, databases, data-storage, cloud, aws]
  root: Technology
  category: tech/databases
  depth: 6
  path: "Technology > Data > Databases > NoSQL > Document > Cloud > DynamoDB"
  description: AWS DynamoDB
```

### Cloud Providers
```yaml
aws:
  canonical: "aws"
  aliases: [amazon-web-services]
  parent_tags: [cloud-providers, cloud, infrastructure]
  root: Technology
  category: tech/cloud
  depth: 3
  path: "Technology > Infrastructure > Cloud > AWS"
  description: Amazon Web Services

azure:
  canonical: "azure"
  aliases: [microsoft-azure]
  parent_tags: [cloud-providers, cloud, infrastructure]
  root: Technology
  category: tech/cloud
  depth: 3
  path: "Technology > Infrastructure > Cloud > Azure"
  description: Microsoft Azure

gcp:
  canonical: "gcp"
  aliases: [google-cloud, google-cloud-platform]
  parent_tags: [cloud-providers, cloud, infrastructure]
  root: Technology
  category: tech/cloud
  depth: 3
  path: "Technology > Infrastructure > Cloud > GCP"
  description: Google Cloud Platform

digitalocean:
  canonical: "digitalocean"
  aliases: [do]
  parent_tags: [cloud-providers, cloud, infrastructure]
  root: Technology
  category: tech/cloud
  depth: 3
  path: "Technology > Infrastructure > Cloud > DigitalOcean"
  description: DigitalOcean

vercel:
  canonical: "vercel"
  aliases: []
  parent_tags: [hosting-platforms, cloud, infrastructure]
  root: Technology
  category: tech/cloud
  depth: 4
  path: "Technology > Infrastructure > Cloud > Hosting > Vercel"
  description: Vercel hosting

netlify:
  canonical: "netlify"
  aliases: []
  parent_tags: [hosting-platforms, cloud, infrastructure]
  root: Technology
  category: tech/cloud
  depth: 4
  path: "Technology > Infrastructure > Cloud > Hosting > Netlify"
  description: Netlify hosting

heroku:
  canonical: "heroku"
  aliases: []
  parent_tags: [paas, cloud-providers, cloud, infrastructure]
  root: Technology
  category: tech/cloud
  depth: 4
  path: "Technology > Infrastructure > Cloud > PaaS > Heroku"
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

## NON-TECH DOMAIN EXAMPLES

### Language & Linguistics
```yaml
chinese-grammar:
  canonical: "chinese-grammar"
  aliases: [mandarin-grammar, chinese-syntax]
  parent_tags: [grammar, chinese-language, linguistics]
  root: Language
  category: language/grammar
  depth: 4
  path: "Language > Chinese > Grammar > Rules"
  description: Chinese language grammatical rules and structures

chinese-time-expressions:
  canonical: "chinese-time-expressions"
  aliases: [时间表达, time-words-chinese]
  parent_tags: [chinese-grammar, grammar, chinese-language]
  root: Language
  category: language/grammar
  depth: 5
  path: "Language > Chinese > Grammar > Rules > Time Expressions"
  description: Time-related expressions in Chinese (几点, 什么时候)

pinyin:
  canonical: "pinyin"
  aliases: [chinese-romanization]
  parent_tags: [writing-systems, chinese-language, linguistics]
  root: Language
  category: language/writing
  depth: 4
  path: "Language > Chinese > Writing Systems > Pinyin"
  description: Romanization system for Mandarin Chinese

hanzi:
  canonical: "hanzi"
  aliases: [chinese-characters, 汉字]
  parent_tags: [writing-systems, chinese-language, linguistics]
  root: Language
  category: language/writing
  depth: 4
  path: "Language > Chinese > Writing Systems > Hanzi"
  description: Chinese characters
```

### History
```yaml
ea-nasir:
  canonical: "ea-nasir"
  aliases: [copper-merchant-ea-nasir]
  parent_tags: [historical-figures, mesopotamia, bronze-age, ancient-traders]
  root: History
  category: history/people
  depth: 5
  path: "History > Ancient > Bronze Age > Mesopotamia > Notable Figures > Ea-nasir"
  description: Ancient Mesopotamian copper trader, known from complaint tablets

dilmun-trading-guild:
  canonical: "dilmun-trading-guild"
  aliases: [dilmun-merchants, dilmun-traders]
  parent_tags: [trading-organizations, dilmun, bronze-age, mesopotamian-trade]
  root: History
  category: history/organizations
  depth: 6
  path: "History > Ancient > Bronze Age > Mesopotamia > Trade > Organizations > Dilmun Trading Guild"
  description: Bronze Age trading organization based in Dilmun

mesopotamian-trade:
  canonical: "mesopotamian-trade"
  aliases: [ancient-mesopotamian-commerce, bronze-age-trade]
  parent_tags: [ancient-trade, mesopotamia, bronze-age, economics]
  root: History
  category: history/economics
  depth: 5
  path: "History > Ancient > Bronze Age > Mesopotamia > Economics > Trade"
  description: Trade systems and commerce in ancient Mesopotamia

copper-trade:
  canonical: "copper-trade"
  aliases: [bronze-age-copper, copper-commerce]
  parent_tags: [ancient-trade, bronze-age, metallurgy, resources]
  root: History
  category: history/economics
  depth: 6
  path: "History > Ancient > Bronze Age > Resources > Metals > Copper > Trade"
  description: Copper trading in the Bronze Age
```

### Culture
```yaml
western-culture:
  canonical: "western-culture"
  aliases: [western-civilization]
  parent_tags: [cultural-studies, world-cultures]
  root: Culture
  category: culture/regions
  depth: 2
  path: "Culture > Regions > Western"
  description: Cultural traditions and practices of Western civilization

eastern-culture:
  canonical: "eastern-culture"
  aliases: [eastern-civilization, asian-culture]
  parent_tags: [cultural-studies, world-cultures]
  root: Culture
  category: culture/regions
  depth: 2
  path: "Culture > Regions > Eastern"
  description: Cultural traditions and practices of Eastern civilizations
```

### Projects
```yaml
projects:
  canonical: "Projects"
  aliases: []
  parent_tags: []
  root: Projects
  category: projects
  depth: 1
  path: "Projects"
  description: User's active and completed projects

youtube-sentiment-project:
  canonical: "YouTube Sentiment Project"
  aliases: [YouTube Sentiment, yt-sentiment, youtube-sentiment]
  parent_tags: [projects, data-science, python]
  root: Projects
  category: projects/data-science
  depth: 3
  path: "Projects > Data Science > YouTube Sentiment"
  description: YouTube comment sentiment analysis for financial markets

second-brain-project:
  canonical: "Second Brain System"
  aliases: [second-brain, memory-system, obsidian-system]
  parent_tags: [projects, knowledge-management, automation]
  root: Projects
  category: projects/personal-knowledge
  depth: 3
  path: "Projects > Personal Knowledge > Second Brain"
  description: Obsidian-based second brain system with automated processing pipeline
```

## NOTES FOR AI AGENTS

When processing conversations:
1. **Load this taxonomy first** before tagging
2. **Check canonical forms** for entity resolution
3. **Use aliases** to match variations
4. **Calculate semantic similarity** for uncertain matches
5. **Propose to Tag Review Queue** when confidence < 0.60
6. **Apply hierarchical tags** (category + specific)
7. **Prefer existing tags** over creating new ones
8. **Support ANY domain** - not limited to technology
9. **Infer appropriate root** (Technology, Language, History, Culture, Science, Art, etc.)
10. **Link to Neo4j entities** for cross-referencing

Remember: **Consistency > Completeness**. Better to use fewer tags consistently than many tags inconsistently.

**CRITICAL**: This taxonomy supports flexible domains. If conversation discusses Chinese grammar, extract those entities. If it discusses Bronze Age trade, extract those. Don't force everything into Technology category.

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
