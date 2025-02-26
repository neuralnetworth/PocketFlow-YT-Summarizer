"""
YouTube Content Processor Flow

This module defines the Node classes and Flow for processing YouTube videos,
extracting topics, generating questions and answers, and creating HTML output.
"""

from typing import List, Dict, Any, Tuple
import yaml
import logging

from utils.call_llm import call_llm
from utils.youtube_processor import get_video_info
from utils.html_generator import html_generator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define the Node and Flow classes
class Node:
    """Base Node class for the YouTube Content Processor Flow"""
    def __init__(self, max_retries=1, wait=0):
        self.successors = {}
        self.max_retries = max_retries
        self.wait = wait
        self.cur_retry = 0
        self.params = {}
    
    def set_params(self, params):
        """Set parameters for the node"""
        self.params = params
        return self
    
    def prep(self, shared):
        """Prepare data from shared store for execution"""
        pass
    
    def exec(self, prep_res):
        """Execute the node's main logic"""
        pass
    
    def post(self, shared, prep_res, exec_res):
        """Post-process and update shared store with results"""
        return "default"
    
    def exec_fallback(self, prep_res, exc):
        """Fallback execution if main execution fails"""
        raise exc
    
    def run(self, shared):
        """Run the node's prep, exec, and post steps"""
        prep_res = self.prep(shared)
        
        self.cur_retry = 0
        exec_res = None
        while self.cur_retry < self.max_retries:
            try:
                exec_res = self.exec(prep_res)
                break
            except Exception as e:
                if self.cur_retry == self.max_retries - 1:
                    try:
                        exec_res = self.exec_fallback(prep_res, e)
                        break
                    except Exception as fallback_e:
                        raise fallback_e
                self.cur_retry += 1
                import time
                time.sleep(self.wait)
        
        action = self.post(shared, prep_res, exec_res)
        if action is None:
            action = "default"
        return action
    
    def __rshift__(self, other):
        """Operator >> for default transition"""
        self.successors["default"] = other
        return other
    
    def __sub__(self, action):
        """Operator - for named action transition"""
        return NodeAction(self, action)

class NodeAction:
    """Helper class for handling action transitions"""
    def __init__(self, node, action):
        self.node = node
        self.action = action
    
    def __rshift__(self, other):
        """Operator >> for action transition"""
        self.node.successors[self.action] = other
        return other

class BatchNode(Node):
    """Batch Node for processing multiple items"""
    def exec(self, items):
        """Execute for each item in the batch"""
        if not items:
            return []
        results = []
        for item in items:
            results.append(super(BatchNode, self).exec(item))
        return results

class Flow(Node):
    """Flow for managing execution of multiple nodes"""
    def __init__(self, start=None, **kwargs):
        super().__init__(**kwargs)
        self.start = start
    
    def exec(self, prep_res):
        """Flows don't have exec; they orchestrate nodes"""
        return None
    
    def run(self, shared):
        """Run the flow starting from the start node"""
        prep_res = self.prep(shared)
        
        current = self.start
        while current:
            logger.info(f"Running {type(current).__name__}")
            action = current.run(shared)
            
            if action in current.successors:
                current = current.successors[action]
            else:
                current = None
        
        self.post(shared, prep_res, None)
        return "default"

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

class ExtractTopics(Node):
    """Extract interesting topics from the video transcript"""
    def prep(self, shared):
        """Get transcript and title from video_info"""
        video_info = shared.get("video_info", {})
        transcript = video_info.get("transcript", "")
        title = video_info.get("title", "")
        
        # For very long transcripts, we might need to truncate
        if len(transcript) > 15000:
            transcript = transcript[:15000]
            logger.info("Transcript truncated to 15000 characters")
        
        return {"transcript": transcript, "title": title}
    
    def exec(self, data):
        """Extract topics using LLM"""
        transcript = data["transcript"]
        title = data["title"]
        
        prompt = f"""
You are an expert content analyzer. Given a YouTube video transcript, identify the 5 most interesting topics discussed.
Remove any intro or advertising content, focus only on the substantive material.

VIDEO TITLE: {title}

TRANSCRIPT:
{transcript}

Extract exactly 5 topics that are most interesting and unique to this video.
Format your response in YAML:

```yaml
topics:
  - title: "First Topic Title"
  - title: "Second Topic Title"
  - title: "Third Topic Title"
  - title: "Fourth Topic Title"
  - title: "Fifth Topic Title"
```
        """
        
        response = call_llm(prompt)
        
        # Extract YAML content
        yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
        
        # Parse YAML
        try:
            parsed = yaml.safe_load(yaml_content)
            topics = parsed.get("topics", [])
            
            # Ensure we have at most 5 topics
            topics = topics[:5]
            
            return topics
        except Exception as e:
            logger.error(f"Error parsing topics YAML: {e}")
            raise ValueError(f"Failed to parse topics: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """Store topics in shared"""
        # Initialize the topics list with the extracted topics
        shared["topics"] = [
            {
                "title": topic.get("title", ""),
                "questions": []
            }
            for topic in exec_res
        ]
        
        logger.info(f"Extracted {len(shared['topics'])} topics")
        return "default"

class GenerateQuestions(BatchNode):
    """Generate interesting questions for each topic"""
    def prep(self, shared):
        """Return list of topics for batch processing"""
        video_info = shared.get("video_info", {})
        transcript = video_info.get("transcript", "")
        topics = shared.get("topics", [])
        
        # For each topic, prepare a batch item with topic and transcript
        batch_items = []
        for topic in topics:
            batch_items.append({
                "topic_title": topic["title"],
                "transcript": transcript
            })
        
        return batch_items
    
    def exec(self, item):
        """Generate questions for a topic using LLM"""
        topic_title = item["topic_title"]
        transcript = item["transcript"]
        
        prompt = f"""
You are an expert content analyzer. Given a YouTube video transcript and a topic, generate 3 most interesting questions related to this topic.

TOPIC: {topic_title}

TRANSCRIPT EXCERPT:
{transcript[:5000]}

Generate the 3 most interesting questions about this topic that are answerable from the transcript.
Format your response in YAML:

```yaml
questions:
  - question: "First question?"
  - question: "Second question?"
  - question: "Third question?"
```
        """
        
        response = call_llm(prompt)
        
        # Extract YAML content
        yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
        
        # Parse YAML
        try:
            parsed = yaml.safe_load(yaml_content)
            questions = parsed.get("questions", [])
            
            # Ensure we have exactly 3 questions
            questions = questions[:3]
            
            return {
                "topic_title": topic_title,
                "questions": questions
            }
        except Exception as e:
            logger.error(f"Error parsing questions YAML: {e}")
            raise ValueError(f"Failed to parse questions: {e}")
    
    def post(self, shared, prep_res, exec_res_list):
        """Update topics with questions in shared"""
        topics = shared.get("topics", [])
        
        # Map of topic title to list of questions
        topic_to_questions = {
            result["topic_title"]: result["questions"]
            for result in exec_res_list
        }
        
        # Update the topics with questions
        for topic in topics:
            topic_title = topic["title"]
            if topic_title in topic_to_questions:
                # Add the questions to the topic
                topic["questions"] = [
                    {
                        "original": q.get("question", ""),
                        "rephrased": "",
                        "answer": ""
                    }
                    for q in topic_to_questions[topic_title]
                ]
        
        # Update shared with modified topics
        shared["topics"] = topics
        
        logger.info(f"Generated questions for {len(exec_res_list)} topics")
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
        
        prompt = f"""
You are a content simplifier for children. Given a topic and questions from a YouTube video, rephrase the topic title and questions to be clearer, and provide simple ELI5 (Explain Like I'm 5) answers.

TOPIC: {topic_title}

QUESTIONS:
{chr(10).join([f"- {q}" for q in questions])}

TRANSCRIPT EXCERPT:
{transcript[:5000]}

Rephrase the topic title and each question to be clear and simple. Then provide a brief, child-friendly answer (ELI5) for each question.
Format your response in YAML:

```yaml
rephrased_title: "Clearer topic title"
questions:
  - original: "{questions[0] if len(questions) > 0 else ''}"
    rephrased: "Rephrased question 1?"
    answer: "Simple answer that a 5-year-old could understand."
  - original: "{questions[1] if len(questions) > 1 else ''}"
    rephrased: "Rephrased question 2?"
    answer: "Simple answer that a 5-year-old could understand."
  - original: "{questions[2] if len(questions) > 2 else ''}"
    rephrased: "Rephrased question 3?"
    answer: "Simple answer that a 5-year-old could understand."
```
        """
        
        response = call_llm(prompt)
        
        # Extract YAML content
        yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
        
        # Parse YAML
        try:
            parsed = yaml.safe_load(yaml_content)
            rephrased_title = parsed.get("rephrased_title", topic_title)
            processed_questions = parsed.get("questions", [])
            
            result = {
                "title": topic_title,
                "rephrased_title": rephrased_title,
                "questions": processed_questions
            }
            
            return result
        except Exception as e:
            logger.error(f"Error parsing processed content YAML: {e}")
            raise ValueError(f"Failed to parse processed content: {e}")
    
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
                bullets.append((q, a))
            
            sections.append({
                "title": section_title,
                "bullets": bullets
            })
        
        # Generate HTML
        html_content = html_generator(title, thumbnail_url, sections)
        return html_content
    
    def post(self, shared, prep_res, exec_res):
        """Store HTML output in shared"""
        shared["html_output"] = exec_res
        
        # Write HTML to file
        with open("output.html", "w") as f:
            f.write(exec_res)
        
        logger.info("Generated HTML output and saved to output.html")
        return "default"

# Create the flow
def create_youtube_processor_flow():
    """Create and connect the nodes for the YouTube processor flow"""
    # Create nodes
    process_url = ProcessYouTubeURL(max_retries=2)
    extract_topics = ExtractTopics(max_retries=2)
    generate_questions = GenerateQuestions(max_retries=2)
    process_content = ProcessContent(max_retries=2)
    generate_html = GenerateHTML()
    
    # Connect nodes
    process_url >> extract_topics >> generate_questions >> process_content >> generate_html
    
    # Create flow
    flow = Flow(start=process_url)
    
    return flow
