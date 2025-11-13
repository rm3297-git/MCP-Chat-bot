# MCP Research Assistant with Groq AI

A comprehensive AI application using the Model Context Protocol (MCP) for searching and managing academic papers from arXiv, powered by **Groq's fast LLM inference**.

## 🚀 Why Groq?

This application uses Groq instead of Anthropic Claude for several advantages:
- ⚡ **Ultra-fast inference**: Groq's LPU™ provides incredibly fast response times
- 💰 **Cost-effective**: Generous free tier and competitive pricing
- 🔓 **Multiple models**: Support for Llama 3.3, Mixtral, and other open models
- 🌐 **Easy API**: Simple REST API compatible with OpenAI format

## 📦 What's Included

### Core Files
- `research_server.py` - MCP server with tools, resources, and prompts
- `mcp_chatbot.py` - Groq-powered interactive client
- `server_config.json` - Server connection configuration
- `requirements.txt` - Python dependencies
- `.env.template` - Environment variable template
- `test_server.py` - Automated test suite

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.9+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Get Groq API key
# Visit: https://console.groq.com/keys
# Sign up (free) and create an API key

# 3. Configure
cp .env.template .env
# Edit .env and add: GROQ_API_KEY=your_key_here

# 4. Run
python mcp_chatbot.py
```

### First Commands

```
💬 You: Find papers about neural networks
💬 You: @folders
💬 You: @neural_networks
💬 You: /prompts
💬 You: /prompt generate_search_prompt topic=ai num_papers=5
```

## 🎯 Features

### MCP Primitives

**Tools** - Functions Groq can call:
```python
@mcp.tool()
def search_papers(topic: str, max_results: int = 5):
    """Search arXiv and store papers"""
```

**Resources** - Read-only data via URI:
```python
@mcp.resource("papers://folders")
def get_available_folders():
    """List all topic folders"""
```

**Prompts** - Pre-configured templates:
```python
@mcp.prompt()
def generate_search_prompt(topic: str, num_papers: int = 5):
    """Battle-tested research prompt"""
```

### Interaction Modes

1. **Natural Language**: Groq decides when to use tools
   ```
   Find papers about quantum computing
   ```

2. **Resource Access**: Use @ syntax
   ```
   @folders
   @quantum_computing
   ```

3. **Prompt Templates**: Use / syntax
   ```
   /prompts
   /prompt generate_search_prompt topic=ai num_papers=10
   ```

## 📊 Command Reference

| Command | Example | Purpose |
|---------|---------|---------|
| Natural | `Find papers on AI` | Groq decides actions |
| @folders | `@folders` | List topics |
| @topic | `@quantum_computing` | View papers |
| /prompts | `/prompts` | List templates |
| /prompt | `/prompt <n> arg=val` | Execute template |
| quit | `quit` | Exit |

## 💡 Usage Examples

### Example 1: Search and Analyze
```
💬 You: Search for papers about transformers

🔧 Using tool: search_papers
   Arguments: {'topic': 'transformers', 'max_results': 5}

🤖 Assistant:
I found 5 papers about transformers:

1. "Attention Is All You Need" (2017)
   - Introduced transformer architecture
   - Authors: Vaswani et al.
   [Full analysis provided]
```

### Example 2: Browse Topics
```
💬 You: @folders

# Available Topics

- transformers
  Use @transformers to access papers in that topic.
- quantum_computing
  Use @quantum_computing to access papers in that topic.
```

### Example 3: Comprehensive Research
```
💬 You: /prompt generate_search_prompt topic=deep_learning num_papers=10

⚡ Executing prompt: generate_search_prompt

🤖 Assistant:
[Searches for 10 papers]
[Provides comprehensive analysis]
[Identifies trends and gaps]
[Highlights key papers]
```

## 🏗️ Architecture

```
User Query
    ↓
Groq AI (fast inference)
    ↓
Tool Calling Decision
    ↓
MCP Server (executes tools)
    ↓
Local Storage (papers/)
    ↓
Formatted Response
    ↓
User
```

## 🔧 Configuration

### Groq Models

Edit in `mcp_chatbot.py`:
```python
# Choose your model
self.model = "llama-3.3-70b-versatile"  # Default (fast & good)
# self.model = "llama-3.1-70b-versatile"  # Alternative
# self.model = "mixtral-8x7b-32768"       # Long context
# self.model = "gemma2-9b-it"             # Lightweight
```

### Available Groq Models
- `llama-3.3-70b-versatile` - Best balance (recommended)
- `llama-3.1-70b-versatile` - Stable alternative  
- `mixtral-8x7b-32768` - 32K context window
- `gemma2-9b-it` - Lightweight and fast

## 🎓 How MCP Works

### 1. Tools (AI-Callable Functions)
The server defines tools that Groq can automatically call:
```python
@mcp.tool()
def search_papers(topic, max_results):
    # Searches arXiv
    # Stores results
    # Returns paper IDs
```

Groq sees the tool definition and calls it when needed.

### 2. Resources (URI-Based Data)
Data accessible via custom URIs:
```python
@mcp.resource("papers://folders")
def get_folders():
    # Returns list of topics
```

Access with `@folders` command.

### 3. Prompts (Templates)
Pre-configured prompts with arguments:
```python
@mcp.prompt()
def generate_search_prompt(topic, num_papers=5):
    # Returns filled template
```

Execute with `/prompt` command.

## 🛠️ Extending the Application

### Add a Custom Tool
```python
@mcp.tool()
def analyze_citations(paper_id: str) -> dict:
    """Analyze citations for a paper"""
    # Implementation
    return {"citations": 42, "h_index": 10}
```

### Add a Custom Resource
```python
@mcp.resource("stats://overview")
def get_statistics() -> str:
    """Get paper statistics"""
    return "Total papers: 100\nTopics: 5"
```

### Add a Custom Prompt
```python
@mcp.prompt()
def compare_papers_prompt(paper1: str, paper2: str) -> str:
    """Compare two papers"""
    return f"Compare these papers: {paper1} vs {paper2}"
```

## 🐛 Troubleshooting

### API Key Issues
```bash
# Error: GROQ_API_KEY not found
# Solution:
cp .env.template .env
# Edit .env and add your key
```

### Rate Limits
Groq has generous free limits. If exceeded:
- Wait a moment
- Check usage at console.groq.com
- Consider upgrading plan

### Tool Not Called
Make your query more explicit:
```
# Instead of: "transformers"
# Try: "Use search_papers to find papers about transformers"
```

### Model Errors
Try a different model:
```python
self.model = "llama-3.1-70b-versatile"
```

## 📈 Performance Comparison

| Feature | Groq | Anthropic Claude |
|---------|------|------------------|
| **Speed** | ⚡⚡⚡ 200-500 tok/s | ⚡⚡ 50-100 tok/s |
| **Latency** | < 1 sec | 2-5 sec |
| **Cost** | 💰 Low | 💰💰 Higher |
| **Free Tier** | ✅ Generous | ✅ Limited |
| **Tool Calling** | ✅ Yes | ✅ Yes |
| **Max Context** | 32K-128K | 200K |
| **Quality** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Verdict**: Groq is perfect for speed-critical applications. Claude is better for maximum quality.

## 🔒 Security

- ✅ API keys in `.env` (gitignored)
- ✅ No hardcoded secrets
- ✅ Local storage only
- ✅ Read-only resources
- ✅ Input validation

## 📝 Project Structure

```
mcp-research-assistant/
├── research_server.py      # MCP server
├── mcp_chatbot.py          # Groq client
├── server_config.json      # Config
├── requirements.txt        # Dependencies
├── .env.template          # API key template
├── test_server.py         # Tests
└── papers/                # Storage
    └── {topic}/
        └── papers_info.json
```

## 🎉 What Makes This Special

1. ⚡ **Lightning Fast**: Groq's speed makes interaction fluid
2. 🎯 **Complete MCP**: All three primitives implemented
3. 📚 **Real Use Case**: Practical research tool
4. 🔄 **Multiple Modes**: Natural language, resources, prompts
5. 💰 **Cost Effective**: Free tier is very generous
6. 🛠️ **Extensible**: Easy to add tools/resources/prompts

## 🔗 Resources

### Official Links
- **Groq Console**: https://console.groq.com
- **Groq Documentation**: https://console.groq.com/docs
- **MCP Protocol**: https://modelcontextprotocol.io
- **arXiv API**: https://arxiv.org/help/api

### Get Started
1. Create Groq account (free)
2. Generate API key
3. Follow Quick Start above
4. Start researching!

## 🤝 Contributing

Ideas for contribution:
- Add streaming responses
- Implement more Groq models
- Add vector search for papers
- Create web interface
- Add more research databases
- Improve prompt templates

## 📄 License

MIT License - Free to use and modify

## 🙏 Acknowledgments

- **Groq** - Ultra-fast LLM inference platform
- **Anthropic** - MCP protocol specification
- **arXiv** - Open access research papers
- **Meta** - Llama models
- **Community** - MCP developers

---

**Built with ⚡ Groq AI + 🔬 MCP + 📚 arXiv**

*Get started in 5 minutes. Questions? Check the code comments or open an issue!*

## 🚦 Getting Started Checklist

- [ ] Install Python 3.9+
- [ ] Run `pip install -r requirements.txt`
- [ ] Sign up at console.groq.com
- [ ] Get API key
- [ ] Copy .env.template to .env
- [ ] Add GROQ_API_KEY to .env
- [ ] Run `python mcp_chatbot.py`
- [ ] Try: "Find papers about neural networks"
- [ ] Try: `@folders`
- [ ] Try: `/prompts`
- [ ] Start researching! 🎉
