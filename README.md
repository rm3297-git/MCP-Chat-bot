MCP Research Assistant with Groq AI

This project is a simple research assistant that uses the Model Context Protocol and Groq AI to search and organize academic papers from arXiv.

What this project does

It lets you
search papers by topic
store them locally
browse stored topics
ask questions using the Groq LLM
run tools such as search and view stored papers
use prompt templates for research tasks

Key files

research_server.py
mcp_chatbot.py
server_config.json
requirements.txt
env template
papers folder for saved topics

How to set up

Install Python version 3.10 or higher
Install the required packages
Create a Groq API key at console dot groq dot com
Copy env template to env
Add your Groq API key inside the env file
Run the chatbot

Example setup

pip install -r requirements.txt
python mcp_chatbot.py

Basic usage

Example queries

Find papers about neural networks
Show folders using at folders
Open a stored topic using at followed by the topic name
List all prompt templates using slash prompts
Use a specific prompt template using slash prompt

Features included

Tool calling
Resource browsing
Prompt templates
Local paper storage
Fast Groq model responses

Supported Groq models

llama 3 point 3 seventy b versatile
llama 3 point 1 seventy b versatile
mixtral eight by seven b
gemma two nine b

Project structure

mcp research assistant folder
research server
chatbot client
config file
papers folder for topics and JSON files

Requirements

Python version 3.10 or higher
Groq API key
Internet connection for arXiv searches

How it works

Your question is sent to the Groq model
The model decides whether to call a tool
Tools fetch or read data
The server returns results back to Groq
Groq produces a final answer

Quick example

You
Find papers about deep learning

Assistant automatically calls the search tool and saves papers
You can then type at deep learning to view the folder

Summary

This project is a compact and fast research assistant
It uses Groq for speed
It uses MCP for structured tools and resources
It stores papers locally for easy browsing
