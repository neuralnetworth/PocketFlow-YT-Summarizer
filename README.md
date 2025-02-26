# YouTube Content Processor

A system that processes YouTube videos to extract interesting topics, generates questions and answers, and creates child-friendly (ELI5 - Explain Like I'm 5) explanations in a beautiful HTML format.

## Features

- 🎬 Extracts transcript and metadata from YouTube videos
- 🔍 Identifies up to 5 most interesting topics from the content
- ❓ Generates 3 interesting questions for each topic
- 🧠 Rephrases topics and questions for clarity
- 👶 Creates simple ELI5 (Explain Like I'm 5) answers
- 🌐 Generates a beautiful HTML report with all the processed content

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/youtube-content-processor.git
cd youtube-content-processor
```

2. Set up a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Set up API keys:

Create a `.env` file in the project root and add your API keys:

```
ANTHROPIC_REGION=your_anthropic_region
ANTHROPIC_PROJECT_ID=your_anthropic_project_id
```

## Usage

You can run the processor in two ways:

### Command Line

```bash
python main.py --url "https://www.youtube.com/watch?v=example"
```

If you don't provide a URL, the program will prompt you to enter one.

### As a Module

```python
from flow import create_youtube_processor_flow

# Create the flow
flow = create_youtube_processor_flow()

# Initialize shared memory
shared = {
    "url": "https://www.youtube.com/watch?v=example"
}

# Run the flow
flow.run(shared)

# The HTML output is in shared["html_output"] and also saved to output.html
print(f"HTML saved to: {os.path.abspath('output.html')}")
```

## Output

The program generates an `output.html` file in the project directory. Open this file in a web browser to view the processed content in a beautiful, child-friendly format.

The HTML output includes:
- The video title and thumbnail
- Sections for each identified topic
- Questions and ELI5 answers for each topic

## Project Structure

```
youtube-content-processor/
├── main.py               # Main entry point
├── flow.py               # Flow definition and node implementations
├── utils/
│   ├── __init__.py
│   ├── call_llm.py       # LLM interaction functions
│   ├── youtube_processor.py  # YouTube content extraction
│   └── html_generator.py # HTML generation functions
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## Requirements

- Python 3.7+
- Access to Anthropic API (Claude)
- Internet connection to access YouTube content

## License

MIT
