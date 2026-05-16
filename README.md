# ✨ Aura Atelier — Luxury AI Jewellery Stylist & Lookbook Engine

![Python](https://img.shields.io/badge/Python-3.11%2B-deepBurgundy?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Luxury_API-roseGold?style=for-the-badge&logo=fastapi)
![MCP](https://img.shields.io/badge/Protocol-MCP_Stdio-luxuryGold?style=for-the-badge)
![TailwindCSS](https://img.shields.io/badge/Styling-Tailwind_CSS-mutedBlush?style=for-the-badge&logo=tailwindcss)

**Aura Atelier** is a high-fidelity, premium interactive lookbook and AI styling consultation platform. Powered by cutting-edge Multimodal AI and the **Model Context Protocol (MCP)**, the engine analyzes uploaded outfit imagery to curate bespoke, perfectly balanced 4-to-5 piece luxury jewellery ensembles in real-time.

---

## 🎥 Live Platform Demonstration

[![Aura Atelier Demo](https://img.youtube.com/vi/CrxVtq90mRI/0.jpg)](https://youtu.be/CrxVtq90mRI)

*Click the thumbnail above to watch the full video demonstration of the Aura Atelier Luxury AI Jewellery Stylist in action!*

---

## 🌟 Key Architectural Highlights

### 1. Multimodal AI Outfit Analysis
* **Deep Neckline & Craftsmanship Evaluation:** The multimodal vision engine inspects your outfit's neckline cut, embroidery density, and overarching fashion aesthetic.
* **Bespoke Skin Tone Harmony:** Evaluates dominant outfit colors to provide tailored advice on how specific jewel tones complement warm, olive, or fair skin undertones.

### 2. Pure Model Context Protocol (MCP) Orchestration
* **Architectural Decoupling:** Maintains strict protocol purity by separating the core LLM reasoning orchestrator (`agent_stylist.py`) from the live web execution tools (`mcp_server.py`) via a robust `stdio` client-server pipe.
* **Self-Healing Failover:** Features an automated stdio session respawning mechanism to guarantee flawless tool execution even during long-running LLM synthesis windows.

### 3. Double-Layered Live Scraping Engine
* **Advanced Anti-Bot Capabilities:** Equipped with elite scraping headers (`User-Agent`, `Referer`, `Upgrade-Insecure-Requests`) to bypass bot detection walls across major search engines and marketplaces.
* **Multi-Tier Marketplace Fallback:** Dynamically searches **Everstylish** and **Kushal's Fashion Jewellery**, falling back to isolated product shots on **Bing** and a curated high-resolution backup dictionary.
* **Deterministic Query Hashing:** Utilizes mathematical query hashing (`abs(hash(query))`) to ensure that multiple tiles within the same category receive completely distinct, non-repeating catalog images that perfectly match their descriptions.

### 4. Immersive Luxury UI/UX
* **Aura Atelier Splash Screen:** Welcomes users with a shimmering dark-burgundy overlay and a graceful 1.6s fade-out.
* **Golden Sparkle Dust Engine:** Triggers a custom interactive particle animation upon successful lookbook generation to provide premium tactile feedback.
* **Magazine-Quality Editorial Layout:** Features a perfectly symmetrical, vertically balanced two-column grid combining the AI Outfit Analysis and the Stylist's Editorial Note with zero awkward whitespace.

---

## 🚀 Getting Started

### Prerequisites
Ensure you have Python 3.11+ installed along with `pip`.

### Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/luxury-ai-stylist.git
   cd luxury-ai-stylist/session5_assignment
   ```

2. **Create and Activate Virtual Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables:**
   Ensure your `.env` file is configured with the necessary API gateway credentials:
   ```env
   LLM_GATEWAY_URL=http://localhost:9000
   ```

---

## 🖥️ Running the Application

The platform relies on a two-part microservice architecture: the LLM Gateway and the FastAPI Stylist Backend.

### 1. Start the LLM Gateway
Open a terminal, navigate to the gateway directory, and execute the run script:
```bash
cd ../llm_gatewayV2/
./run.sh
```

### 2. Start the Aura Atelier Backend
Open a second terminal, navigate to the assignment directory, and launch the FastAPI server:
```bash
cd session5_assignment/
python3 app.py
```

### 3. Access the Lookbook
Open your favorite modern web browser (Chrome/Safari recommended) and navigate to:
```
http://localhost:8105
```

---

## 📁 Project Structure

```text
session5_assignment/
├── app.py                 # FastAPI main application & API routing
├── agent_stylist.py       # Master AI Stylist Agent & MCP Client Orchestrator
├── mcp_server.py          # MCP Stdio Server & Multi-Tier Web Scraping Engine
├── requirements.txt       # Project dependencies
├── wardrobe.json          # Local persistent storage for user's saved jewellery
└── static/
    └── index.html         # High-fidelity luxury frontend lookbook & particle engine
```

---

## 🛡️ License & Acknowledgements
Built for Session 5 Advanced Multimodal & MCP Architecture. Designed with a commitment to architectural purity, visual excellence, and luxury editorial aesthetics.
