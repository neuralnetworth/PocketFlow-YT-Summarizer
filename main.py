import argparse
import logging
import sys
import os
from flow import create_youtube_processor_flow

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("youtube_processor.log")
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the YouTube content processor."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Process a YouTube video to extract topics, questions, and generate informative answers."
    )
    parser.add_argument(
        "--url", 
        type=str, 
        help="YouTube video URL to process",
        required=False
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=['openai', 'gemini'],
        help="LLM provider to use (overrides .env setting). If not specified, uses both providers.",
        required=False
    )
    args = parser.parse_args()
    
    # Get YouTube URL from arguments or prompt user
    url = args.url
    if not url:
        url = input("Enter YouTube URL to process: ")
    
    # Determine which providers to use
    if args.provider:
        providers = [args.provider]
        logger.info(f"Using LLM provider from CLI: {args.provider}")
    else:
        providers = ['openai', 'gemini']
        logger.info("No provider specified - using both OpenAI and Gemini")
    
    logger.info(f"Starting YouTube content processor for URL: {url}")
    
    output_files = []
    
    # Process with each provider
    for provider in providers:
        logger.info(f"Processing with {provider.upper()} provider...")
        
        # Set the provider for this run
        original_provider = os.environ.get("LLM_PROVIDER")
        os.environ["LLM_PROVIDER"] = provider
        
        try:
            # Create flow
            flow = create_youtube_processor_flow()
            
            # Initialize shared memory
            shared = {
                "url": url
            }
            
            # Run the flow
            flow.run(shared)
            
            # Get output file path
            output_file = shared.get("output_file", "output.html")
            output_files.append(output_file)
            
            logger.info(f"✅ {provider.upper()} processing completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ {provider.upper()} processing failed: {e}")
            # Continue with next provider if one fails
            continue
            
        finally:
            # Restore original provider
            if original_provider:
                os.environ["LLM_PROVIDER"] = original_provider
            elif "LLM_PROVIDER" in os.environ:
                del os.environ["LLM_PROVIDER"]
    
    # Report success and output file locations
    print("\n" + "=" * 50)
    if output_files:
        print("Processing completed successfully!")
        print("Output HTML files:")
        for output_file in output_files:
            print(f"  - {os.path.abspath(output_file)}")
    else:
        print("❌ Processing failed for all providers.")
        return 1
    print("=" * 50 + "\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
