# ChatGPT RAG Injector 🚀

> Transparently inject context into ChatGPT conversations using man-in-the-middle proxy interception

![Status](https://img.shields.io/badge/status-working-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**What if ChatGPT could remember things? What if you could silently add context to every prompt?**

This project intercepts ChatGPT API requests in real-time and injects custom context before they reach OpenAI's servers. The user types normally, but ChatGPT receives enhanced prompts with your injected data.

Built during a Summer 2024 Research Internship after *many* iterations and approaches.

---

## 🎯 What This Does

```
User types: "What is AI?"
           ↓
    [Proxy Intercepts]
           ↓
ChatGPT receives: "You have to answer with my name AHMED WALI. 
                   Must include my name. Prompt: What is AI?"
           ↓
ChatGPT responds: "AHMED WALI, AI stands for Artificial Intelligence..."
```

**The magic?** The user never sees the injected context, but ChatGPT does! 🎭

---

## Use Cases

- **RAG Systems**: Inject retrieved documents into prompts
- **Persistent Memory**: Add conversation history across sessions  
- **Corporate Context**: Automatically include company guidelines
- **User Preferences**: Inject user-specific settings and info
- **Real-time Data**: Add live information from external APIs

---

## How It Works

```
┌─────────────┐
│   Browser   │ (PySide6/Qt WebEngine)
└──────┬──────┘
       │ All traffic goes through proxy
       ↓
┌─────────────┐
│  mitmproxy  │ ← Intercepts ChatGPT requests
└──────┬──────┘   Modifies prompts
       │          Forwards to ChatGPT
       ↓
┌─────────────┐
│  ChatGPT    │
│   Server    │
└─────────────┘
```

**Key Components**:
1. **Custom Browser** - Qt WebEngine configured to route through proxy
2. **mitmproxy Server** - Intercepts and modifies HTTPS traffic
3. **Request Logger** - Captures, modifies, and forwards ChatGPT API calls

---

## Quick Start

### Prerequisites
```bash
pip install PySide6 mitmproxy
```

### Run (Basic Version - WORKING)
```bash
cd src
python main.py
```

### Run (Secure Version - WIP, NOT WORKING)
```bash
cd src_secure
python main.py
# Note: This version has bugs and UI won't launch. See src_secure/README.md
```

### Test It
1. Browser window opens automatically (in basic version)
2. Navigate to ChatGPT (or it loads by default)
3. Send any message
4. Watch the terminal - you'll see the interception happen!
5. ChatGPT's response will include injected context

**Terminal Output**:
```
Starting proxy on port: 35347
Chrome DevTools on port: 35348
Waiting for proxy to start...
Proxy should be ready!
Request: POST https://chatgpt.com/backend-api/conversation
INTERCEPTED CHATGPT REQUEST!
Modified Prompt: You have to answer with my name AHMED WALI. Must include my name. Prompt: What is AI?
```

---

## Project Structure

```
.
├── src/                     # WORKING VERSION (Basic)
│   ├── main.py              # Entry point - starts proxy & browser
│   ├── mitmproxy_integration.py  # THE MAGIC - intercepts & modifies
│   └── ui.py                # Browser UI
├── src_secure/              # WIP VERSION (Secure but broken)
│   ├── main.py              # With proper SSL certificate handling
│   ├── mitmproxy_integration.py  # Same interception, better security
│   ├── ui.py                # Browser UI
│   ├── certificates/        # Generated CA certificates
│   └── README.md            # Details on why it's not working
├── README.md                # You are here
├── PROJECT_JOURNEY.md       # Full development story
├── SETUP.md                 # Quick setup guide
└── requirements.txt         # Dependencies
```

**Note**: The basic version (`src/`) is fully working and ready to use. The secure version (`src_secure/`) has proper SSL handling but currently has bugs preventing UI launch.

---

## Technical Details

### The Interception Code

The core logic (from `mitmproxy_integration.py`):

```python
class RequestResponseLogger:
    def request(self, flow):
        # Flexible matching - works with API changes!
        if "/conversation" in flow.request.url and "chatgpt.com" in flow.request.url:
            # Parse the request
            payload_json = json.loads(flow.request.content)
            original_prompt = payload_json['messages'][0]['content']['parts'][0]
            
            # INJECT YOUR CONTEXT HERE
            modified_prompt = f"[Your context here] Prompt: {original_prompt}"
            
            # Update and forward
            payload_json['messages'][0]['content']['parts'][0] = modified_prompt
            flow.request.content = json.dumps(payload_json).encode('utf-8')
```

### Key Features

**Dynamic Port Allocation** - No hardcoded ports, no conflicts  
**Flexible URL Matching** - Works with ChatGPT API changes  
**SSL Handling** - Accepts proxy certificates automatically  
**Clean Shutdown** - Proper thread & async management  
**Comprehensive Logging** - See everything that's happening  

---

## Customization

### Change the Injected Context

Edit `mitmproxy_integration.py`, line ~51:

```python
# Current (example):
modified_prompt = f"You have to answer with my name AHMED WALI. Must include my name. Prompt: {original_prompt}"

# Change to anything:
modified_prompt = f"Context: You are a pirate. Prompt: {original_prompt}"
modified_prompt = f"[DOCS]: {get_relevant_docs()} User asks: {original_prompt}"
modified_prompt = f"User preferences: {load_user_prefs()} Question: {original_prompt}"
```

### Add RAG (Retrieval Augmented Generation)

```python
def request(self, flow):
    if "/conversation" in flow.request.url and "chatgpt.com" in flow.request.url:
        payload_json = json.loads(flow.request.content)
        original_prompt = payload_json['messages'][0]['content']['parts'][0]
        
        # Retrieve relevant context
        relevant_docs = vector_search(original_prompt)  # Your vector DB here
        context = "\n".join(relevant_docs)
        
        # Inject it
        modified_prompt = f"Context: {context}\n\nUser Question: {original_prompt}"
        payload_json['messages'][0]['content']['parts'][0] = modified_prompt
        
        # Update request
        flow.request.content = json.dumps(payload_json).encode('utf-8')
```

---

## The Journey

This wasn't a straight path. Check out [PROJECT_JOURNEY.md](PROJECT_JOURNEY.md) for the full story, but here's the summary:

### Attempts Made:

1. **Qt Network Interception** - Can observe, can't modify
2. **Chrome DevTools Protocol (Network Domain)** - Read-only
3. **Chrome DevTools Protocol (Fetch Domain)** - Too complex, unstable
4. (DONE) **mitmproxy** - Finally worked!

### Key Hurdles Overcome:

- **URL Matching Hell**: Exact URL matching broke when ChatGPT changed endpoints
- **Port Conflicts**: Hardcoded ports caused issues
- **SSL Nightmares**: Certificate errors everywhere
- **Threading Chaos**: Async event loops and threads fighting each other
- **Debugging in the Dark**: Couldn't see what was being intercepted

**Result**: After "so many iterations" (my words), it works! 🎉

---

## TODO / Future Work

### Immediate
- [ ] Fix `src_secure/` UI launch issue (proper SSL version)
- [ ] Debug blocking issue in secure proxy initialization

### Short Term
- [ ] Replace hardcoded context with dynamic RAG retrieval
- [ ] Add vector database integration (Pinecone/Chroma)
- [ ] Implement semantic search for context selection
- [ ] Add configuration UI

### Medium Term
- [ ] Multi-user support with separate contexts
- [ ] Context relevance scoring
- [ ] Conversation history tracking
- [ ] REST API for external context sources

### Long Term
- [ ] Complete production SSL certificate handling (finish `src_secure/`)
- [ ] Support for Claude, Gemini, other LLMs
- [ ] Standalone proxy service (separate from browser)
- [ ] Analytics dashboard
- [ ] Browser extension version

---

## Limitations & Notes

### Basic Version (`src/`)
- **Works with ChatGPT web interface** (chat.openai.com / chatgpt.com)
- **Requires running proxy locally** (not for ChatGPT mobile apps)
- **SSL certificate warnings** - Uses `ssl_insecure=True` (not production-ready)
- **Currently hardcoded context** - Real RAG not yet implemented
- **Research project** - Works great for development/research

### Secure Version (`src_secure/`)
- **UI doesn't launch** - Known bug, needs debugging
- **Proper SSL handling** - Custom CA certificate generation
- **More production-ready approach** - When fixed
- **Took significant time to develop** - Shows proper security implementation
- **Contributions welcome** - Help fix the blocking issue!

---

## Research Context

**Built during**: Summer 2024 Research Internship  
**Institution**: LUMS (Lahore University of Management Sciences)  
**Course Context**: CS 438 Machine Learning  
**Status**: On hold (didn't get time after summer to continue)  

This was part of exploring RAG systems and how to augment LLMs with external context transparently.

---

## Contributing

This is a research project currently on hold, but if you want to:

- Fix bugs → Open an issue or PR
- Add RAG functionality → Please do! That's the next step
- Try different approaches → Share your findings
- Use it for your own research → Go for it!

---

## License

MIT License - Feel free to use, modify, and learn from this!

---

## Acknowledgments

- **mitmproxy** - The tool that made this possible
- **PySide6/Qt** - For the browser framework  
- **ChatGPT** - For being interceptable :)
- **Persistence** - For getting through "so many iterations"

---

## Questions?

Open an issue or check out [PROJECT_JOURNEY.md](PROJECT_JOURNEY.md) for the complete development story, including all the failures and learnings.

---

**"It took so many iterations, but we got there!"**

*Built with ❤️, frustration, and lots of CHAI :))*

---

## TL;DR

**What**: Inject context into ChatGPT prompts behind the scenes  
**How**: mitmproxy intercepts requests, modifies them, forwards to ChatGPT  
**Status**: Working! (But RAG part not implemented yet)  
**Run**: `cd proxy_done/now && python main.py`  
**Customize**: Edit line 51 in `mitmproxy_integration.py`  

Give it a ⭐ if this helps your research in whatever small way it can help!
