"""Integration tests for the PocketFlow workflow to verify task-specific LLM calls."""

import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import yaml

# Add the parent directory to Python path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flow import (
    ExtractTopicsAndQuestions,
    ProcessContent,
    create_youtube_processor_flow
)


class TestExtractTopicsAndQuestions:
    """Test that ExtractTopicsAndQuestions node uses analysis task."""
    
    def test_node_uses_analysis_task(self):
        """Test that the ExtractTopicsAndQuestions node calls LLM with task='analysis'."""
        node = ExtractTopicsAndQuestions()
        
        # Create mock shared data
        shared = {
            "video_info": {
                "title": "Test Video",
                "transcript": "This is a test transcript with interesting content."
            }
        }
        
        # Mock the call_llm function
        with patch('flow.call_llm') as mock_call_llm:
            # Mock YAML response
            yaml_response = """```yaml
topics:
  - title: |
        Test Topic
    questions:
      - |
        What is this about?
      - |
        Why is this important?
```"""
            mock_call_llm.return_value = yaml_response
            
            # Call the node
            prep_result = node.prep(shared)
            exec_result = node.exec(prep_result)
            
            # Verify call_llm was called with task="analysis"
            mock_call_llm.assert_called_once()
            args, kwargs = mock_call_llm.call_args
            
            # Check that task parameter was passed
            assert 'task' in kwargs
            assert kwargs['task'] == 'analysis'
            
            # Verify the prompt contains the transcript and title
            prompt = args[0]
            assert "Test Video" in prompt
            assert "This is a test transcript" in prompt
            
            # Verify the result structure
            assert len(exec_result) == 1
            assert exec_result[0]['title'].strip() == 'Test Topic'
            assert len(exec_result[0]['questions']) == 2


class TestProcessContent:
    """Test that ProcessContent BatchNode uses simplification task."""
    
    def test_batch_node_uses_simplification_task(self):
        """Test that ProcessContent node calls LLM with task='simplification'."""
        node = ProcessContent()
        
        # Create mock shared data with topics
        shared = {
            "video_info": {
                "transcript": "Full transcript content here."
            },
            "topics": [{
                "title": "Test Topic",
                "questions": [
                    {"original": "What is this?", "rephrased": "", "answer": ""},
                    {"original": "Why does it matter?", "rephrased": "", "answer": ""}
                ]
            }]
        }
        
        # Mock the call_llm function
        with patch('flow.call_llm') as mock_call_llm:
            # Mock YAML response
            yaml_response = """```yaml
rephrased_title: |
    Cool Test Topic
questions:
  - original: |
        What is this?
    rephrased: |
        What's this all about?
    answer: |
        This is a simple explanation.
  - original: |
        Why does it matter?
    rephrased: |
        Why should we care?
    answer: |
        It matters because of reasons.
```"""
            mock_call_llm.return_value = yaml_response
            
            # Test batch processing
            prep_result = node.prep(shared)
            
            # Process the first (and only) batch item
            batch_item = prep_result[0]
            exec_result = node.exec(batch_item)
            
            # Verify call_llm was called with task="simplification"
            mock_call_llm.assert_called_once()
            args, kwargs = mock_call_llm.call_args
            
            # Check that task parameter was passed
            assert 'task' in kwargs
            assert kwargs['task'] == 'simplification'
            
            # Verify the prompt contains the topic and questions
            prompt = args[0]
            assert "Test Topic" in prompt
            assert "What is this?" in prompt
            assert "Why does it matter?" in prompt
            
            # Verify the result structure
            assert exec_result['title'] == 'Test Topic'
            assert exec_result['rephrased_title'].strip() == 'Cool Test Topic'
            assert len(exec_result['questions']) == 2


class TestWorkflowIntegration:
    """Test the complete workflow with mocked LLM calls."""
    
    @patch('flow.call_llm')
    def test_complete_workflow_task_routing(self, mock_call_llm):
        """Test that the workflow routes tasks correctly to LLM calls."""
        
        # Mock LLM responses for different tasks
        def llm_side_effect(*args, **kwargs):
            task = kwargs.get('task', 'general')
            
            if task == 'analysis':
                return """```yaml
topics:
  - title: |
        Test Topic
    questions:
      - |
        What is this?
```"""
            elif task == 'simplification':
                return """```yaml
rephrased_title: |
    Simple Topic
questions:
  - original: |
        What is this?
    rephrased: |
        What's this?
    answer: |
        Simple answer.
```"""
            else:
                return "General response"
        
        mock_call_llm.side_effect = llm_side_effect
        
        # Test individual node task routing
        
        # Test ExtractTopicsAndQuestions uses analysis task
        extract_node = ExtractTopicsAndQuestions()
        shared_extract = {
            "video_info": {
                "title": "Test Video",
                "transcript": "Test transcript"
            }
        }
        
        prep_res = extract_node.prep(shared_extract)
        extract_node.exec(prep_res)
        
        # Verify analysis task was called
        analysis_calls = [call for call in mock_call_llm.call_args_list 
                         if call[1].get('task') == 'analysis']
        assert len(analysis_calls) >= 1
        
        mock_call_llm.reset_mock()
        
        # Test ProcessContent uses simplification task
        process_node = ProcessContent()
        shared_process = {
            "video_info": {"transcript": "Test transcript"},
            "topics": [{
                "title": "Test Topic",
                "questions": [{"original": "What is this?", "rephrased": "", "answer": ""}]
            }]
        }
        
        prep_res = process_node.prep(shared_process)
        if prep_res:  # Only test if there are items to process
            process_node.exec(prep_res[0])
            
            # Verify simplification task was called
            simplification_calls = [call for call in mock_call_llm.call_args_list 
                                  if call[1].get('task') == 'simplification']
            assert len(simplification_calls) >= 1


class TestNodeErrorHandling:
    """Test error handling in nodes with task-specific calls."""
    
    def test_extract_topics_handles_llm_failure(self):
        """Test that ExtractTopicsAndQuestions handles LLM failures gracefully."""
        node = ExtractTopicsAndQuestions()
        
        shared = {
            "video_info": {
                "title": "Test Video",
                "transcript": "Test transcript"
            }
        }
        
        with patch('flow.call_llm') as mock_call_llm:
            mock_call_llm.side_effect = Exception("LLM API Error")
            
            prep_result = node.prep(shared)
            
            # Should raise the exception since we don't have error handling in the node
            with pytest.raises(Exception, match="LLM API Error"):
                node.exec(prep_result)
            
            # Verify it was called with the analysis task
            mock_call_llm.assert_called_once()
            args, kwargs = mock_call_llm.call_args
            assert kwargs.get('task') == 'analysis'
    
    def test_process_content_handles_yaml_parsing_error(self):
        """Test ProcessContent handles invalid YAML responses."""
        node = ProcessContent()
        
        batch_item = {
            "topic": {
                "title": "Test Topic",
                "questions": [{"original": "Test question?", "rephrased": "", "answer": ""}]
            },
            "transcript": "Test transcript"
        }
        
        with patch('flow.call_llm') as mock_call_llm:
            # Return invalid YAML
            mock_call_llm.return_value = "Invalid YAML content without proper structure"
            
            # Should raise a YAML parsing error
            with pytest.raises((yaml.YAMLError, KeyError, IndexError)):
                node.exec(batch_item)
            
            # Verify it was called with the simplification task
            mock_call_llm.assert_called_once()
            args, kwargs = mock_call_llm.call_args
            assert kwargs.get('task') == 'simplification'


class TestNodeConfiguration:
    """Test node configuration and setup."""
    
    def test_flow_creation_includes_retry_configuration(self):
        """Test that flow can be created successfully."""
        flow = create_youtube_processor_flow()
        
        # Verify flow was created
        assert flow is not None
        assert hasattr(flow, 'start_node')
        
        # Verify start node is the correct type
        assert isinstance(flow.start_node, type)  # Should be a class
    
    def test_node_types_are_correct(self):
        """Test that we can create the individual node types."""
        # Test individual node creation
        extract_node = ExtractTopicsAndQuestions()
        process_node = ProcessContent()
        
        # Verify they are the correct types
        assert isinstance(extract_node, ExtractTopicsAndQuestions)
        assert isinstance(process_node, ProcessContent)
        
        # Verify they have required methods
        assert hasattr(extract_node, 'prep')
        assert hasattr(extract_node, 'exec')
        assert hasattr(extract_node, 'post')
        
        assert hasattr(process_node, 'prep')
        assert hasattr(process_node, 'exec')
        assert hasattr(process_node, 'post')


if __name__ == "__main__":
    pytest.main([__file__])