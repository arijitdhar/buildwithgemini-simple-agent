# GlobeTrotter AI — Agentic Travel Concierge

![GlobeTrotter AI Demo](./demo.gif)

**GlobeTrotter AI** is an agentic travel concierge built with the **Google Agent Development Kit (ADK)**. It helps users discover global destinations, create personalized travel itineraries, calculate trip budgets, and generate visual travel media (AI postcards and promo videos) directly inside a rich A2UI dialogue interface.

---

## 🚀 Wired Features & Implemented Services

All features listed below are fully implemented in code in `app/agent.py` and deployed on Google Cloud infrastructure:

### 1. 🧠 Cross-Session Long-Term Memory (Vertex AI Memory Bank)
* **Wired via**: `RobustPreloadMemoryTool` & ADK memory callbacks (`generate_memories_callback`).
* **Capability**: Automatically remembers user travel styles (e.g., luxury vs. budget, solo vs. family), dietary preferences, and saved trip history across separate chat sessions.

### 2. 🗄️ Structured Catalog Database (Google Cloud Firestore)
* **Wired via**: Google Cloud Firestore (`travel_catalog` collection).
* **Tools**:
  * `get_destinations`: Queries Firestore for curated travel catalog items by region.
  * `add_destination`: Allows users to add new destinations into the persistent database.
  * `create_itinerary`: Builds personalized day-by-day travel schedules saved in Firestore.

### 3. 🎨 AI Image & Video Generation (Vertex AI Imagen & Gemini Omni)
* **Tools**:
  * `generate_signature_place_image`: Generates high-quality scenic destination previews using Vertex AI (`gemini-3.1-flash-lite-image` in `global` region).
  * `generate_destination_postcard`: Creates custom travel postcards, uploads media bytes to public Google Cloud Storage (`globetrotter-travel-catalog-84b0d8`), and returns public HTTPS links.
  * `generate_destination_promo_video`: Generates short MP4 promo videos using Google's Omni model (`gemini-omni-flash-preview` in `global` region), uploads bytes to Cloud Storage, and saves execution artifacts.

### 4. 🪟 Agent-to-UI (A2UI) Rich Component Surface
* **Wired via**: `a2ui_callback` & custom A2UI web renderer.
* **Capability**: Formats agent tool outputs and responses into structured A2UI cards (Cards, Columns, Rows, Texts, Images, and Video players) instead of plain markdown.

### 5. 🧮 Code Execution & Financial Calculators
* **Tools**:
  * `CodeExecutorTool`: In-agent Python sandbox for dynamic calculations.
  * `calculate_trip_budget`: Computes daily expenditures, total accommodation, food, and activity budgets.
  * `get_currency_exchange_rates`: Fetches real-time foreign currency conversion rates.
  * `get_weather`: Looks up real-time weather forecasts for target cities.
  * `get_current_time`: Provides current UTC timestamps.

---

## 📋 Planned / Stretch Capabilities

* **Google Maps API Live Routing**: *Planned, not yet implemented.* (Turn-by-turn routing and live traffic mapping were proposed in the design brief but are pending future integration).

---

## 🛠️ Project Structure

```
simple-agent/
├── app/
│   ├── agent.py                 # Core ADK agent, tools, callbacks, and system prompt
│   └── __init__.py
├── frontend/
│   ├── main.py                  # FastAPI proxy server (A2A protocol bridge to agent)
│   ├── static/
│   │   ├── index.html           # Modern chat UI & A2UI card renderer
│   │   └── style.css            # GlobeTrotter AI dark theme design system
│   └── template/                # Blueprint templates
├── agents-cli-manifest.yaml     # Agent Platform deployment manifest
├── demo.gif                     # Animated demo recording preview
├── generate_lofi_music.py       # Upbeat lo-fi track generator
└── record_demo.py               # Playwright browser demo recorder
```

---

## 💻 Local Setup & Execution Guide

### Prerequisites
* Python 3.11+
* `uv` package manager (`pip install uv`)
* Google Cloud project configured with Vertex AI and Firestore APIs enabled

### 1. Install Dependencies
```bash
uv sync
```

### 2. Start Local Frontend Server
Set your deployed Agent Engine resource name (or test locally with `app`) and launch the proxy server:

```bash
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_ID>/locations/<LOCATION>/reasoningEngines/<ENGINE_ID>"
export AGENT_DIRECTORY="app"
cd frontend
uv run python main.py
```

The web interface will be served at port `8080`.

### 3. Deploy Agent to Cloud Agent Platform
Deploy updates to Google Cloud Agent Runtime using `agents-cli`:

```bash
agents-cli deploy --no-confirm-project
```

---

## 📜 License

Distributed under the Apache 2.0 License. See `LICENSE` for details.
