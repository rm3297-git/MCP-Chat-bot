# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                      (Command Line Chat)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MCP ChatBot Client                          │
│                     (mcp_chatbot.py)                             │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Command Parser                                           │   │
│  │ • Natural Language → Claude API                          │   │
│  │ • @{resource} → Resource Fetch                           │   │
│  │ • /{command} → Command Execution                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Session Manager                                          │   │
│  │ • Tool Sessions                                          │   │
│  │ • Resource Sessions                                      │   │
│  │ • Prompt Sessions                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────┬───────────────────────────┬──────────────────────────┬───┘
      │                           │                          │
      │ MCP Protocol              │ Anthropic API            │
      ▼                           ▼                          ▼
┌──────────────┐          ┌──────────────┐         ┌─────────────┐
│   MCP Server │          │    Claude    │         │   Storage   │
│  (research)  │          │     API      │         │   (papers)  │
└──────────────┘          └──────────────┘         └─────────────┘
```

## Component Breakdown

### 1. User Interface Layer
**Location**: Command Line

**Responsibilities**:
- Accept user input
- Display results
- Handle quit/exit commands

**Interaction**:
```
User Input → ChatBot Client → Process → Display Output
```

### 2. MCP ChatBot Client
**File**: `mcp_chatbot.py`

**Components**:

#### A. Command Parser
```python
if query.startswith('@'):
    # Resource access
    resource_uri = parse_resource(query)
    content = await get_resource(resource_uri)
    
elif query.startswith('/'):
    # Command execution
    command, args = parse_command(query)
    await execute_command(command, args)
    
else:
    # Natural language
    response = await process_query(query)
```

#### B. Session Manager
```python
self.sessions = {
    "tool_name": session_object,
    "resource_uri": session_object,
    "prompt_name": session_object
}
```

**Key Methods**:
- `connect_to_servers()` - Initialize connections
- `process_query()` - Handle Claude API interaction
- `execute_prompt()` - Run prompt templates
- `get_resource()` - Fetch resource data

### 3. MCP Server
**File**: `research_server.py`

**Architecture**:
```
FastMCP Server
├── Tools (@mcp.tool)
│   └── search_papers(topic, max_results)
│
├── Resources (@mcp.resource)
│   ├── papers://folders
│   └── papers://{topic}
│
└── Prompts (@mcp.prompt)
    └── generate_search_prompt(topic, num_papers)
```

**Data Flow**:
```
Tool Call → arXiv API → Process Results → Store JSON → Return IDs
Resource Request → Read JSON → Format Markdown → Return Content
Prompt Request → Build Template → Insert Args → Return Prompt
```

### 4. Storage Layer
**Location**: `papers/` directory

**Structure**:
```
papers/
└── {topic_name}/
    └── papers_info.json
        {
          "entry_id": {
            "title": "...",
            "authors": [...],
            "summary": "...",
            "pdf_url": "...",
            "published": "..."
          }
        }
```

## Data Flow Diagrams

### Flow 1: Natural Language Query
```
┌──────┐    "Find papers"    ┌──────────┐
│ User │───────────────────→ │ ChatBot  │
└──────┘                      └─────┬────┘
                                    │
                              Build │ messages
                                    ▼
                             ┌─────────────┐
                             │ Claude API  │
                             │  (decides   │
                             │   to use    │
                             │   tool)     │
                             └──────┬──────┘
                                    │ tool_use
                                    ▼
                             ┌─────────────┐
                             │ MCP Server  │
                             │ (search_    │
                             │  papers)    │
                             └──────┬──────┘
                                    │
                                    ▼
                             ┌─────────────┐
                             │ arXiv API   │
                             └──────┬──────┘
                                    │ results
                                    ▼
                             ┌─────────────┐
                             │   Storage   │
                             └──────┬──────┘
                                    │ success
                                    ▼
                             ┌─────────────┐
                             │ ChatBot     │
                             │ (format &   │
                             │  display)   │
                             └──────┬──────┘
                                    │
                                    ▼
                                ┌──────┐
                                │ User │
                                └──────┘
```

### Flow 2: Resource Access (@command)
```
┌──────┐    "@folders"    ┌──────────┐
│ User │─────────────────→│ ChatBot  │
└──────┘                   └─────┬────┘
                                 │
                           Parse │ URI
                                 │
                                 ▼
                          ┌─────────────┐
                          │ MCP Server  │
                          │ (resource:  │
                          │  papers://  │
                          │  folders)   │
                          └──────┬──────┘
                                 │
                           Read  │ directory
                                 │
                                 ▼
                          ┌─────────────┐
                          │  Storage    │
                          └──────┬──────┘
                                 │ folder list
                                 ▼
                          ┌─────────────┐
                          │  ChatBot    │
                          │  (display)  │
                          └──────┬──────┘
                                 │
                                 ▼
                             ┌──────┐
                             │ User │
                             └──────┘
```

### Flow 3: Prompt Execution (/command)
```
┌──────┐  "/prompt..."  ┌──────────┐
│ User │───────────────→│ ChatBot  │
└──────┘                 └─────┬────┘
                               │
                         Parse │ command
                               │ & args
                               ▼
                        ┌─────────────┐
                        │ MCP Server  │
                        │ (get_prompt)│
                        └──────┬──────┘
                               │
                         Build │ template
                               │
                               ▼
                        ┌─────────────┐
                        │  Template   │
                        │  populated  │
                        │  with args  │
                        └──────┬──────┘
                               │ full prompt
                               ▼
                        ┌─────────────┐
                        │ Claude API  │
                        │ (processes  │
                        │  prompt &   │
                        │  uses tools)│
                        └──────┬──────┘
                               │
                               ▼
                        ┌─────────────┐
                        │  ChatBot    │
                        │  (display   │
                        │   result)   │
                        └──────┬──────┘
                               │
                               ▼
                           ┌──────┐
                           │ User │
                           └──────┘
```

## Protocol Details

### MCP Protocol Messages

#### Tool Call
```json
{
  "type": "tool_use",
  "id": "toolu_xxx",
  "name": "search_papers",
  "input": {
    "topic": "machine learning",
    "max_results": 5
  }
}
```

#### Tool Response
```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_xxx",
  "content": ["paper_id_1", "paper_id_2", ...]
}
```

#### Resource Request
```python
await session.read_resource("papers://folders")
```

#### Resource Response
```python
{
  "contents": [{
    "uri": "papers://folders",
    "mimeType": "text/plain",
    "text": "# Available Topics\n- topic1\n- topic2"
  }]
}
```

#### Prompt Request
```python
await session.get_prompt(
    "generate_search_prompt",
    arguments={"topic": "AI", "num_papers": 5}
)
```

#### Prompt Response
```python
{
  "messages": [{
    "role": "user",
    "content": "Search for 5 papers about AI..."
  }]
}
```

## Async Architecture

### AsyncExitStack Pattern
```python
self.exit_stack = AsyncExitStack()

# Context enters
transport = await self.exit_stack.enter_async_context(
    stdio_client(params)
)

session = await self.exit_stack.enter_async_context(
    ClientSession(read, write)
)

# Automatic cleanup on exit
await self.exit_stack.aclose()
```

### Event Loop Management
```python
# Main async loop
async def main():
    chatbot = MCP_ChatBot()
    try:
        await chatbot.connect_to_servers()
        await chatbot.chat_loop()
    finally:
        await chatbot.cleanup()

# Entry point
if __name__ == "__main__":
    asyncio.run(main())
```

## Error Handling Strategy

### Server-Side
```python
@mcp.resource("papers://{topic}")
def get_topic_papers(topic: str) -> str:
    if not os.path.exists(papers_file):
        return "# No papers found for topic: {topic}\n\n..."
    
    try:
        with open(papers_file, 'r') as f:
            data = json.load(f)
        return format_papers(data)
    except json.JSONDecodeError:
        return "# Error reading papers data..."
```

### Client-Side
```python
try:
    result = await session.call_tool(name, arguments)
    messages.append({
        'role': 'user',
        'content': [{
            'type': 'tool_result',
            'tool_use_id': content.id,
            'content': result.content
        }]
    })
except Exception as e:
    messages.append({
        'role': 'user',
        'content': [{
            'type': 'tool_result',
            'tool_use_id': content.id,
            'content': f"Error: {str(e)}",
            'is_error': True
        }]
    })
```

## Security Considerations

### 1. API Key Management
```
.env file (gitignored)
    ↓
Environment Variables
    ↓
Anthropic Client
```

### 2. Input Validation
- Command parsing validates @ and / prefixes
- Prompt arguments are validated by MCP server
- File paths use os.path.join to prevent traversal

### 3. Resource Access Control
- Resources are read-only
- Limited to papers/ directory
- No arbitrary file access

## Performance Optimization

### 1. Session Reuse
```python
# Store sessions by name/URI
self.sessions[tool.name] = session
self.sessions[resource_uri] = session

# Reuse for subsequent calls
session = self.sessions.get(tool_name)
```

### 2. Async Operations
- All I/O operations are async
- Multiple servers can be queried concurrently
- Non-blocking user interface

### 3. Caching Strategy
- Papers stored locally after search
- Resource access reads from cache
- No redundant API calls

## Scalability

### Current Limitations
- Single-user design
- Local file storage
- Synchronous chat loop

### Scaling Options
1. **Multi-User**:
   - Add user authentication
   - Separate storage per user
   - Session management

2. **Distributed Storage**:
   - Replace JSON files with database
   - Use Redis for caching
   - Cloud storage for papers

3. **Horizontal Scaling**:
   - Message queue for requests
   - Multiple server instances
   - Load balancer

## Extension Points

### Adding New Tools
```python
@mcp.tool()
def new_tool(arg1: str, arg2: int) -> str:
    """Tool description"""
    # Implementation
    return result
```

### Adding New Resources
```python
@mcp.resource("custom://{param}")
def new_resource(param: str) -> str:
    """Resource description"""
    # Implementation
    return content
```

### Adding New Prompts
```python
@mcp.prompt()
def new_prompt(arg1: str, arg2: int = 5) -> str:
    """Prompt description"""
    return f"Template with {arg1} and {arg2}"
```

## Design Patterns Used

1. **Factory Pattern**: Server creation via config
2. **Observer Pattern**: Tool use → Response cycle
3. **Command Pattern**: @ and / command parsing
4. **Singleton Pattern**: Single chatbot instance
5. **Strategy Pattern**: Different query handling strategies
6. **Template Pattern**: Prompt templates

## Technology Stack

```
┌─────────────────────────────────────┐
│         Application Layer            │
│  • Python 3.9+                      │
│  • asyncio                          │
│  • nest_asyncio                     │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│         Protocol Layer              │
│  • MCP (Model Context Protocol)    │
│  • stdio transport                  │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│         Integration Layer            │
│  • Anthropic API                    │
│  • arXiv API                        │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│         Storage Layer               │
│  • JSON files                       │
│  • Local filesystem                 │
└─────────────────────────────────────┘
```

## Future Enhancements

1. **Web Interface**: Replace CLI with web UI
2. **Vector Search**: Semantic paper search
3. **Paper Analysis**: Automatic summarization
4. **Citation Network**: Track paper relationships
5. **Collaborative Features**: Share research with team
6. **Advanced Filtering**: By date, author, venue
7. **Export Options**: PDF, markdown, BibTeX
8. **Notification System**: New papers alerts
9. **Integration**: Zotero, Mendeley, etc.
10. **Analytics**: Research trend analysis
