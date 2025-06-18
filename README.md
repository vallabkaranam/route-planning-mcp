# 🗺️ Route Planning MCP Tool Server

A modern, production-grade API service designed for both traditional frontends and LLM-based agents. This backend system empowers AI agents to plan trips, geocode locations, search nearby mountains, and find EV chargers—using a lightweight, type-safe FastAPI backend that’s fully compliant with the Model Context Protocol (MCP).

**Live MCP Server**: [https://route-planning-mcp.onrender.com](https://route-planning-mcp.onrender.com)

---

## ✨ Key Features

- 🌍 **Geolocation & Mapping Intelligence**

  - Geocodes human-readable locations to lat/lon using OpenStreetMap Nominatim
  - Fetches optimized driving routes via OpenRouteService
  - Calculates ETA and distance summaries
  - Includes landmark & terrain context: mountain peak lookup via Overpass API

- ⚡ **Nearby EV Infrastructure**

  - Local, statically indexed EV charger data
  - Fast Haversine-filtered spatial queries for chargers by radius

- 🧠 **LLM-Friendly & MCP-Compliant**

  - Built with [`fastapi-mcp`](https://github.com/multion/fastapi-mcp) to conform to Model Context Protocol (MCP)
  - Semantic errors (e.g., `LOCATION_NOT_FOUND`, `ORS_API_FAILED`)
  - Type-safe responses for seamless tool discovery and reasoning in agents

- 🛠️ **Tool & pipeline orchestration**  
  Showcases real-world **agent tooling primitives** — geocoding, routing, environmental context — that form the building blocks of **RAG**, **vector memory**, and **multi-tool workflows**

- 🚀 **AI-First Architecture & Agentic Systems**

  - Demonstrates how to build an **MCP-compliant tool server** to enable **multi-step LLM reasoning**
  - Useful for **LLMOps**, **AI Platform Engineering**, and **Agent-Oriented Design** portfolios

- 📐 **Type-Safe, Structured API Design**
  - Uses FastAPI + Pydantic `response_model`s
  - Semantic error handling
  - Fully OpenAPI-documented with Swagger UI
  - Ideal for toolchains like **LangChain**, **LangGraph**, and **Claude tool use**

---

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Async HTTP Client**: `httpx`
- **Data Modeling**: Pydantic
- **Protocol**: [`fastapi-mcp`](https://github.com/multion/fastapi-mcp)
- **Environment Management**: `python-dotenv`
- **Deployment**: [Render](https://render.com/) (Free-tier, stateless)
- **Geocoding**: OpenStreetMap Nominatim
- **Routing**: OpenRouteService API
- **Terrain Data**: Overpass API (OpenStreetMap)
- **EV Charger Data**: Supercharge.info static JSON

---

## 🚀 Getting Started (Local Development)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/route-planning-mcp.git
cd route-planning-mcp
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` to include your OpenRouteService API key:

```env
ORS_API_KEY=your_openrouteservice_key_here
```

### 5. Run the Server

```bash
uvicorn main:app --reload
```

### 6. Test API

Visit Swagger UI at:  
[http://localhost:8000/docs](http://localhost:8000/docs)

---

## ☁️ Deployment (Render)

Deployed to:  
👉 https://route-planning-mcp.onrender.com

- Render used for interim free-tier deployment
- MCP tool server hosted publicly for LLMs like Claude
- Fast cold start and stateless HTTP design
- No ALB or RDS required — ultra-lightweight cost footprint

---

## 📈 Why This Project Stands Out

- 🔗 **Model Context Protocol (MCP) Expertise**

  - Demonstrates understanding of **agent-tool standards** for interoperable AI tooling
  - Emerging pattern for **Claude, GPT, LangGraph, and OpenAgents** use cases

- 🛠️ **Tool Composition & Multi-Tool Reasoning**

  - Real-world example of tools that support geospatial reasoning
  - Aligns with modern trends in **AI agent orchestration**, **RAG**, and **LLM tool-use**

- 📐 **LLM-Ready, Semantic API Design**

  - Uses typed, structured responses for **tool discovery** and **LLM reasoning**
  - Robust error reporting supports fallback chains in **multi-agent** workflows

- ☁️ **DevOps Simplicity**
  - Stateless API deployed on free-tier Render
  - Easy CI/CD pipeline potential
  - Portable and extensible to ECS, Fargate, Lambda, or Fly.io

---

## 📁 Project Structure

```
route-planning-mcp/
├── main.py               # FastAPI app with MCP server logic
├── ev_chargers.json      # Static EV charger dataset (Supercharge.info)
├── .env.example          # Environment variable template
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## 🧪 Example Use Cases

- Claude Desktop tool connection via MCP
- Trip planner assistant with multimodal steps
- AI agent choosing route based on charger availability
- LangGraph node for geospatial lookup and planning

---

## 📝 License

MIT License – Free to use and adapt. Attribution appreciated!
