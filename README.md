# 🤖 Universal AI Chatbot

A full-stack, multi-provider AI assistant platform inspired by ChatGPT and Claude. It talks to **OpenAI, Groq, and Google Gemini** through one unified provider layer, orchestrates conversations with **LangGraph**, calls external tools through **MCP (Model Context Protocol)**, remembers context across turns, and streams answers token-by-token to a **React + TypeScript** interface.

The codebase is built as a modular, production-oriented reference architecture rather than a demo, with clean separation between the API, service, orchestration, and provider layers.

---

## 📑 Table of Contents

1. [Features](#-features)
2. [Architecture](#-architecture)
3. [Tech Stack](#-tech-stack)
4. [Project Structure](#-project-structure)
5. [Getting Started](#-getting-started)
6. [Configuration](#-configuration)
7. [API Reference](#-api-reference)
8. [How It Works](#-how-it-works)
9. [Tools and MCP Servers](#-tools-and-mcp-servers)
10. [Memory](#-memory)
11. [Testing and Verification](#-testing-and-verification)
12. [Troubleshooting](#-troubleshooting)
13. [Current Status and Roadmap](#-current-status-and-roadmap)
14. [Security Notes](#-security-notes)
15. [Contributing](#-contributing)
16. [License](#-license)

---

## ✨ Features

- **Multi-provider LLM support**: OpenAI, Groq, and Google Gemini behind a single factory (`get_llm`). Switch providers per request with one field.
- **Automatic retry and fallback**: transient failures are retried with exponential backoff; if a provider keeps failing, the request automatically falls back to another provider.
- **Agent orchestration with LangGraph**: a stateful graph handles the LLM call, tool execution, and approval steps.
- **Tool calling**: built-in local tools (safe calculator, weather, web search) plus tools loaded dynamically from MCP servers.
- **MCP integration**: three MCP servers (math, weather, search) are launched automatically over stdio and their tools are registered at startup.
- **Human-in-the-loop approval**: risky tools (web search) pause the graph and wait for a human to approve or reject before running.
- **Short-term memory**: conversation history is persisted per `thread_id` using a LangGraph checkpointer, so clients only send the new message each turn.
- **Long-term memory**: per-user facts stored across threads using a LangGraph Store.
- **Real-time streaming**: Server-Sent Events (SSE) endpoint streams tokens as they are generated.
- **User feedback**: 👍 / 👎 ratings with optional comments, stored per thread.
- **Robust error handling**: custom exception hierarchy with global handlers that return safe JSON errors and never leak tracebacks.
- **Structured logging**: configurable log level and format.
- **Modern frontend**: React 19, TypeScript, Vite, and Tailwind CSS with a streaming chat UI.

---

## 🏗 Architecture

```
┌──────────────────────┐        HTTP / SSE         ┌─────────────────────────────────────┐
│  React + TypeScript  │ ────────────────────────▶ │            FastAPI (api/)            │
│  (Vite, Tailwind)    │ ◀──────────────────────── │  /chat  /chat/stream  /chat/approve  │
└──────────────────────┘                           │  /feedback  /health                  │
                                                   └──────────────────┬──────────────────┘
                                                                      │
                                                   ┌──────────────────▼──────────────────┐
                                                   │         Service layer (services/)    │
                                                   │  chat_service · feedback_service     │
                                                   └──────────────────┬──────────────────┘
                                                                      │
                                                   ┌──────────────────▼──────────────────┐
                                                   │      LangGraph workflow (graph/)     │
                                                   │                                      │
                                                   │   START ─▶ call_llm ──┬─▶ END        │
                                                   │              ▲        │              │
                                                   │              │        ▼              │
                                                   │            tools ◀─ human_approval   │
                                                   └───────┬──────────────────┬──────────┘
                                                           │                  │
                                         ┌─────────────────▼───┐   ┌──────────▼──────────┐
                                         │  LLM factory (llm/) │   │  Tools (tools/, mcp/)│
                                         │  OpenAI · Groq ·    │   │  Local tools + MCP   │
                                         │  Gemini + fallback  │   │  servers (stdio)     │
                                         └─────────────────────┘   └─────────────────────┘
                                                           │
                                         ┌─────────────────▼───────────────────┐
                                         │  Memory (memory/)                    │
                                         │  Checkpointer (thread) · Store (user)│
                                         └──────────────────────────────────────┘
```

**Layering rule:** each layer only talks to the one below it. The API layer never touches the graph directly, and only the factory knows about the concrete provider classes. This is what makes it easy to add a new model, tool, or provider without rewriting anything else.

### Graph flow

```
START → call_llm → route_after_llm
                     ├── no tool calls ............................ END
                     ├── tool calls (all low-risk) ................ tools → call_llm
                     └── tool calls include a risky tool .......... human_approval
                                                                      ├── approved ... tools → call_llm
                                                                      └── rejected ... call_llm (with rejection message)
```

---

## 🧰 Tech Stack

| Area | Technology |
|------|-----------|
| **Backend framework** | FastAPI, Uvicorn |
| **Validation / settings** | Pydantic v2, pydantic-settings |
| **Agent orchestration** | LangGraph, LangChain |
| **LLM providers** | `langchain-openai`, `langchain-groq`, `langchain-google-genai` |
| **Tool protocol** | MCP (`mcp`, `langchain-mcp-adapters`) |
| **Web search** | DuckDuckGo (`ddgs`), no API key needed |
| **Weather** | wttr.in, no API key needed |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS 4 |
| **Testing** | pytest, pytest-asyncio, pytest-mock, httpx |

---

## 📁 Project Structure

```
Universal_AI_Chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app, routers, startup (MCP + graph build)
│   │   ├── api/                    # Thin HTTP layer
│   │   │   ├── chat.py             #   POST /chat, /chat/stream, /chat/approve
│   │   │   ├── feedback.py         #   POST /feedback, GET /feedback/{thread_id}
│   │   │   └── health.py           #   GET /health
│   │   ├── services/               # Business logic
│   │   │   ├── chat_service.py     #   invoke / stream / resume the graph
│   │   │   └── feedback_service.py #   record and list feedback
│   │   ├── graph/                  # LangGraph workflow
│   │   │   ├── workflow.py         #   builds and compiles the graph (cached)
│   │   │   ├── nodes.py            #   call_llm, human_approval
│   │   │   ├── edges.py            #   route_after_llm (conditional routing)
│   │   │   └── state.py            #   GraphState (messages, provider, model_name)
│   │   ├── llm/                    # Provider abstraction
│   │   │   ├── base.py             #   BaseLLMProvider + text extraction helper
│   │   │   ├── factory.py          #   get_llm, get_default_model, invoke_with_fallback
│   │   │   ├── openai_provider.py
│   │   │   ├── groq_provider.py
│   │   │   └── gemini_provider.py
│   │   ├── tools/                  # Local tools
│   │   │   ├── calculator.py       #   AST-based safe arithmetic (no eval)
│   │   │   ├── weather.py          #   wttr.in
│   │   │   └── search.py           #   DuckDuckGo
│   │   ├── mcp/                    # MCP integration
│   │   │   ├── client.py           #   MultiServerMCPClient config (3 stdio servers)
│   │   │   └── tool_manager.py     #   load once at startup, merge with local tools
│   │   ├── memory/
│   │   │   ├── short_term.py       #   checkpointer (per-thread history)
│   │   │   ├── long_term.py        #   Store (per-user facts)
│   │   │   └── manager.py          #   builds user context from stored facts
│   │   ├── models/                 # Pydantic request/response schemas
│   │   ├── config/settings.py      # Environment-driven settings
│   │   ├── core/                   # constants, exceptions, logging
│   │   └── utils/retry.py          # retry with exponential backoff
│   ├── tests/
│   ├── verify_module_*.py          # Step-by-step verification scripts
│   ├── list_gemini_models.py       # Helper: list available Gemini models
│   └── list_groq_models.py         # Helper: list available Groq models
├── mcp_servers/
│   ├── math_server.py              # mcp_add, mcp_subtract, mcp_multiply, mcp_divide
│   ├── weather_server.py           # mcp_get_weather
│   └── search_server.py            # mcp_web_search
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── hooks/useChat.ts        # chat state + streaming logic
│   │   ├── services/api.ts         # SSE streaming client + feedback call
│   │   ├── components/             # Sidebar, ChatWindow, ChatInput, Message, ...
│   │   └── pages/                  # Chat, Settings
│   ├── package.json
│   └── vite.config.ts
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- At least one LLM API key: [OpenAI](https://platform.openai.com/), [Groq](https://console.groq.com/), or [Google AI Studio (Gemini)](https://aistudio.google.com/)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd Universal_AI_Chatbot
```

### 2. Backend setup

```bash
# Create and activate a virtual environment
python -m venv venv

# macOS / Linux
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# MCP and search packages used by the tools and MCP servers
pip install mcp langchain-mcp-adapters ddgs
```

> **Note:** the MCP servers are launched with the `python` command, so make sure your virtual environment is **activated** when you start the backend. Otherwise the servers may start with the wrong interpreter and the MCP tools will not load.

### 3. Configure environment variables

```bash
cp .env.example backend/.env
```

Open `backend/.env` and add at least one provider key (see [Configuration](#-configuration)).

### 4. Run the backend

The `.env` file is read from the current working directory, so start the server **from the `backend/` folder**:

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

On startup you should see log lines showing the MCP tools being loaded. Then check:

- Health check: <http://127.0.0.1:8000/health>
- Interactive API docs (Swagger): <http://127.0.0.1:8000/docs>

### 5. Run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (usually <http://localhost:5173>).

> The frontend calls the backend at `http://127.0.0.1:8000` (set in `frontend/src/services/api.ts`). If you change the backend host or port, update `API_BASE_URL` there.

---

## ⚙️ Configuration

All settings are loaded from environment variables (or `backend/.env`) via `pydantic-settings`.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | One provider key required | none | OpenAI API key |
| `GROQ_API_KEY` | One provider key required | none | Groq API key |
| `GEMINI_API_KEY` | One provider key required | none | Google Gemini API key |
| `OPENAI_DEFAULT_MODEL` | No | `gpt-4o-mini` | Default OpenAI model |
| `GROQ_DEFAULT_MODEL` | No | `openai/gpt-oss-20b` | Default Groq model |
| `GEMINI_DEFAULT_MODEL` | No | `gemini-flash-lite-latest` | Default Gemini model |
| `APP_ENV` | No | `development` | `development`, `staging`, or `production` |
| `LOG_LEVEL` | No | `INFO` | Python log level |
| `DATABASE_URL` | No | none | Reserved for the planned PostgreSQL storage (not used yet) |

**Example `backend/.env`:**

```env
GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here

APP_ENV=development
LOG_LEVEL=INFO
```

> If a provider's key is missing, requests to that provider return a clear `ProviderConfigurationError`, and the fallback logic skips it. You only need keys for the providers you want to use.

---

## 📡 API Reference

Base URL: `http://127.0.0.1:8000`

### `GET /health`

Liveness check.

```json
{ "status": "ok", "app": "Universal AI Chatbot", "version": "0.1.0", "environment": "development" }
```

### `POST /chat`

Send a message and get the full reply (non-streaming). This is the fully supported path for approval flows.

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | yes | The user's message |
| `provider` | string | no (default `groq`) | `openai`, `groq`, or `gemini` |
| `model_name` | string | no | Specific model; defaults to the provider's default |
| `thread_id` | string | no | Reuse to continue a conversation; omitted = new thread |

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 12 * (4 + 1)?", "provider": "groq"}'
```

**Response**

```json
{
  "reply": "12 * (4 + 1) = 60",
  "provider": "groq",
  "model_name": "openai/gpt-oss-20b",
  "thread_id": "3f0c1a2e-...",
  "requires_approval": false,
  "approval_request": null
}
```

If the model wants to run a tool that needs approval (e.g. web search), the response comes back **paused**:

```json
{
  "reply": "",
  "requires_approval": true,
  "approval_request": {
    "type": "tool_approval",
    "tool_calls": [{ "name": "web_search", "args": { "query": "latest AI news" } }]
  },
  "thread_id": "3f0c1a2e-..."
}
```

### `POST /chat/approve`

Resume a paused conversation with a human decision.

```bash
curl -X POST http://127.0.0.1:8000/chat/approve \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "3f0c1a2e-...", "approved": true}'
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `thread_id` | string | yes | The paused conversation's thread |
| `approved` | boolean | yes | `true` to run the tool, `false` to reject |
| `reason` | string | no | Optional reason (passed back to the model on rejection) |

### `POST /chat/stream`

Same request body as `/chat`, but the reply is streamed as **Server-Sent Events**:

```
data: {"thread_id": "3f0c1a2e-..."}      ← first event: the thread to reuse
data: {"content": "Hello"}                ← one event per text chunk
data: {"content": " there!"}
data: {"done": true}                      ← final event
```

Errors mid-stream are sent as `data: {"error": "..."}` followed by `done`.

> **Limitation:** human approval is not yet surfaced in the streaming endpoint. Use `POST /chat` for flows that may trigger an approval-required tool.

### `POST /feedback`

```bash
curl -X POST http://127.0.0.1:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "3f0c1a2e-...", "message_index": 1, "rating": "up", "comment": "Great answer"}'
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `thread_id` | string | yes | Conversation thread |
| `message_index` | integer | no | Index of the rated message |
| `rating` | `"up"` or `"down"` | yes | Thumbs up / down |
| `comment` | string | no | Free text |

### `GET /feedback/{thread_id}`

Returns all feedback recorded for a thread.

### Error format

All handled errors return safe JSON, never a traceback:

```json
{ "error": "OpenAI API key is not configured", "type": "ProviderConfigurationError" }
```

Unexpected errors return `500` with `{"error": "Internal server error", "type": "InternalError"}`; full details go to the logs only.

---

## 🔍 How It Works

### Provider abstraction and fallback

`llm/factory.py` is the only module that knows about all three provider classes. Every provider implements `BaseLLMProvider` (config validation + `get_chat_model`).

`invoke_with_fallback` tries the requested provider first (with up to 2 retries and exponential backoff). If it still fails, it moves through the fallback order **Groq → OpenAI → Gemini**, using each provider's default model. If every provider fails, an `LLMProviderError` is raised listing the attempted providers.

### Human-in-the-loop approval

Tools listed in `TOOLS_REQUIRING_APPROVAL` (`web_search`, `mcp_web_search`) route through the `human_approval` node. It calls LangGraph's `interrupt()`, which pauses the run and saves state in the checkpointer. The client then calls `/chat/approve` with the same `thread_id`, and the graph resumes: approved calls go to the `tools` node, rejected calls send a rejection message back to the model.

Low-risk tools (calculator, weather, math) run automatically.

### Startup sequence

1. Settings are loaded and logging is configured.
2. Exception handlers and routers are registered.
3. On startup, MCP tools are loaded **before** the graph is built, so tool calling works from the very first request. If an MCP server fails, the error is logged and the app continues with local tools only.
4. The LangGraph workflow is compiled once and cached.

---

## 🛠 Tools and MCP Servers

### Local tools (`backend/app/tools/`)

| Tool | Description | Approval needed |
|------|-------------|-----------------|
| `calculator` | Safe arithmetic (`+ - * / **`) using an AST parser. It never uses `eval()` | No |
| `get_weather` | Current weather via wttr.in | No |
| `web_search` | Top 3 DuckDuckGo results | **Yes** |

### MCP servers (`mcp_servers/`)

Started automatically as stdio subprocesses; you do not need to run them manually.

| Server | Tools |
|--------|-------|
| `math_server.py` | `mcp_add`, `mcp_subtract`, `mcp_multiply`, `mcp_divide` |
| `weather_server.py` | `mcp_get_weather` |
| `search_server.py` | `mcp_web_search` (**requires approval**) |

### Adding your own tool

**Local tool:** create a function decorated with `@tool` in `backend/app/tools/`, then add it to `LOCAL_TOOLS` in `tools/__init__.py`.

**MCP tool:** create a `FastMCP` server in `mcp_servers/`, register it in `mcp/client.py`, and its tools are discovered at startup.

To make a tool require approval, add its name to `TOOLS_REQUIRING_APPROVAL` in `core/constants.py`.

---

## 🧠 Memory

| Type | Implementation | Scope | Persistence |
|------|---------------|-------|-------------|
| **Short-term** | LangGraph `InMemorySaver` checkpointer | One conversation (`thread_id`) | In-memory (lost on restart) |
| **Long-term** | LangGraph `InMemoryStore` | Per user, across threads | In-memory (lost on restart) |

Because the checkpointer holds the history, clients only send the **new** message each turn and reuse the `thread_id`.

> Both stores are in-memory and work with a single server process. Moving to PostgreSQL-backed storage is on the roadmap.

---

## ✅ Testing and Verification

Install the test tools (already in `requirements.txt`) and run pytest from the `backend/` folder:

```bash
cd backend
pytest
```

The repository also includes step-by-step verification scripts used during development, one per module:

```bash
cd backend
python verify_module_3.py     # provider layer
python verify_module_4.py
python verify_module_6.py
python verify_module_7.py
python verify_module_8.py
python verify_module_9.py
python verify_module_10.py    # (and 10b, 10c)
```

Helper scripts to see which models your keys can access:

```bash
python list_gemini_models.py
python list_groq_models.py
```

---

## 🩹 Troubleshooting

**The browser shows a CORS error / requests from the frontend fail**
The backend does not currently configure CORS. Add this to `backend/app/main.py` right after creating `app`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**`ProviderConfigurationError: ... API key is not configured`**
The key for that provider is missing. Check that `backend/.env` exists, the variable name is exact (for example `GEMINI_API_KEY`), and you started `uvicorn` from the `backend/` folder.

**`Failed to load MCP tools` in the logs**
Make sure `mcp`, `langchain-mcp-adapters`, and `ddgs` are installed and your virtual environment is activated (MCP servers are launched with the `python` command).

**`ModuleNotFoundError: No module named 'app'`**
Run uvicorn from inside `backend/`: `cd backend && uvicorn app.main:app --reload`.

**Conversation history disappears after a restart**
Expected: memory is currently in-memory only.

**A provider returns "model not found"**
Model names change. Run `list_groq_models.py` or `list_gemini_models.py` and set the matching `*_DEFAULT_MODEL` variable.

---

## 🗺 Current Status and Roadmap

**Working today**

- Multi-provider chat with retry and fallback
- LangGraph agent with local and MCP tools
- Human-in-the-loop tool approval (via `POST /chat` and `/chat/approve`)
- Short-term and long-term memory (in-memory)
- SSE streaming endpoint and streaming React UI
- Feedback API
- Health check, structured logging, global error handling

**Planned / in progress**

- [ ] PostgreSQL persistence for conversation history, long-term memory, and feedback (`DATABASE_URL` is already reserved)
- [ ] Retrieval-Augmented Generation (document upload and vector search)
- [ ] Approval flow inside the streaming endpoint
- [ ] Wire the provider/model selectors, tool-execution display, code blocks, and feedback buttons fully into the UI
- [ ] User authentication and per-user conversations
- [ ] Docker and Docker Compose setup
- [ ] Rate limiting
- [ ] Automated test suite and CI (GitHub Actions)
- [ ] Production deployment guide

---

## 🔐 Security Notes

- **Never commit `.env`.** It is listed in `.gitignore`. Use `.env.example` as the template and rotate any key that was ever committed or shared.
- The calculator tool parses expressions with `ast` and only allows a small set of arithmetic operators; it never executes arbitrary code.
- Errors returned to clients are sanitized; full details are logged server-side only.
- Web search requires explicit human approval before it runs.
- Before deploying publicly, add authentication, restrict CORS origins, and add rate limiting.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push the branch: `git push origin feature/my-feature`
5. Open a Pull Request

When adding code, please keep to the layering rule: **API → service → graph → provider/tools**, with no business logic in `api/` or `main.py`.

---

## 📄 License

MIT

---

## 👤 Author

**Your Name**
- GitHub: [@147Ayush](https://github.com/147Ayush)
- LinkedIn: [ayushsoni96](www.linkedin.com/in/ayushsoni96)

⭐ If you found this project useful, consider giving it a star!
