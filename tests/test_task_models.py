"""Integration tests for task-specific model selection across the workflow."""

import os
import pytest
from unittest.mock import patch, MagicMock
import sys

# Add the parent directory to Python path so we can import from utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.call_llm import call_llm


class TestTaskSpecificModelSelection:
    """Test that different tasks use appropriate models based on configuration."""
    
    @patch('utils.call_llm.call_llm_openai')
    def test_analysis_task_uses_reasoning_model(self, mock_openai):
        """Test that analysis tasks use reasoning models (gpt-4o, gemini-1.5-pro)."""
        mock_openai.return_value = "Analysis result"
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-valid-key',
            'OPENAI_ANALYSIS_MODEL': 'gpt-4o',
            'OPENAI_SIMPLIFICATION_MODEL': 'gpt-4o-mini'
        }):
            result = call_llm("Analyze this transcript", task="analysis")
            
            assert result == "Analysis result"
            # Verify the correct model was used
            mock_openai.assert_called_once_with("Analyze this transcript", model="gpt-4o")
    
    @patch('utils.call_llm.call_llm_openai')
    def test_simplification_task_uses_fast_model(self, mock_openai):
        """Test that simplification tasks use fast models (gpt-4o-mini, gemini-1.5-flash)."""
        mock_openai.return_value = "Simplified result"
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-valid-key',
            'OPENAI_ANALYSIS_MODEL': 'gpt-4o',
            'OPENAI_SIMPLIFICATION_MODEL': 'gpt-4o-mini'
        }):
            result = call_llm("Simplify this content", task="simplification")
            
            assert result == "Simplified result"
            # Verify the correct model was used
            mock_openai.assert_called_once_with("Simplify this content", model="gpt-4o-mini")
    
    @patch('utils.call_llm.call_llm_gemini')
    def test_gemini_analysis_uses_pro_model(self, mock_gemini):
        """Test that Gemini analysis tasks use gemini-1.5-pro."""
        mock_gemini.return_value = "Gemini analysis result"
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'gemini',
            'GEMINI_API_KEY': 'valid-gemini-key',
            'GEMINI_ANALYSIS_MODEL': 'gemini-1.5-pro',
            'GEMINI_SIMPLIFICATION_MODEL': 'gemini-1.5-flash'
        }):
            result = call_llm("Complex analysis task", task="analysis")
            
            assert result == "Gemini analysis result"
            mock_gemini.assert_called_once_with("Complex analysis task", model="gemini-1.5-pro")
    
    @patch('utils.call_llm.call_llm_gemini')
    def test_gemini_simplification_uses_flash_model(self, mock_gemini):
        """Test that Gemini simplification tasks use gemini-1.5-flash."""
        mock_gemini.return_value = "Gemini simplified result"
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'gemini',
            'GEMINI_API_KEY': 'valid-gemini-key',
            'GEMINI_ANALYSIS_MODEL': 'gemini-1.5-pro',
            'GEMINI_SIMPLIFICATION_MODEL': 'gemini-1.5-flash'
        }):
            result = call_llm("Simple explanation task", task="simplification")
            
            assert result == "Gemini simplified result"
            mock_gemini.assert_called_once_with("Simple explanation task", model="gemini-1.5-flash")


class TestOptimalModelConfigurations:
    """Test different optimal configurations for cost vs quality."""
    
    @patch('utils.call_llm.call_llm_openai')
    def test_cost_optimized_configuration(self, mock_openai):
        """Test cost-optimized configuration using smaller models."""
        mock_openai.return_value = "Cost optimized result"
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-valid-key',
            'OPENAI_ANALYSIS_MODEL': 'gpt-4o-mini',     # Cheaper for analysis
            'OPENAI_SIMPLIFICATION_MODEL': 'gpt-3.5-turbo'  # Cheapest for simplification
        }):
            # Test analysis task
            call_llm("analysis prompt", task="analysis")
            mock_openai.assert_called_with("analysis prompt", model="gpt-4o-mini")
            
            mock_openai.reset_mock()
            
            # Test simplification task
            call_llm("simplification prompt", task="simplification")
            mock_openai.assert_called_with("simplification prompt", model="gpt-3.5-turbo")
    
    @patch('utils.call_llm.call_llm_openai')
    def test_quality_optimized_configuration(self, mock_openai):
        """Test quality-optimized configuration using best models."""
        mock_openai.return_value = "Quality optimized result"
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-valid-key',
            'OPENAI_ANALYSIS_MODEL': 'gpt-4o',           # Best for analysis
            'OPENAI_SIMPLIFICATION_MODEL': 'gpt-4o-mini'    # Good enough for simplification
        }):
            # Test analysis task
            call_llm("complex analysis", task="analysis")
            mock_openai.assert_called_with("complex analysis", model="gpt-4o")
            
            mock_openai.reset_mock()
            
            # Test simplification task
            call_llm("simple explanation", task="simplification")
            mock_openai.assert_called_with("simple explanation", model="gpt-4o-mini")


class TestFallbackBehavior:
    """Test fallback behavior when task-specific models aren't configured."""
    
    @patch('utils.call_llm.call_llm_openai')
    def test_fallback_to_general_model_when_task_model_missing(self, mock_openai):
        """Test fallback to general model when task-specific model not configured."""
        mock_openai.return_value = "Fallback result"
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-valid-key',
            'OPENAI_MODEL': 'gpt-4o'  # Only general model configured
            # No OPENAI_ANALYSIS_MODEL or OPENAI_SIMPLIFICATION_MODEL
        }, clear=True):
            # Both tasks should fall back to the general model
            call_llm("analysis task", task="analysis")
            mock_openai.assert_called_with("analysis task", model="gpt-4o")
            
            mock_openai.reset_mock()
            
            call_llm("simplification task", task="simplification")
            mock_openai.assert_called_with("simplification task", model="gpt-4o")
    
    @patch('utils.call_llm.call_llm_openai')
    def test_fallback_to_hardcoded_default_when_no_models_configured(self, mock_openai):
        """Test fallback to hardcoded defaults when no models configured."""
        mock_openai.return_value = "Default result"
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-valid-key'
            # No model configuration at all
        }, clear=True):
            # Should use hardcoded defaults
            call_llm("any task", task="analysis")
            mock_openai.assert_called_with("any task", model="gpt-4o")  # Default


class TestMixedProviderConfiguration:
    """Test scenarios with mixed provider configurations."""
    
    def test_different_providers_for_different_tasks(self):
        """Test configuration where different providers could be optimal for different tasks."""
        # This test documents the current behavior where LLM_PROVIDER determines
        # which provider is used, regardless of which models are configured
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',  # This determines the provider used
            'OPENAI_API_KEY': 'sk-valid-key',
            'GEMINI_API_KEY': 'valid-gemini-key',
            
            # Configure both providers with optimal models
            'OPENAI_ANALYSIS_MODEL': 'gpt-4o',
            'OPENAI_SIMPLIFICATION_MODEL': 'gpt-4o-mini',
            'GEMINI_ANALYSIS_MODEL': 'gemini-1.5-pro',
            'GEMINI_SIMPLIFICATION_MODEL': 'gemini-1.5-flash'
        }):
            with patch('utils.call_llm.call_llm_openai') as mock_openai:
                mock_openai.return_value = "OpenAI result"
                
                # Both tasks use OpenAI because LLM_PROVIDER is set to 'openai'
                call_llm("analysis", task="analysis")
                mock_openai.assert_called_with("analysis", model="gpt-4o")
                
                mock_openai.reset_mock()
                
                call_llm("simplification", task="simplification")
                mock_openai.assert_called_with("simplification", model="gpt-4o-mini")


class TestTaskTypeValidation:
    """Test behavior with different task type inputs."""
    
    @patch('utils.call_llm.call_llm_openai')
    def test_case_insensitive_task_types(self, mock_openai):
        """Test that task types are case insensitive."""
        mock_openai.return_value = "Result"
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-valid-key',
            'OPENAI_ANALYSIS_MODEL': 'gpt-4o',
            'OPENAI_SIMPLIFICATION_MODEL': 'gpt-4o-mini'
        }):
            # Test different case variations
            test_cases = [
                ('analysis', 'gpt-4o'),
                ('ANALYSIS', 'gpt-4o'),
                ('Analysis', 'gpt-4o'),
                ('simplification', 'gpt-4o-mini'),
                ('SIMPLIFICATION', 'gpt-4o-mini'),
                ('Simplification', 'gpt-4o-mini')
            ]
            
            for task, expected_model in test_cases:
                mock_openai.reset_mock()
                call_llm("test prompt", task=task)
                mock_openai.assert_called_with("test prompt", model=expected_model)
    
    @patch('utils.call_llm.call_llm_openai')
    def test_unknown_task_type_uses_general_model(self, mock_openai):
        """Test that unknown task types fall back to general model."""
        mock_openai.return_value = "Result"
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-valid-key',
            'OPENAI_MODEL': 'gpt-4o',
            'OPENAI_ANALYSIS_MODEL': 'gpt-4-turbo'
        }):
            # Unknown task should use general model
            call_llm("test prompt", task="unknown_task")
            mock_openai.assert_called_with("test prompt", model="gpt-4o")
    
    @patch('utils.call_llm.call_llm_openai')
    def test_none_task_uses_general_model(self, mock_openai):
        """Test that None task uses general model."""
        mock_openai.return_value = "Result"
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-valid-key',
            'OPENAI_MODEL': 'gpt-4o'
        }):
            call_llm("test prompt", task=None)
            mock_openai.assert_called_with("test prompt", model="gpt-4o")


if __name__ == "__main__":
    pytest.main([__file__])