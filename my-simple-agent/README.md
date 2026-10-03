# Color Guide for Designers

A conversational AI assistant built with Google's Agent Development Kit (ADK) that helps UI/UX and visual designers generate, audit, and preview color palettes with curated color themes, contrast compliance calculations, and dynamic visual card rendering.

![Color Guide Agent Demo](./agent_demo.gif)

---

## Key Features & Wired-Up Capabilities

This agent is powered by **Google Gemini 2.5 Flash** and integrates the following Google Cloud services and tools:

- **Cross-Session Long-Term Memory**:
  - Powered by **Vertex AI Memory Bank** (`VertexAiMemoryBankService`), persisting user brand style guidelines, contrast targets, and favorite color themes across conversations.
- **Firestore Palette Database**:
  - Reads (`get_palettes`) and writes (`save_palette`) color palette documents to **Google Cloud Firestore**.
- **AI Image Generation & Cloud Storage**:
  - Uses `gemini-3.1-flash-lite-image` on **Vertex AI** (`generate_palette_image`) to generate color swatch preview cards, saving them as ADK artifacts and uploading bytes to **Google Cloud Storage**.
- **AI Video Preview Generation**:
  - Uses `gemini-omni-flash-preview` on **Vertex AI** (`generate_palette_video`) to create short animated color palette preview videos, saved as ADK artifacts and hosted on **Google Cloud Storage**.
- **A2UI Schema Rendering**:
  - Employs `A2uiSchemaManager` (v0.8 BasicCatalog) and callback handlers to stream structured UI cards (Card, Column, Row, Text, Image) directly into the web interface.
- **Python Sandbox Code Execution**:
  - Executes dynamic Python code via `AgentEngineSandboxCodeExecutor` for specialized color calculations.
- **WCAG 2.1 Contrast Analysis**:
  - Calculates exact foreground/background contrast ratios (`calculate_wcag_contrast`) and provides WCAG 2.1 AA/AAA compliance status for normal and large text.
- **Color Details API Integration**:
  - Fetches exact color names, RGB, HSL, CMYK representations, and text contrast guidance via **The Color API** (`get_color_info_api`).
- **Google Maps & Places Integration**:
  - Geocodes addresses (`geocode_address`) and locates nearby design studios, art galleries, and creative spaces (`search_nearby_places`) via Google Maps & Places APIs.

---

## Feature Roadmap

- **OKLCH / Perceptual Color Space Conversions**: *(Planned, not yet implemented)* Native OKLCH color space math functions for perceptually uniform palette manipulation.

---

## Local Development & Setup

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend recording and tooling)
- Google Cloud SDK (`gcloud` CLI) authenticated with access to Vertex AI, Firestore, and Cloud Storage.

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd my-simple-agent
   ```

2. **Set up Python Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Set your Google Cloud Project ID and optional API keys:
   ```bash
   export GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
   export GOOGLE_MAPS_API_KEY="<your-maps-api-key>"       # Optional: for Maps/Places tools
   export THE_COLOR_API_KEY="<your-color-api-key>"       # Optional: for Color API tool
   ```

4. **Run the Local Proxy & Frontend**:
   ```bash
   export AGENT_ENGINE_RESOURCE_NAME="projects/<project-number>/locations/us-east1/reasoningEngines/<engine-id>"
   export AGENT_DIRECTORY="app"
   export PORT=8080

   python main.py
   ```
   Open your browser to `http://localhost:<PORT>` to interact with the local agent proxy.

5. **Record a UI Demo**:
   To generate an updated demo recording using Playwright:
   ```bash
   node ../.agents/skills/record-demo/record-agent.js \
     -u "http://localhost:8080" \
     -q "Generate a dark mode UI color palette with electric blue accents" \
     -q "Save this palette to the Firestore database as 'electric-dev-dark'" \
     -o agent_demo.webm
   ```

---

## License

Copyright 2026 Google LLC. Licensed under the Apache License, Version 2.0.
