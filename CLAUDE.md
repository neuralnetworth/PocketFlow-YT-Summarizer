# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PocketFlow-YT-Summarizer is an LLM-powered application that converts long YouTube videos into concise, easy-to-understand summaries. It extracts transcripts, identifies key topics, generates questions, and provides ELI5 (Explain Like I'm 5) answers.

## Common Development Commands

### Setup and Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run with YouTube URL
python main.py --url "https://www.youtube.com/watch?v=VIDEO_ID"

# Run interactively (prompts for URL)
python main.py
```

### Output
The application generates `output.html` in the project directory.

## Architecture

The application uses the PocketFlow framework with a 4-node workflow:

1. **ProcessYouTubeURL** → Extracts video metadata and transcript
2. **ExtractTopicsAndQuestions** → Identifies up to 5 topics with 3 questions each
3. **ProcessContent** → Batch processes topics to rephrase and generate ELI5 answers
4. **GenerateHTML** → Creates styled HTML output

### Key Files
- `flow.py`: Main workflow implementation with node definitions
- `main.py`: Entry point handling CLI arguments
- `utils/youtube_processor.py`: YouTube data extraction
- `utils/call_llm.py`: LLM API wrapper (configured for Anthropic Claude via Vertex AI)
- `utils/html_generator.py`: HTML generation with Tailwind CSS styling

### Shared Memory Structure
```python
{
    "url": str,
    "video_info": {
        "title": str,
        "transcript": str,
        "thumbnail_url": str,
        "video_id": str
    },
    "topics": [{
        "title": str,
        "rephrased_title": str,
        "questions": [{
            "original": str,
            "rephrased": str,
            "answer": str  # ELI5 answer with HTML formatting
        }]
    }],
    "html_output": str
}
```

## Development Guidelines

### LLM Configuration
- The LLM configuration is in `utils/call_llm.py`
- Supports multiple providers: OpenAI and Google Gemini
- **Task-specific model selection** for optimal performance and cost
- Switch providers by setting `LLM_PROVIDER` environment variable
- Implements retry logic with exponential backoff for both providers
- Uses YAML for structured outputs (more reliable than JSON)

#### Task-Specific Model Configuration

The application makes 2 distinct types of LLM calls:

1. **Analysis Tasks** (`task="analysis"`) - Complex reasoning for topic extraction
   - **Node:** `ExtractTopicsAndQuestions` 
   - **Purpose:** Analyze full video transcript, identify themes, generate questions
   - **Complexity:** High cognitive load, pattern recognition
   - **Recommended:** Use reasoning models (`gpt-4o`, `gemini-1.5-pro`)

2. **Simplification Tasks** (`task="simplification"`) - Content rephrasing and ELI5
   - **Node:** `ProcessContent` (BatchNode - runs multiple times)
   - **Purpose:** Rephrase topics/questions, create simple explanations
   - **Complexity:** Medium - clear communication over deep analysis
   - **Recommended:** Use fast models (`gpt-4o-mini`, `gemini-1.5-flash`)

#### Environment Variables
Set these in your `.env` file:
```bash
# Choose provider: openai or gemini
LLM_PROVIDER=openai

# Task-Specific Model Configuration
# ANALYSIS: Complex reasoning tasks (topic extraction, content analysis)
OPENAI_ANALYSIS_MODEL=gpt-4o
GEMINI_ANALYSIS_MODEL=gemini-1.5-pro

# SIMPLIFICATION: Simple tasks (rephrasing, ELI5 answers) 
OPENAI_SIMPLIFICATION_MODEL=gpt-4o-mini
GEMINI_SIMPLIFICATION_MODEL=gemini-1.5-flash

# General Model Configuration (fallback if task-specific not set)
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-1.5-flash

# API Keys (get the key for your chosen provider)
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

#### Available Models & Recommendations

**OpenAI Models:**
- `gpt-4o` - Latest GPT-4 Omni model (best for analysis)
- `gpt-4o-mini` - Faster, cheaper version (ideal for simplification)
- `gpt-4-turbo` - Previous generation GPT-4 Turbo
- `gpt-3.5-turbo` - Most economical option

**Gemini Models:**
- `gemini-1.5-pro` - Most capable model (best for analysis)
- `gemini-1.5-flash` - Fast and efficient (ideal for simplification)

#### Optimization Examples

**Cost-Optimized Configuration:**
```bash
LLM_PROVIDER=openai
OPENAI_ANALYSIS_MODEL=gpt-4o-mini      # Cheaper for analysis
OPENAI_SIMPLIFICATION_MODEL=gpt-3.5-turbo # Cheapest for simplification
```

**Quality-Optimized Configuration:**
```bash  
LLM_PROVIDER=openai
OPENAI_ANALYSIS_MODEL=gpt-4o           # Best reasoning for analysis
OPENAI_SIMPLIFICATION_MODEL=gpt-4o-mini # Fast enough for simplification
```

**Hybrid Provider Configuration:**
```bash
# Use different providers for different tasks if desired
LLM_PROVIDER=openai
OPENAI_ANALYSIS_MODEL=gpt-4o
GEMINI_SIMPLIFICATION_MODEL=gemini-1.5-flash
```

#### Testing LLM Providers
```bash
# Test current provider
python utils/call_llm.py

# Test all configured providers
python utils/call_llm.py test
```

### PocketFlow Framework
This project is built on PocketFlow, a minimal LLM workflow framework. Key concepts:
- **Nodes**: Individual processing units with async `process()` methods
- **BatchNode**: Processes multiple items in parallel
- **Flow**: Directed graph connecting nodes
- **Shared Memory**: Dictionary passed between nodes

### Output Formatting
- LLM responses include HTML tags (bold, italic, lists)
- Generated HTML uses Tailwind CSS and Kalam handwriting font
- Examples in the `examples/` directory show expected output format

### Error Handling
- YouTube transcript extraction failures are caught and logged
- LLM calls implement retry logic
- Missing video metadata handled gracefully

## Testing

Currently no automated tests. To test changes:
1. Run with a sample YouTube URL
2. Verify HTML output renders correctly
3. Check that all topics have rephrased titles and ELI5 answers
4. Ensure error cases (invalid URLs, private videos) are handled

## Notes

- The project includes 18 pre-generated examples in `examples/`
- See `.cursorrules` for extensive PocketFlow framework documentation
- The application limits to 5 topics and 3 questions per topic for focused summaries