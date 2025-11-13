"""
MCP Research Assistant with Groq - Chainlit Frontend
A beautiful web UI for searching and analyzing academic papers
"""

import chainlit as cl
from dotenv import load_dotenv
from groq import Groq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack
import json
import os

load_dotenv()


class MCP_ChatBot:
    def __init__(self):
        self.exit_stack = AsyncExitStack()
        # Initialize Groq client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        
        self.groq_client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        self.available_tools = []
        self.available_prompts = []
        self.sessions = {}
        self.connected = False
    
    async def connect_to_server(self, server_name, server_config):
        """Connect to an MCP server"""
        try:
            server_params = StdioServerParameters(**server_config)
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            
            await session.initialize()
            
            # List available tools
            try:
                response = await session.list_tools()
                for tool in response.tools:
                    self.sessions[tool.name] = session
                    tool_def = {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema
                        }
                    }
                    self.available_tools.append(tool_def)
            except Exception as e:
                await cl.Message(content=f" Error loading tools: {e}").send()
            
            # List available prompts
            try:
                prompts_response = await session.list_prompts()
                if prompts_response and prompts_response.prompts:
                    for prompt in prompts_response.prompts:
                        self.sessions[prompt.name] = session
                        self.available_prompts.append({
                            "name": prompt.name,
                            "description": prompt.description,
                            "arguments": prompt.arguments
                        })
            except Exception as e:
                await cl.Message(content=f" Error loading prompts: {e}").send()
            
            # List available resources
            try:
                resources_response = await session.list_resources()
                if resources_response and resources_response.resources:
                    for resource in resources_response.resources:
                        resource_uri = str(resource.uri)
                        self.sessions[resource_uri] = session
            except Exception as e:
                await cl.Message(content=f" Error loading resources: {e}").send()
        
        except Exception as e:
            raise Exception(f"Error connecting to {server_name}: {e}")
    
    async def connect_to_servers(self):
        """Connect to all configured MCP servers"""
        try:
            with open("server_config.json", "r") as file:
                data = json.load(file)
                servers = data.get("mcpServers", {})
                for server_name, server_config in servers.items():
                    await self.connect_to_server(server_name, server_config)
            self.connected = True
        except Exception as e:
            raise Exception(f"Error loading server config: {e}")
    
    async def process_query(self, query):
        """Process a query using Groq API with tool calling"""
        messages = [{'role': 'user', 'content': query}]
        
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Create chat completion with Groq
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.available_tools if self.available_tools else None,
                tool_choice="auto",
                max_tokens=4096,
                temperature=0.7
            )
            
            assistant_message = response.choices[0].message
            
            # Add assistant message to conversation
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": assistant_message.tool_calls if hasattr(assistant_message, 'tool_calls') else None
            })
            
            # Check if assistant wants to use tools
            if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
                # Process each tool call
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # Send tool usage notification
                    await cl.Message(
                        content=f" **Using tool:** `{tool_name}`\n**Arguments:** `{tool_args}`",
                        author="System"
                    ).send()
                    
                    # Get the MCP session for this tool
                    session = self.sessions.get(tool_name)
                    if session:
                        try:
                            # Call the MCP tool
                            result = await session.call_tool(tool_name, arguments=tool_args)
                            
                            # Format result
                            if hasattr(result, 'content'):
                                if isinstance(result.content, list):
                                    tool_result = json.dumps([item.text if hasattr(item, 'text') else str(item) for item in result.content])
                                else:
                                    tool_result = str(result.content)
                            else:
                                tool_result = str(result)
                            
                            # Add tool result to messages
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": tool_result
                            })
                            
                        except Exception as e:
                            error_msg = f"Error calling tool: {str(e)}"
                            await cl.Message(content=f"{error_msg}", author="System").send()
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": error_msg
                            })
                
                # Continue the loop to let the model process tool results
                continue
            
            # No tool calls, we have the final response
            if assistant_message.content:
                return assistant_message.content
            else:
                return "No response generated."
        
        return "Maximum iterations reached. Please try again with a simpler query."
    
    async def list_prompts(self):
        """List all available prompts"""
        if not self.available_prompts:
            return "No prompts available."
        
        result = " **Available Prompts:**\n\n"
        for prompt in self.available_prompts:
            result += f"**{prompt['name']}**\n"
            result += f"_{prompt['description']}_\n"
            if prompt['arguments']:
                result += "Arguments:\n"
                for arg in prompt['arguments']:
                    arg_name = arg.name if hasattr(arg, 'name') else arg.get('name', '')
                    arg_required = " (required)" if (hasattr(arg, 'required') and arg.required) or arg.get('required', False) else " (optional)"
                    result += f"  - `{arg_name}`{arg_required}\n"
            result += "\n"
        
        return result
    
    async def execute_prompt(self, prompt_name, args):
        """Execute a prompt with the given arguments"""
        session = self.sessions.get(prompt_name)
        if not session:
            return f" Prompt '{prompt_name}' not found."
        
        try:
            await cl.Message(content=f"⚡ Executing prompt: **{prompt_name}**", author="System").send()
            result = await session.get_prompt(prompt_name, arguments=args)
            
            if result and result.messages:
                # Extract the prompt content
                prompt_content = result.messages[0].content
                
                # Handle different content formats
                if isinstance(prompt_content, str):
                    text = prompt_content
                elif hasattr(prompt_content, 'text'):
                    text = prompt_content.text
                else:
                    text = " ".join(
                        item.text if hasattr(item, 'text') else str(item) 
                        for item in prompt_content
                    )
                
                # Process the prompt with Groq
                response = await self.process_query(text)
                return response
        except Exception as e:
            return f" Error executing prompt: {e}"
    
    async def get_resource(self, resource_uri):
        """Fetch a resource by URI"""
        session = self.sessions.get(resource_uri)
        if not session:
            return f" Resource '{resource_uri}' not found."
        
        try:
            result = await session.read_resource(resource_uri)
            if result and result.contents:
                return result.contents[0].text
            return "No content available."
        except Exception as e:
            return f" Error fetching resource: {e}"
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


# Global chatbot instance
chatbot = None


@cl.on_chat_start
async def start():
    """Initialize chatbot when user starts a chat"""
    global chatbot
    
    # Send welcome message
    await cl.Message(
        content="#  MCP Research Assistant with Groq\n\n"
                "Welcome! I can help you search and analyze academic papers.\n\n"
                "**Commands:**\n"
                "- Type naturally to search papers\n"
                "- `@folders` - See all available topics\n"
                "- `@<topic>` - View papers on a specific topic\n"
                "- `/prompts` - List all prompt templates\n"
                "- `/prompt <name> arg1=value1` - Execute a prompt\n\n"
                "Connecting to MCP servers...",
        author="System"
    ).send()
    
    try:
        # Initialize chatbot
        chatbot = MCP_ChatBot()
        await chatbot.connect_to_servers()
        
        # Store in user session
        cl.user_session.set("chatbot", chatbot)
        
        await cl.Message(
            content="**Connected successfully!** You can now start searching for papers.",
            author="System"
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"**Failed to start:** {e}\n\n"
                    "Please check your configuration and try again.",
            author="System"
        ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    chatbot = cl.user_session.get("chatbot")
    
    if not chatbot:
        await cl.Message(
            content=" Chatbot not initialized. Please refresh the page.",
            author="System"
        ).send()
        return
    
    query = message.content.strip()
    
    if not query:
        return
    
    try:
        # Handle @resource syntax
        if query.startswith('@'):
            topic = query[1:].strip()
            if topic == "folders":
                resource_uri = "papers://folders"
            else:
                resource_uri = f"papers://{topic}"
            
            await cl.Message(
                content=f" Fetching resource: `{resource_uri}`",
                author="System"
            ).send()
            
            content = await chatbot.get_resource(resource_uri)
            await cl.Message(content=content).send()
            return
        
        # Handle /command syntax
        if query.startswith('/'):
            parts = query[1:].split()
            
            if len(parts) == 0:
                await cl.Message(
                    content=" Invalid command. Try `/prompts` or `/prompt <name>`"
                ).send()
                return
            
            command = parts[0]
            
            if command == "prompts":
                result = await chatbot.list_prompts()
                await cl.Message(content=result).send()
                return
                
            elif command == "prompt":
                if len(parts) < 2:
                    await cl.Message(
                        content="Usage: `/prompt <name> arg1=value1 arg2=value2`"
                    ).send()
                    return
                
                prompt_name = parts[1]
                args = {}
                
                # Parse key=value arguments
                for arg in parts[2:]:
                    if '=' in arg:
                        key, value = arg.split('=', 1)
                        try:
                            args[key] = int(value)
                        except ValueError:
                            args[key] = value
                
                response = await chatbot.execute_prompt(prompt_name, args)
                await cl.Message(content=response).send()
                return
            else:
                await cl.Message(
                    content=f" Unknown command: `{command}`"
                ).send()
                return
        
        # Natural language query
        # Show thinking indicator
        msg = cl.Message(content="")
        await msg.send()
        
        response = await chatbot.process_query(query)
        
        # Update message with response
        msg.content = response
        await msg.update()
        
    except Exception as e:
        await cl.Message(
            content=f" **Error:** {str(e)}",
            author="System"
        ).send()


@cl.on_chat_end
async def end():
    """Cleanup when chat ends"""
    chatbot = cl.user_session.get("chatbot")
    if chatbot:
        await chatbot.cleanup()