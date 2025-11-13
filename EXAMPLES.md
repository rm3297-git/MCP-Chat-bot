# Example Usage Scenarios

## Scenario 1: Research on a New Topic

### Step 1: Search for Papers
```
Query: Search for papers about "deep learning transformers"
```

**What happens:**
- Client sends query to Claude
- Claude recognizes the need to use the `search_papers` tool
- Tool searches arXiv and stores results in `papers/deep_learning_transformers/`

**Expected Output:**
```
Found 5 papers on deep learning transformers:
1. "Attention Is All You Need" - arxiv:1706.03762
2. "BERT: Pre-training of Deep Bidirectional Transformers" - arxiv:1810.04805
...
```

### Step 2: View Available Topics
```
Query: @folders
```

**Expected Output:**
```
# Available Topics

- deep_learning_transformers
\nUse @deep_learning_transformers to access papers in that topic.
```

### Step 3: Access Topic Details
```
Query: @deep_learning_transformers
```

**Expected Output:**
```
# Papers on Deep Learning Transformers

Total papers: 5

## Attention Is All You Need
- **Paper ID**: arxiv:1706.03762
- **Authors**: Ashish Vaswani, Noam Shazeer, ...
- **Published**: 2017-06-12
- **PDF URL**: https://arxiv.org/pdf/1706.03762

### Summary
The dominant sequence transduction models are based on complex...
```

## Scenario 2: Using Prompt Templates

### Step 1: List Available Prompts
```
Query: /prompts
```

**Expected Output:**
```
Available prompts:
- generate_search_prompt: Generate a prompt for Claude to find and discuss academic papers on a specific topic.
  Arguments:
    - topic
    - num_papers
```

### Step 2: Execute Prompt
```
Query: /prompt generate_search_prompt topic=quantum_computing num_papers=3
```

**What happens:**
- Client fetches the prompt template
- Template is populated with arguments
- Full prompt is sent to Claude
- Claude executes the search and analysis

**Expected Output:**
```
Executing prompt 'generate_search_prompt'...

I'll search for 3 academic papers about quantum computing.

[Claude automatically uses search_papers tool]

Here's what I found:

## 1. Quantum Computing: A Gentle Introduction
**Authors**: Eleanor Rieffel, Wolfgang Polak
**Published**: 2011-03-15

This paper provides a comprehensive introduction to quantum computing...

[Detailed analysis follows]

## Summary
The current state of research in quantum computing shows...
[Comprehensive overview]
```

## Scenario 3: Multiple Topics Workflow

### Search Multiple Topics
```
Query: Find papers on neural architecture search

Query: Search for papers about few-shot learning

Query: Look for research on meta-learning
```

### View All Topics
```
Query: @folders
```

**Expected Output:**
```
# Available Topics

- neural_architecture_search
\nUse @neural_architecture_search to access papers in that topic.

- few_shot_learning
\nUse @few_shot_learning to access papers in that topic.

- meta_learning
\nUse @meta_learning to access papers in that topic.
```

### Compare Topics
```
Query: What are the connections between few-shot learning and meta-learning? Use @few_shot_learning and @meta_learning to analyze.
```

**What happens:**
- User references multiple resources
- Client would need to fetch both resources
- (Note: Current implementation fetches one at a time; enhancement would allow multiple)

## Scenario 4: Advanced Research Query

### Using Prompt Template
```
Query: /prompt generate_search_prompt topic=reinforcement_learning num_papers=10
```

**What happens:**
1. Prompt template is retrieved
2. Arguments (topic="reinforcement_learning", num_papers=10) are inserted
3. Full prompt is sent to Claude:

```
Search for 10 academic papers about 'reinforcement_learning' using the search_papers tool.

Follow these instructions:
1. First, search for papers using search_papers(topic='reinforcement_learning', max_results=10)
2. For each paper found, extract and organize the following information:
   - Paper title
   - Authors
   ...
```

4. Claude executes the tool
5. Claude analyzes all papers
6. Comprehensive report is generated

**Expected Output:**
```
# Research Report: Reinforcement Learning

## Papers Analyzed

### 1. Deep Reinforcement Learning with Double Q-learning
**Authors**: Hado van Hasselt, Arthur Guez, David Silver
**Key Findings**: The paper addresses overestimation in Q-learning...

[9 more papers follow]

## State of Research
Current research in reinforcement learning focuses on:
- Sample efficiency improvements
- Safe exploration strategies
- Multi-agent systems

## Common Themes
1. Deep neural networks as function approximators
2. Policy gradient methods
3. Model-based approaches

## Research Gaps
- Generalization across environments
- Long-term credit assignment
- Real-world deployment challenges

## Most Influential Papers
1. "Playing Atari with Deep Reinforcement Learning" (2013)
2. "Human-level control through deep reinforcement learning" (2015)
...
```

## Scenario 5: Error Handling

### Topic Not Found
```
Query: @nonexistent_topic
```

**Expected Output:**
```
# No papers found for topic: nonexistent_topic

Try searching for papers on this topic first.
```

### Invalid Prompt Argument
```
Query: /prompt generate_search_prompt topic=ai
```

**What happens:**
- Only required argument provided
- Optional argument (num_papers) uses default value
- Prompt executes normally

### Invalid Command
```
Query: /unknown_command
```

**Expected Output:**
```
Unknown command: unknown_command
```

## Scenario 6: Interactive Research Session

```
Query: I'm researching computer vision. Can you help me find recent papers?

> [Claude uses search_papers tool automatically]

Query: Show me what topics I have stored

> @folders

Query: Tell me more about computer vision papers

> @computer_vision

Query: Can you compare the approaches used in these papers?

> [Claude analyzes the papers from the resource and provides comparison]

Query: Use the comprehensive search prompt for image segmentation

> /prompt generate_search_prompt topic=image_segmentation num_papers=5

> [Full research report generated]
```

## Tips for Effective Usage

### 1. Start with Natural Language
- Let Claude figure out which tools to use
- Example: "Find papers about X" → Claude uses search_papers

### 2. Use Resources for Quick Access
- `@folders` to see what's available
- `@{topic}` to view stored papers
- Faster than re-searching

### 3. Use Prompts for Comprehensive Analysis
- Prompts provide structured, thorough research
- Best for new topics requiring deep dive
- Example: `/prompt generate_search_prompt topic=topic num_papers=10`

### 4. Combine Approaches
- Search → Store → Access → Analyze
- Natural language for exploration
- Resources for quick reference
- Prompts for comprehensive reports

### 5. Error Recovery
- If resource not found, search first
- If prompt fails, check argument format
- Use `/prompts` to see required arguments

## Command Quick Reference

| Command | Syntax | Purpose |
|---------|--------|---------|
| Natural Query | `{text}` | Ask Claude anything; tools auto-invoked |
| List Folders | `@folders` | See all stored topics |
| Access Topic | `@{topic}` | View papers for a topic |
| List Prompts | `/prompts` | See available prompt templates |
| Execute Prompt | `/prompt {name} arg=val` | Run a prompt template |
| Quit | `quit` | Exit the chatbot |

## Common Patterns

### Pattern 1: Quick Search and Review
```
1. "Find papers on {topic}"
2. @{topic}
```

### Pattern 2: Comprehensive Research
```
1. /prompt generate_search_prompt topic={topic} num_papers=10
```

### Pattern 3: Topic Exploration
```
1. "Search for papers on {topic1}"
2. "Also find papers on {topic2}"
3. @folders
4. Compare both topics
```

### Pattern 4: Incremental Research
```
1. "Find 3 papers on {topic}"
2. Review results
3. "Find 5 more papers on {subtopic}"
4. @{subtopic}
```
