import arxiv
import json
import os
from typing import List
from mcp.server.fastmcp import FastMCP

PAPER_DIR = "papers"

# Initialize FastMCP server
mcp = FastMCP("research")


@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic and store their information.
    
    Args:
        topic: The topic to search for
        max_results: Maximum number of results to retrieve (default: 5)
    
    Returns:
        List of paper IDs found in the search
    """
    # Use arxiv to find the papers
    client = arxiv.Client()
    
    # Search for the most relevant articles matching the queried topic
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    papers = client.results(search)
    
    # Store paper information
    paper_ids = []
    
    # Create directory for this topic if it doesn't exist
    topic_dir = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(topic_dir, exist_ok=True)
    
    # Collect paper data
    papers_data = []
    for paper in papers:
        paper_info = {
            "title": paper.title,
            "authors": [author.name for author in paper.authors],
            "summary": paper.summary,
            "pdf_url": paper.pdf_url,
            "published": paper.published.isoformat(),
            "entry_id": paper.entry_id
        }
        papers_data.append(paper_info)
        paper_ids.append(paper.entry_id)
    
    # Save papers info to JSON file
    papers_file = os.path.join(topic_dir, "papers_info.json")
    with open(papers_file, 'w') as f:
        json.dump(papers_data, f, indent=2)
    
    return paper_ids


@mcp.resource("papers://folders")
def get_available_folders() -> str:
    """
    List all available topic folders in the papers directory.
    
    This resource provides a simple list of all available topic folders.
    """
    folders = []
    
    # Get all topic directories
    if os.path.exists(PAPER_DIR):
        for topic_dir in os.listdir(PAPER_DIR):
            topic_path = os.path.join(PAPER_DIR, topic_dir)
            if os.path.isdir(topic_path):
                papers_file = os.path.join(topic_path, "papers_info.json")
                if os.path.exists(papers_file):
                    folders.append(topic_dir)
    
    # Create a simple markdown list
    content = "# Available Topics\n\n"
    if folders:
        for folder in folders:
            content += f"- {folder}\n"
            content += f"  Use @{folder} to access papers in that topic.\n"
    else:
        content += "No topics found.\n"
    
    return content


@mcp.resource("papers://{topic}")
def get_topic_papers(topic: str) -> str:
    """
    Get detailed information about papers on a specific topic.
    
    Args:
        topic: The research topic to retrieve papers for
    """
    topic_dir = topic.lower().replace(" ", "_")
    papers_file = os.path.join(PAPER_DIR, topic_dir, "papers_info.json")
    
    if not os.path.exists(papers_file):
        return f"# No papers found for topic: {topic}\n\nTry searching for papers on this topic first."
    
    try:
        with open(papers_file, 'r') as f:
            papers_data = json.load(f)
        
        # Create markdown content with paper details
        content = f"# Papers on {topic.replace('_', ' ').title()}\n\n"
        content += f"Total papers: {len(papers_data)}\n\n"
        
        for paper_info in papers_data:
            content += f"## {paper_info['title']}\n"
            content += f"- **Paper ID**: {paper_info['entry_id']}\n"
            content += f"- **Authors**: {', '.join(paper_info['authors'])}\n"
            content += f"- **Published**: {paper_info['published']}\n"
            content += f"- **PDF URL**: {paper_info['pdf_url']}\n\n"
            content += f"### Summary\n{paper_info['summary'][:500]}...\n\n"
        
        return content
    except json.JSONDecodeError:
        return f"# Error reading papers data for {topic}\n\nThe papers data file is corrupted."


@mcp.prompt()
def generate_search_prompt(topic: str, num_papers: int = 5) -> str:
    """
    Generate a prompt for the AI to find and discuss academic papers on a specific topic.
    
    Args:
        topic: The topic to search for
        num_papers: Maximum number of results to retrieve (default: 5)
    """
    return f"""Search for {num_papers} academic papers about '{topic}' using the search_papers tool.

Follow these instructions:
1. First, search for papers using search_papers(topic='{topic}', max_results={num_papers})
2. For each paper found, extract and organize the following information:
   - Paper title
   - Authors
   - Publication date
   - Brief summary of the key findings
   - Main contributions or innovations
   - Methodologies used
   - Relevance to the topic '{topic}'

3. Provide a comprehensive summary that includes:
   - Overview of the current state of research in '{topic}'
   - Common themes and trends across the papers
   - Key research gaps or areas for future investigation
   - Most impactful or influential papers in this area

4. Organize your findings in a clear, structured format with headings and bullet points for easy reading.

Please present detailed information about each paper and a high-level summary at the end."""


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
