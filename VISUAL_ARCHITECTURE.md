# 🏗️ Visual Architecture

Detailed documentation of the technical workflows and architectural patterns powering **Git History Storyteller**.

## 1. High-Level System Architecture
The system follows a decoupled asychronous pattern designed for high throughput and resilience.

```mermaid
graph TD
    Client["React Frontend (Vite)"] -->|"SSE / Streaming"| API["FastAPI Backend"]
    
    subgraph "Data Acquisition Layer"
        API -->|"Bulk Fetch"| GQL["GitHub GraphQL API"]
        API -->|"Deep enrichment"| REST["GitHub REST API"]
    end
    
    subgraph "Processing Tier"
        API -->|"Analysis Signals"| SE["Statistics Engine (O(N))"]
        SE -->|"Thematic Context"| AI["AI Layer (Groq/Ollama)"]
    end
    
    subgraph "Persistence"
        API <-->|"SHA-Validation"| Cache[("SQLite Cache (repository_cache.db)")]
    end
    
    AI -->|"JSON Narrative"| API
    API -->|"Final Payload"| Client
```

## 2. Request Lifecycle (Fast Path vs Cold Path)
This diagram illustrates how the SHA-based caching mechanism handles requests.

```mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant C as SQLite Cache
    participant GH as GitHub API
    participant AI as AI Engine

    U->>A: Analyze Repository URL
    A->>GH: Get latest commit SHA
    A->>C: Check for SHA match
    
    alt Cache Hit
        C-->>A: Return pre-computed JSON
        A-->>U: Instant Load (< 200ms)
    else Cache Miss
        A->>GH: Download History & Diffs
        A->>A: O(N) Statistical Processing
        A->>AI: Generate Narrative
        A->>C: Store result with SHA
        A-->>U: Render full dashboard
    end
```

## 3. AI Resilience & Fallback Logic
The system is designed to provide intelligence even when cloud services fail.

```mermaid
stateDiagram-v2
    [*] --> groq
    groq --> Success: API 200 OK
    groq --> gemini: API 429/500/No Key
    gemini --> Success: API 200 OK
    gemini --> ollama: API 429/500/No Key
    ollama --> Success: Local Inference OK
    ollama --> RawData: Local Failure
    
    Success --> [*]
    RawData --> [*] : Show metrics w/o narrative
```

---

## 4. Key Architectural Decisions

### Why GraphQL + REST?
GraphQL provides the high-level history and PR metadata in a single round-trip. However, REST is used for commit enrichment because GitHub's GraphQL implementation has stricter complexity limits for individual file diffs. This hybrid approach yields the best performance.

### Why O(N) Processing?
The `StatisticsEngine` uses single-pass iterations to compute metrics like code churn, bus factor, and hotspots simultaneously. This prevents the "Walking Dead" problem where complexity grows exponentially with repository size.

### Docker Volume Persistence
By mounting `./backend/data:/app/data`, we ensure that your analyzed repository history survives even when the containers are destroyed and rebuilt (`docker-compose down`).
