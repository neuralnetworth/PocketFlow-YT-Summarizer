import os
import time
import logging
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional, continue without it
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_provider_config(provider: str) -> None:
    """Validate that the required configuration is available for the specified provider."""
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY in your .env file.")
    
    elif provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError("Gemini API key is required. Please set GEMINI_API_KEY in your .env file.")
    
    else:
        raise ValueError(f"Unsupported provider: {provider}. Supported providers: openai, gemini")

def call_llm_openai(prompt: str, model: str = None, max_retries: int = 3) -> str:
    """Call OpenAI's API with retry logic."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("OpenAI package is required. Install it with: pip install openai")
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    for attempt in range(max_retries):
        try:
            if model is None:
                model = os.getenv("OPENAI_MODEL", "gpt-4o")
            # o3 models only support temperature=1 (default)
            if model.startswith("o3"):
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=4096
                )
            else:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=4096,
                    temperature=0.7
                )
            return response.choices[0].message.content
        
        except Exception as e:
            logger.warning(f"OpenAI API call failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise

def call_llm_gemini(prompt: str, model: str = None, max_retries: int = 3) -> str:
    """Call Google Gemini's API with retry logic."""
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("Google Generative AI package is required. Install it with: pip install google-generativeai")
    
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    if model is None:
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Configure safety settings to be less restrictive
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
    ]
    
    genai_model = genai.GenerativeModel(model)
    
    for attempt in range(max_retries):
        try:
            response = genai_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=4096,  # Increased for longer responses
                    temperature=0.7,
                ),
                safety_settings=safety_settings
            )
            
            # Check if response was blocked by safety filters
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason') and candidate.finish_reason != 1:  # 1 = STOP (normal completion)
                    # Handle different finish reasons
                    finish_reasons = {
                        2: "MAX_TOKENS",
                        3: "SAFETY", 
                        4: "RECITATION",
                        5: "OTHER"
                    }
                    reason = finish_reasons.get(candidate.finish_reason, f"UNKNOWN({candidate.finish_reason})")
                    logger.warning(f"Gemini response blocked/incomplete. Finish reason: {reason}")
                    
                    if candidate.finish_reason == 3:  # SAFETY
                        raise Exception("Content was blocked by safety filters. Try rephrasing your prompt.")
                    elif candidate.finish_reason == 2:  # MAX_TOKENS
                        # Try to get partial response
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            return candidate.content.parts[0].text
                        else:
                            raise Exception("Response was truncated due to max tokens limit.")
                
                # Get the text response
                if hasattr(response, 'text') and response.text:
                    return response.text
                elif response.candidates and response.candidates[0].content.parts:
                    return response.candidates[0].content.parts[0].text
                else:
                    raise Exception("No valid response text returned from Gemini API.")
            else:
                raise Exception("No candidates returned from Gemini API.")
        
        except Exception as e:
            logger.warning(f"Gemini API call failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise

def get_model_for_task(provider: str, task: str = None) -> str:
    """Get the appropriate model for a given provider and task type."""
    provider = provider.lower()
    
    if task:
        task = task.upper()
        if provider == "openai":
            if task == "ANALYSIS":
                return os.getenv("OPENAI_ANALYSIS_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o"))
            elif task == "SIMPLIFICATION":
                return os.getenv("OPENAI_SIMPLIFICATION_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o"))
        elif provider == "gemini":
            if task == "ANALYSIS":
                return os.getenv("GEMINI_ANALYSIS_MODEL", os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
            elif task == "SIMPLIFICATION":
                return os.getenv("GEMINI_SIMPLIFICATION_MODEL", os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
    
    # Fallback to general model
    if provider == "openai":
        return os.getenv("OPENAI_MODEL", "gpt-4o")
    elif provider == "gemini":
        return os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    raise ValueError(f"Unsupported provider: {provider}")

def call_llm(prompt: str, task: str = None) -> str:
    """
    Call the configured LLM provider based on the LLM_PROVIDER environment variable.
    
    Args:
        prompt: The prompt to send to the LLM
        task: Optional task type for model selection ("analysis" or "simplification")
        
    Returns:
        The LLM's response as a string
        
    Raises:
        ValueError: If the provider is not supported or configuration is missing
        ImportError: If required packages are not installed
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    # Validate configuration
    validate_provider_config(provider)
    
    # Get the appropriate model for this task
    model = get_model_for_task(provider, task)
    
    logger.info(f"Using LLM provider: {provider}, model: {model}, task: {task or 'general'}")
    
    try:
        if provider == "openai":
            return call_llm_openai(prompt, model=model)
        elif provider == "gemini":
            return call_llm_gemini(prompt, model=model)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
            
    except Exception as e:
        logger.error(f"LLM call failed with provider {provider}, model {model}: {e}")
        raise

def test_provider(provider: str) -> bool:
    """Test if a specific provider is working correctly."""
    test_prompt = "Hello, please respond with just the word 'success' to test the connection."
    
    try:
        # Temporarily set the provider for testing
        original_provider = os.getenv("LLM_PROVIDER")
        os.environ["LLM_PROVIDER"] = provider
        
        validate_provider_config(provider)
        response = call_llm(test_prompt)
        
        # Restore original provider
        if original_provider:
            os.environ["LLM_PROVIDER"] = original_provider
        
        logger.info(f"✅ {provider.upper()} test successful. Response: {response[:50]}...")
        return True
        
    except Exception as e:
        logger.error(f"❌ {provider.upper()} test failed: {e}")
        return False
    finally:
        # Ensure we restore the original provider even if an error occurs
        if 'original_provider' in locals() and original_provider:
            os.environ["LLM_PROVIDER"] = original_provider

def test_all_providers() -> None:
    """Test all configured providers."""
    print("Testing LLM providers...")
    print("=" * 50)
    
    providers = ["openai", "gemini"]
    results = {}
    
    for provider in providers:
        try:
            validate_provider_config(provider)
            results[provider] = test_provider(provider)
        except ValueError as e:
            logger.warning(f"Skipping {provider}: {e}")
            results[provider] = False
    
    print("\nTest Results:")
    print("=" * 50)
    for provider, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{provider.upper()}: {status}")
    
    working_providers = [p for p, success in results.items() if success]
    if working_providers:
        print(f"\nWorking providers: {', '.join(working_providers)}")
    else:
        print("\n⚠️  No working providers found. Please check your API keys and configuration.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_all_providers()
    else:
        # Test the currently configured provider
        test_prompt = "Hello, how are you?"
        try:
            response = call_llm(test_prompt)
            print(f"✅ Test successful. Response: {response}")
        except Exception as e:
            print(f"❌ Test failed: {e}")