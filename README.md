# 🧭 Route Planning MCP

A modular, LLM-ready microservice designed for intelligent agents and frontend clients alike. This backend system supports geocoding, route planning, mountain discovery, and EV charger lookup—leveraging fast, structured APIs tailored for use by both humans and machines.

🔗 [Live API Docs](https://route-planning-mcp.onrender.com/docs)

---

## ✨ Key Features

- 📍 **Geocoding**

  - Converts location text into precise coordinates using OpenStreetMap Nominatim API.

- 🛣️ **Route Planning**

  - Plans optimal routes with distance, duration, step-by-step instructions, and estimated arrival times using OpenRouteService.

- 🏔️ **Mountain Discovery**

  - Finds named and unnamed peaks around a location using Overpass API.

- 🔌 **EV Charger Lookup**

  - Identifies nearby Tesla Superchargers from curated static data using Haversine distance.

- 🤖 **LLM + MCP Integration**

  - Full support for Claude-compatible agents via `fastapi-mcp`, exposing agent-friendly tool schemas with typed responses.

- ⚡ **Production-Ready**
  - Typed Pydantic schemas, HTTPX async calls, FastAPI for blazing-fast performance, and a clean architecture.

---

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Async Client**: HTTPX
- **MCP Toolkit**: `fastapi-mcp` (Claude-compatible)
- **Model Validation**: Pydantic
- **Geocoding API**: OpenStreetMap (Nominatim)
- **Routing API**: OpenRouteService (ORS)
- **Geospatial Query**: Overpass API
- **Deployment**: Render (Free Tier)
- **Environment Config**: python-dotenv
- **Serialization**: JSON (for both AI agents and frontend clients)

---

## 🚀 Deployment

### 🌐 Live URL

```
https://route-planning-mcp.onrender.com
```

### 🧠 Claude Desktop Integration

In your `mcp-config.json`, add:

```json
{
  "mcpServers": {
    "route-planning-mcp": {
      "command": "/path/to/mcp-proxy",
      "args": ["https://route-planning-mcp.onrender.com/mcp"],
      "cwd": "/local/project/path",
      "env": {}
    }
  }
}
```

---

## 🧪 Local Development

### Prerequisites

- Python 3.11+
- `venv`
- OpenRouteService API key (free tier is fine)
- `.env` file with:
  ```env
  ORS_API_KEY=your_api_key_here
  ```

### Setup

```bash
git clone https://github.com/yourusername/route-planning-mcp.git
cd route-planning-mcp

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
uvicorn main:app --reload
```

### Example Test

```bash
curl -X POST http://localhost:8000/geocode_location \
  -H "Content-Type: application/json" \
  -d '{"location_text": "Seattle, WA"}'
```

---

## 📂 Project Structure

```
route-planning-mcp/
├── main.py              # Core FastAPI server and endpoints
├── ev_chargers.json     # Static EV charger database
├── .env                 # Contains ORS_API_KEY
├── requirements.txt     # All dependencies
└── README.md            # Project documentation
```

---

## 📈 Why This Project Stands Out

This microservice showcases:

- ✅ **End-to-End Backend Engineering**: From API integration to async architecture and response typing.
- 🤖 **LLM and AI Tool Integration**: Shows readiness for modern agent ecosystems like Claude.
- 📦 **Microservice Modularity**: Encapsulated, stateless service with a single responsibility—ideal for scaling and service-oriented architecture.
- 💬 **Human & Machine Friendly**: Clear OpenAPI documentation for humans and structured tool specs for LLMs.
- 🏗️ **Deployment Experience**: Deployable to modern cloud platforms like Render and AWS with environment management.

---

## 📝 License

MIT License — use, remix, and extend freely.
