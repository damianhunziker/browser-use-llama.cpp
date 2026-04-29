# Browser-Use MCP - Local AI Browser Automation with Vision

**Browser automation powered by local AI models in under 5 minutes.** No cloud API keys, no recurring costs, runs entirely on your hardware.

## Why This Setup?

- **🚀 Install in Minutes** - Just start a llama.cpp server and configure your MCP client
- **💰 100% Free & Local** - No API costs, all processing on your machine
- **🖼️ Vision Support** - AI sees screenshots and understands web pages
- **⚡ < 15GB VRAM** - Runs on consumer GPUs like RTX 4070/3080 or AMD 7800 XT
- **🔒 Privacy First** - All data stays local, nothing leaves your network

This setup uses browser-use with a local llama.cpp server providing OpenAI-compatible API for the AI agent. The agent can navigate websites, take screenshots, analyze visual content, and complete complex multi-step tasks autonomously.

---

## Quick Start

### 1. Start llama.cpp Server

```bash
toolbox enter llama-rocm7-nightlies

llama-server -m /path/to/model/Qwen3.5-9B-Q4_K_M.gguf \
  --mmproj /path/to/mmproj/mmproj-Qwen3.5-9B-BF16.gguf \
  --host 0.0.0.0 --port 8080 \
  --temp 0.6 --top-p 0.95 --top-k 20 \
  --flash-attn on --no-mmap --mlock
```

**⚠️ Firewall Required:** Open port 8080 (TCP) on your home server's firewall so the MCP client can reach the llama.cpp server from other machines on your network.

**📍 Server IP Address:** The address `192.168.43.136` is your home server's local IP (found via `ip addr show` or `ifconfig` on that server). Replace it in the MCP config with your actual server IP.

**🏠 Same Machine?** If llama.cpp runs on the same computer as your MCP client, use `127.0.0.1` instead of `192.168.43.136` in the `OPENAI_BASE_URL`.

**Requirements:**
- llama.cpp with multimodal support (ROCm build for AMD GPUs)
- Vision model with mmproj file (Qwen2.5-VL, Qwen3-VL, etc.)
- Model quantization: Q4_K_M recommended for 9B models (~6GB VRAM)

### 2. Configure MCP Client (Roo Cline)

Add to `~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`:

```json
"browser-use-2": {
  "command": "uvx",
  "args": ["--from", "browser-use[cli]", "browser-use", "--mcp"],
  "env": {
    "OPENAI_API_KEY": "ollama",
    "OPENAI_BASE_URL": "http://192.168.43.136:8080/v1",
    "BROWSER_USE_LLM_MODEL": "qwen3.5:9b",
    "BROWSER_USE_HEADLESS": "false",
    "no_proxy": "localhost,127.0.0.1,192.168.43.136"
  },
  "alwaysAllow": [
    "browser_navigate", "browser_get_state", "retry_with_browser_use_agent",
    "browser_screenshot", "browser_click", "browser_type", "browser_scroll",
    "browser_go_back", "browser_list_tabs", "browser_switch_tab",
    "browser_close_tab", "browser_get_html", "browser_extract_content",
    "browser_close_all", "browser_close_session", "browser_list_sessions"
  ],
  "timeout": 300
}
```

### 3. Use Vision Tools

```json
{
  "tool": "retry_with_browser_use_agent",
  "arguments": {
    "task": "Go to google.ch and describe what you see in detail",
    "max_steps": 15,
    "use_vision": true
  }
}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ROO/Claude Code                         │
│                  (Orchestrator Layer)                      │
└─────────────────────────┬─────────────────────────────────┘
                          │ MCP Protocol (stdio)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              browser-use MCP Server                       │
│          (via uvx browser-use --mcp)                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         retry_with_browser_use_agent                │    │
│  │  ┌─────────────────────────────────────────────────┐│    │
│  │  │            ChatOpenAI (Vision)                 ││    │
│  │  │  • model: qwen3.5:9b                            ││    │
│  │  │  • base_url: http://192.168.43.136:8080/v1     ││    │
│  │  │  • vision: true                                 ││    │
│  │  └─────────────────────────────────────────────────┘│    │
│  │                         │                           │    │
│  │                         ▼                           │    │
│  │  ┌─────────────────────────────────────────────────┐│    │
│  │  │              Agent (autonomous)                 ││    │
│  │  │  • takes screenshots internally               ││    │
│  │  │  • sends to LLM for vision analysis            ││    │
│  │  │  • receives analysis, continues task          ││    │
│  │  └─────────────────────────────────────────────────┘│    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Available MCP Tools

### Vision-Capable Tools

| Tool | Vision? | Use Case |
|------|---------|----------|
| `retry_with_browser_use_agent` | ✅ | Full autonomous tasks with vision analysis |
| `browser_get_state` | ❌ | DOM inspection only (returns JSON) |
| `browser_screenshot` | ❌ | Capture image (no LLM analysis) |

### Direct Browser Control

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Navigate to URL |
| `browser_click` | Click element by index |
| `browser_type` | Type into input |
| `browser_scroll` | Scroll up/down |
| `browser_go_back` | Go back |
| `browser_list_tabs` | List tabs |
| `browser_switch_tab` | Switch tab |
| `browser_close_tab` | Close tab |
| `browser_get_html` | Get raw HTML |
| `browser_extract_content` | Extract structured content |

### Session Management

| Tool | Purpose |
|------|---------|
| `browser_list_sessions` | List active sessions |
| `browser_close_session` | Close specific session |
| `browser_close_all` | Close all sessions |

---

## Key Concept: Vision vs Non-Vision Tools

### `browser_get_state` (NO VISION - Fast)
- Returns DOM as JSON
- Returns screenshot as ImageContent to MCP client
- **Screenshot is displayed to you, NOT analyzed by AI**
- Response time: < 1 second

### `retry_with_browser_use_agent` (WITH VISION - Powerful)
- Creates Agent with ChatOpenAI that has vision enabled
- Agent takes screenshot internally
- Agent sends screenshot to **your llama.cpp server**
- Agent receives vision analysis back
- Response time: 10-60 seconds (depends on model)

**Use vision tools when you need AI to "see" and understand web pages.**

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | API key (any dummy value for llama.cpp) |
| `OPENAI_BASE_URL` | llama.cpp server endpoint (http://IP:PORT/v1) |
| `BROWSER_USE_LLM_MODEL` | Model name (e.g., qwen3.5:9b) |
| `BROWSER_USE_HEADLESS` | Browser visibility (false = show browser) |
| `no_proxy` | Bypass proxy for local server communication |

---

## Research MCP Integration

Combine with these tools for comprehensive research workflows:

| Tool | Purpose |
|------|---------|
| `perplexity_search/ask/research` | Web research with reasoning |
| `brave_web_search` | Find relevant URLs |
| `qdrant_url_reader` | Extract content from URLs |
| `md_read_tool` | Read specific content sections |

---

## Testing

### Quick Test (no vision):
```json
{
  "tool": "browser_navigate",
  "arguments": {"url": "https://google.ch"}
}
```

### Vision Test (AI analyzes the page):
```json
{
  "tool": "retry_with_browser_use_agent",
  "arguments": {
    "task": "Go to google.ch, search for 'browser automation', and tell me the first 3 results",
    "max_steps": 15,
    "use_vision": true
  }
}
```

---

## Troubleshooting

### "Request timed out" with retry_with_browser_use_agent
- **Cause**: Vision processing takes time with local models
- **Solution**: Increase timeout to 300+ seconds in MCP config

### Screenshots not analyzed by AI
- **Cause**: Using `browser_get_state` which returns screenshot but doesn't send to LLM
- **Solution**: Use `retry_with_browser_use_agent` for vision tasks

### Ollama doesn't work with vision
- **Cause**: Ollama may not properly handle vision with multimodal models
- **Solution**: Use **llama.cpp** directly with `--mmproj` multimodal projection file

### Proxy interference
- **Cause**: System proxy blocks local llama.cpp communication
- **Solution**: Set `no_proxy` to include your server IP (e.g., `192.168.43.136,localhost,127.0.0.1`)

---

## File Overview

| File | Description |
|------|-------------|
| `browser_use_working.py` | Direct Python script using browser-use Agent |
| `browser_use_mcp_server.py` | Custom MCP server wrapper (legacy) |
| `browser_use_mcp_config.json` | Alternative MCP config format |
| `README.md` | This documentation |