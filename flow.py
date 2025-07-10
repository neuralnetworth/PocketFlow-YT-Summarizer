from typing import List, Dict, Any, Tuple
import yaml
import logging
import os
import re
from pocketflow import Node, BatchNode, Flow
from utils.call_llm import call_llm
from utils.youtube_processor import get_video_info
from utils.html_generator import html_generator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    """Sanitize a string to be safe for use as a filename"""
    # Remove or replace characters that are invalid in filenames
    # Keep alphanumeric, spaces, hyphens, and underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace multiple spaces with single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    # Remove leading/trailing whitespace
    sanitized = sanitized.strip()
    # Limit length to 200 characters to avoid filesystem issues
    if len(sanitized) > 200:
        sanitized = sanitized[:200].strip()
    # If empty after sanitization, use a default name
    if not sanitized:
        sanitized = "youtube_video"
    return sanitized

# Define the specific nodes for the YouTube Content Processor

class ProcessYouTubeURL(Node):
    """Process YouTube URL to extract video information"""
    def prep(self, shared):
        """Get URL from shared"""
        return shared.get("url", "")
    
    def exec(self, url):
        """Extract video information"""
        if not url:
            raise ValueError("No YouTube URL provided")
        
        logger.info(f"Processing YouTube URL: {url}")
        video_info = get_video_info(url)
        
        if "error" in video_info:
            raise ValueError(f"Error processing video: {video_info['error']}")
        
        return video_info
    
    def post(self, shared, prep_res, exec_res):
        """Store video information in shared"""
        shared["video_info"] = exec_res
        logger.info(f"Video title: {exec_res.get('title')}")
        logger.info(f"Transcript length: {len(exec_res.get('transcript', ''))}")
        return "default"

class ExtractTopicsAndQuestions(Node):
    """Extract interesting topics and generate questions from the video transcript"""
    def prep(self, shared):
        """Get transcript and title from video_info"""
        video_info = shared.get("video_info", {})
        transcript = video_info.get("transcript", "")
        title = video_info.get("title", "")
        return {"transcript": transcript, "title": title}
    
    def exec(self, data):
        """Extract topics and generate questions using LLM"""
        transcript = data["transcript"]
        title = data["title"]
        
        # Single prompt to extract topics and questions together
        prompt = f"""
You are an expert content analyzer. Given a YouTube video transcript, identify at most 5 most interesting topics discussed and generate at most 3 most thought-provoking questions for each topic.
These questions don't need to be directly asked in the video. It's good to have clarification questions.

VIDEO TITLE: {title}

TRANSCRIPT:
{transcript}

Format your response in YAML:

```yaml
topics:
  - title: |
        First Topic Title
    questions:
      - |
        Question 1 about first topic?
      - |
        Question 2 ...
  - title: |
        Second Topic Title
    questions:
        ...
```
        """
        
        response = call_llm(prompt, task="analysis")
        
        # Extract YAML content
        yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
        
        parsed = yaml.safe_load(yaml_content)
        
        if parsed is None:
            raise ValueError("Failed to parse YAML response from LLM - parsed result is None")
        
        raw_topics = parsed.get("topics", [])
        
        # Ensure we have at most 5 topics
        raw_topics = raw_topics[:5]
        
        # Format the topics and questions for our data structure
        result_topics = []
        for topic in raw_topics:
            topic_title = topic.get("title", "")
            raw_questions = topic.get("questions", [])
            
            # Create a complete topic with questions
            result_topics.append({
                "title": topic_title,
                "questions": [
                    {
                        "original": q,
                        "rephrased": "",
                        "answer": ""
                    }
                    for q in raw_questions
                ]
            })
        
        return result_topics
    
    def post(self, shared, prep_res, exec_res):
        """Store topics with questions in shared"""
        shared["topics"] = exec_res
        
        # Count total questions
        total_questions = sum(len(topic.get("questions", [])) for topic in exec_res)
        
        logger.info(f"Extracted {len(exec_res)} topics with {total_questions} questions")
        return "default"

class ProcessContent(BatchNode):
    """Process each topic for rephrasing and answering"""
    def prep(self, shared):
        """Return list of topics for batch processing"""
        topics = shared.get("topics", [])
        video_info = shared.get("video_info", {})
        transcript = video_info.get("transcript", "")
        
        batch_items = []
        for topic in topics:
            batch_items.append({
                "topic": topic,
                "transcript": transcript
            })
        
        return batch_items
    
    def exec(self, item):
        """Process a topic using LLM"""
        topic = item["topic"]
        transcript = item["transcript"]
        
        topic_title = topic["title"]
        questions = [q["original"] for q in topic["questions"]]
        
        prompt = f"""You are an expert content processor. Given a topic and questions from a YouTube video, rephrase the topic title and questions to be clearer and more engaging, and provide concise, informative answers.

TOPIC: {topic_title}

QUESTIONS:
{chr(10).join([f"- {q}" for q in questions])}

TRANSCRIPT EXCERPT:
{transcript}

For topic title and questions:
1. Keep them engaging and clear, but concise
2. Make them accessible to a general adult audience

For your answers:
1. Format them using HTML with <b> and <i> tags for highlighting. 
2. Prefer lists with <ol> and <li> tags. Ideally, <li> followed by <b> for the key points.
3. Define technical terms clearly but don't oversimplify (e.g., "<b>Quantum computing</b> uses quantum mechanical phenomena to process information exponentially faster than classical computers")
4. Provide comprehensive yet concise explanations suitable for an educated audience
5. Focus on clarity and accuracy rather than simplification

Format your response in YAML:

```yaml
rephrased_title: |
    Clear and engaging topic title
questions:
  - original: |
        {questions[0] if len(questions) > 0 else ''}
    rephrased: |
        Clear, engaging question
    answer: |
        Comprehensive, well-structured answer with proper technical depth
  - original: |
        {questions[1] if len(questions) > 1 else ''}
    ...
```
        """
        
        response = call_llm(prompt, task="simplification")
        
        # Extract YAML content
        yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
        
        parsed = yaml.safe_load(yaml_content)
        rephrased_title = parsed.get("rephrased_title", topic_title)
        processed_questions = parsed.get("questions", [])
        
        result = {
            "title": topic_title,
            "rephrased_title": rephrased_title,
            "questions": processed_questions
        }
        
        return result

    
    def post(self, shared, prep_res, exec_res_list):
        """Update topics with processed content in shared"""
        topics = shared.get("topics", [])
        
        # Map of original topic title to processed content
        title_to_processed = {
            result["title"]: result
            for result in exec_res_list
        }
        
        # Update the topics with processed content
        for topic in topics:
            topic_title = topic["title"]
            if topic_title in title_to_processed:
                processed = title_to_processed[topic_title]
                
                # Update topic with rephrased title
                topic["rephrased_title"] = processed["rephrased_title"]
                
                # Map of original question to processed question
                orig_to_processed = {
                    q["original"]: q
                    for q in processed["questions"]
                }
                
                # Update each question
                for q in topic["questions"]:
                    original = q["original"]
                    if original in orig_to_processed:
                        processed_q = orig_to_processed[original]
                        q["rephrased"] = processed_q.get("rephrased", original)
                        q["answer"] = processed_q.get("answer", "")
        
        # Update shared with modified topics
        shared["topics"] = topics
        
        logger.info(f"Processed content for {len(exec_res_list)} topics")
        return "default"

class GenerateHTML(Node):
    """Generate HTML output from processed content"""
    def prep(self, shared):
        """Get video info and topics from shared"""
        video_info = shared.get("video_info", {})
        topics = shared.get("topics", [])
        
        return {
            "video_info": video_info,
            "topics": topics
        }
    
    def exec(self, data):
        """Generate HTML using html_generator"""
        video_info = data["video_info"]
        topics = data["topics"]
        
        title = video_info.get("title", "YouTube Video Summary")
        thumbnail_url = video_info.get("thumbnail_url", "")
        
        # Prepare sections for HTML
        sections = []
        for topic in topics:
            # Skip topics without questions
            if not topic.get("questions"):
                continue
                
            # Use rephrased_title if available, otherwise use original title
            section_title = topic.get("rephrased_title", topic.get("title", ""))
            
            # Prepare bullets for this section
            bullets = []
            for question in topic.get("questions", []):
                # Use rephrased question if available, otherwise use original
                q = question.get("rephrased", question.get("original", ""))
                a = question.get("answer", "")
                
                # Only add bullets if both question and answer have content
                if q.strip() and a.strip():
                    bullets.append((q, a))
            
            # Only include section if it has bullets
            if bullets:
                sections.append({
                    "title": section_title,
                    "bullets": bullets
                })
        
        # Get LLM provider for display
        llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        
        # Generate HTML
        html_content = html_generator(title, sections, provider=llm_provider)
        return html_content
    
    def post(self, shared, prep_res, exec_res):
        """Store HTML output in shared"""
        shared["html_output"] = exec_res
        
        # Create output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Get video title and sanitize it for filename
        video_info = prep_res["video_info"]
        video_title = video_info.get("title", "youtube_video")
        safe_filename = sanitize_filename(video_title)
        
        # Get LLM provider for filename
        llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        
        # Create full file path with provider name
        file_path = os.path.join(output_dir, f"{safe_filename}_{llm_provider}.html")
        
        # Write HTML to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(exec_res)
        
        # Store the file path in shared for reference
        shared["output_file"] = file_path
        
        logger.info(f"Generated HTML output and saved to {file_path}")
        return "default"

# Create the flow
def create_youtube_processor_flow():
    """Create and connect the nodes for the YouTube processor flow"""
    # Create nodes
    process_url = ProcessYouTubeURL(max_retries=2, wait=10)
    extract_topics_and_questions = ExtractTopicsAndQuestions(max_retries=2, wait=10)
    process_content = ProcessContent(max_retries=2, wait=10)
    generate_html = GenerateHTML(max_retries=2, wait=10)
    
    # Connect nodes
    process_url >> extract_topics_and_questions >> process_content >> generate_html
    
    # Create flow
    flow = Flow(start=process_url)
    
    return flow
