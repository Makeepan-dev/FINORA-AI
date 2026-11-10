# Zero-Cost AI Provider Setup Guide

FINORA is architected to guarantee **zero API spend** (`MAX_API_SPEND_USD=0`).
It supports official free-tier developer endpoints as well as an integrated 100% offline deterministic reasoning engine.

## Supported Providers

### 1. Deterministic Engine (Default - Zero API Key Required)
- **Status:** Active out of the box.
- Requires no external network access, API keys, or credit cards.
- Directly ingests deterministic analytics from the backend and produces mathematically consistent conclusions.

### 2. Google Gemini API (Free Tier)
- Model: `gemini-1.5-flash`
- Get a free key: [https://aistudio.google.com/](https://aistudio.google.com/)
- Set in `.env`:
  ```env
  AI_PRIMARY_PROVIDER=gemini
  GEMINI_API_KEY=your_gemini_api_key
  ```

### 3. Groq Developer Access (Free Tier)
- Model: `llama-3.1-8b-instant`
- Get a free key: [https://console.groq.com/](https://console.groq.com/)
- Set in `.env`:
  ```env
  AI_PRIMARY_PROVIDER=groq
  GROQ_API_KEY=your_groq_api_key
  ```

### 4. OpenRouter (Free Models Only)
- Model: `meta-llama/llama-3.2-3b-instruct:free`
- Set in `.env`:
  ```env
  AI_PRIMARY_PROVIDER=openrouter
  OPENROUTER_API_KEY=your_openrouter_api_key
  ```

## Security Enforcement
The application strictly enforces:
```env
ALLOW_PAID_MODELS=false
ALLOW_AUTO_RECHARGE=false
MAX_API_SPEND_USD=0
```
If an external API quota is exceeded or an invalid key is supplied, the system automatically falls back to the deterministic engine without interrupting the user.
