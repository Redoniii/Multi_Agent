# Enterprise Multi-Agent Copilot – Supply Chain

A production-ready multi-agent system that transforms supply chain business requests into structured, decision-ready deliverables using coordinated AI agents, grounded in retrieved evidence from supply chain management documents and best practices.

## 🎯 What It Does

**System Workflow:** Plan → Research → Draft → Verify → Deliver

- 📋 **Planner Agent** - Decomposes your business task into ordered subtasks
- 🔎 **Research Agent** - Retrieves grounded evidence with full citations
- ✍️ **Writer Agent** - Generates executive summary, client email, and action items
- ✔️ **Verifier Agent** - Blocks unsupported claims and detects contradictions

**Key Features:**
- ✅ Full citation tracking (document name + chunk ID)
- ✅ Marks unsupported claims with `[NOT FOUND IN SOURCES]`
- ✅ Structured JSON outputs (summary, email, actions, sources)
- ✅ Complete trace logs with latency metrics
- ✅ Web UI with Streamlit

## 📁 Project Structure

```
Project5/
├── /app              # Streamlit UI
│   └── main.py       # Web interface
├── /agents           # AI agent implementations
│   ├── planner_agent.py
│   ├── research_agent.py
│   ├── writer_agent.py
│   └── verifier_agent.py
├── /retrieval        # Document loaders & vector store
│   └── vector_store.py
├── /data             # Supply chain documents (8 PDFs)
│   └── README.md     # Document inventory & descriptions
├── /eval             # Test prompts & acceptance criteria
│   └── test_prompts.json  # 10 test cases
├── graph.py          # Workflow orchestrator
└── README.md         # This file
```

## 🚀 Quick Start (5 minutes)

### 1. Prerequisites
- Python 3.9+
- OpenAI API key (GPT-4o-mini access)

### 2. Setup

```bash
# Clone/navigate to project
cd Project5

# Create virtual environment (if not already done)
python -m venv .venv
.venv\Scripts\activate  # Windows
# or source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file with your OpenAI key
echo OPENAI_API_KEY=sk-... > .env
```

### 3. Run the Web UI

```bash
streamlit run app/main.py
```

Then open `http://localhost:8501` in your browser.

### 4. Try an Example Query

```
"What are the key strategies for improving supply chain resilience?"
```

The system will:
1. Plan the analysis
2. Research documents with citations
3. Draft executive summary, email, and action items
4. Verify all claims against sources
5. Display results with full trace log

### 4. Try an Example Query that will trigger the NOT FOUND IN SOURCES.

```
"What are the best practices for treating autoimmune diseases?"
```

## 🧪 Testing

**Eval folder :** You can find the test prompts in the -test_prompts.json- file..

## 🔧 Configuration

### .env File
```
OPENAI_API_KEY=sk-your-key-here
```

### Agent Communication Flow
```
User Input
    ↓
Planner → (task decomposition) → Plan
    ↓
Research → (document retrieval) → Notes + Citations
    ↓
Writer → (structured generation) → JSON output
    ↓
Verifier → (claim validation) → Verified output
    ↓
Deliverable (summary, email, actions, sources)
```


