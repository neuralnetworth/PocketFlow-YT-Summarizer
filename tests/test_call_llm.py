"""Tests for the LLM calling functionality including task-specific model selection."""

import os
import pytest
from unittest.mock import patch, MagicMock
import sys
import tempfile

# Add the parent directory to Python path so we can import from utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.call_llm import (
    get_model_for_task,
    validate_provider_config,
    call_llm,
    call_llm_openai,
    call_llm_gemini,
    test_provider
)


class TestGetModelForTask:
    """Test the get_model_for_task function for task-specific model selection."""
    
    def test_openai_analysis_task(self):
        """Test that analysis tasks use the analysis model for OpenAI."""
        with patch.dict(os.environ, {
            'OPENAI_ANALYSIS_MODEL': 'gpt-4o',
            'OPENAI_MODEL': 'gpt-3.5-turbo'
        }):
            model = get_model_for_task('openai', 'analysis')
            assert model == 'gpt-4o'
    
    def test_openai_simplification_task(self):
        """Test that simplification tasks use the simplification model for OpenAI."""
        with patch.dict(os.environ, {
            'OPENAI_SIMPLIFICATION_MODEL': 'gpt-4o-mini',
            'OPENAI_MODEL': 'gpt-3.5-turbo'
        }):
            model = get_model_for_task('openai', 'simplification')
            assert model == 'gpt-4o-mini'
    
    def test_gemini_analysis_task(self):
        """Test that analysis tasks use the analysis model for Gemini."""
        with patch.dict(os.environ, {
            'GEMINI_ANALYSIS_MODEL': 'gemini-1.5-pro',
            'GEMINI_MODEL': 'gemini-1.5-flash'
        }):
            model = get_model_for_task('gemini', 'analysis')
            assert model == 'gemini-1.5-pro'
    
    def test_gemini_simplification_task(self):
        """Test that simplification tasks use the simplification model for Gemini."""
        with patch.dict(os.environ, {
            'GEMINI_SIMPLIFICATION_MODEL': 'gemini-1.5-flash',
            'GEMINI_MODEL': 'gemini-1.5-pro'
        }):
            model = get_model_for_task('gemini', 'simplification')
            assert model == 'gemini-1.5-flash'
    
    def test_fallback_to_general_model_openai(self):
        """Test fallback to general model when task-specific model not configured."""
        with patch.dict(os.environ, {
            'OPENAI_MODEL': 'gpt-4o'
        }, clear=True):
            # Clear any task-specific models
            os.environ.pop('OPENAI_ANALYSIS_MODEL', None)
            model = get_model_for_task('openai', 'analysis')
            assert model == 'gpt-4o'
    
    def test_fallback_to_general_model_gemini(self):
        """Test fallback to general model when task-specific model not configured."""
        with patch.dict(os.environ, {
            'GEMINI_MODEL': 'gemini-1.5-flash'
        }, clear=True):
            # Clear any task-specific models
            os.environ.pop('GEMINI_ANALYSIS_MODEL', None)
            model = get_model_for_task('gemini', 'analysis')
            assert model == 'gemini-1.5-flash'
    
    def test_fallback_to_default_model(self):
        """Test fallback to hardcoded default when no models configured."""
        with patch.dict(os.environ, {}, clear=True):
            model = get_model_for_task('openai', 'analysis')
            assert model == 'gpt-4o'  # Default OpenAI model
            
            model = get_model_for_task('gemini', 'simplification')
            assert model == 'gemini-1.5-flash'  # Default Gemini model
    
    def test_case_insensitive_task(self):
        """Test that task parameter is case insensitive."""
        with patch.dict(os.environ, {
            'OPENAI_ANALYSIS_MODEL': 'gpt-4o'
        }):
            model = get_model_for_task('openai', 'ANALYSIS')
            assert model == 'gpt-4o'
            
            model = get_model_for_task('openai', 'analysis')
            assert model == 'gpt-4o'
    
    def test_no_task_specified(self):
        """Test behavior when no task is specified."""
        with patch.dict(os.environ, {
            'OPENAI_MODEL': 'gpt-4o'
        }):
            model = get_model_for_task('openai', None)
            assert model == 'gpt-4o'
    
    def test_unsupported_provider(self):
        """Test error handling for unsupported providers."""
        with pytest.raises(ValueError, match="Unsupported provider: invalid"):
            get_model_for_task('invalid', 'analysis')


class TestValidateProviderConfig:
    """Test provider configuration validation."""
    
    def test_valid_openai_config(self):
        """Test validation passes with valid OpenAI API key."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-valid-key'}):
            # Should not raise an exception
            validate_provider_config('openai')
    
    def test_valid_gemini_config(self):
        """Test validation passes with valid Gemini API key."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'valid-gemini-key'}):
            # Should not raise an exception
            validate_provider_config('gemini')
    
    def test_missing_openai_key(self):
        """Test validation fails with missing OpenAI API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                validate_provider_config('openai')
    
    def test_placeholder_openai_key(self):
        """Test validation fails with placeholder OpenAI API key."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'your_openai_api_key_here'}):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                validate_provider_config('openai')
    
    def test_missing_gemini_key(self):
        """Test validation fails with missing Gemini API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Gemini API key is required"):
                validate_provider_config('gemini')
    
    def test_placeholder_gemini_key(self):
        """Test validation fails with placeholder Gemini API key."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'your_gemini_api_key_here'}):
            with pytest.raises(ValueError, match="Gemini API key is required"):
                validate_provider_config('gemini')
    
    def test_unsupported_provider(self):
        """Test validation fails for unsupported providers."""
        with pytest.raises(ValueError, match="Unsupported provider: invalid"):
            validate_provider_config('invalid')


class TestCallLLM:
    """Test the main call_llm function."""
    
    @patch('utils.call_llm.call_llm_openai')
    def test_call_llm_openai_provider(self, mock_openai):
        """Test that call_llm uses OpenAI when configured."""
        mock_openai.return_value = "Test response"
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-valid-key',
            'OPENAI_ANALYSIS_MODEL': 'gpt-4o'
        }):
            result = call_llm("test prompt", task="analysis")
            
            assert result == "Test response"
            mock_openai.assert_called_once_with("test prompt", model="gpt-4o")
    
    @patch('utils.call_llm.call_llm_gemini')
    def test_call_llm_gemini_provider(self, mock_gemini):
        """Test that call_llm uses Gemini when configured."""
        mock_gemini.return_value = "Test response"
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'gemini',
            'GEMINI_API_KEY': 'valid-gemini-key',
            'GEMINI_SIMPLIFICATION_MODEL': 'gemini-1.5-flash'
        }):
            result = call_llm("test prompt", task="simplification")
            
            assert result == "Test response"
            mock_gemini.assert_called_once_with("test prompt", model="gemini-1.5-flash")
    
    def test_call_llm_default_provider(self):
        """Test that call_llm defaults to OpenAI when no provider specified."""
        with patch('utils.call_llm.call_llm_openai') as mock_openai, \
             patch.dict(os.environ, {
                 'OPENAI_API_KEY': 'sk-valid-key'
             }):
            mock_openai.return_value = "Test response"
            
            # Clear LLM_PROVIDER to test default
            os.environ.pop('LLM_PROVIDER', None)
            
            call_llm("test prompt")
            mock_openai.assert_called_once()
    
    def test_call_llm_validation_failure(self):
        """Test that call_llm raises error when validation fails."""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai'
        }, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                call_llm("test prompt")


class TestLLMProviderFunctions:
    """Test individual provider functions with mocking."""
    
    @patch('utils.call_llm.OpenAI')
    def test_call_llm_openai_success(self, mock_openai_class):
        """Test successful OpenAI API call."""
        # Mock the OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-valid-key'}):
            result = call_llm_openai("test prompt", model="gpt-4o")
            
            assert result == "Test response"
            mock_client.chat.completions.create.assert_called_once()
    
    @patch('utils.call_llm.genai')
    def test_call_llm_gemini_success(self, mock_genai):
        """Test successful Gemini API call."""
        # Mock the Gemini model and response
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        mock_response = MagicMock()
        mock_response.text = "Test response"
        mock_model.generate_content.return_value = mock_response
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'valid-gemini-key'}):
            result = call_llm_gemini("test prompt", model="gemini-1.5-flash")
            
            assert result == "Test response"
            mock_genai.configure.assert_called_once_with(api_key='valid-gemini-key')
            mock_model.generate_content.assert_called_once()
    
    @patch('utils.call_llm.OpenAI')
    def test_call_llm_openai_retry_logic(self, mock_openai_class):
        """Test retry logic for OpenAI API failures."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # First two calls fail, third succeeds
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error"),
            Exception("API Error"),
            MagicMock(choices=[MagicMock(message=MagicMock(content="Success"))])
        ]
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-valid-key'}):
            result = call_llm_openai("test prompt", max_retries=3)
            
            assert result == "Success"
            assert mock_client.chat.completions.create.call_count == 3


class TestTestProvider:
    """Test the provider testing functionality."""
    
    @patch('utils.call_llm.call_llm')
    def test_test_provider_success(self, mock_call_llm):
        """Test successful provider test."""
        mock_call_llm.return_value = "success"
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-valid-key'
        }):
            result = test_provider('openai')
            
            assert result is True
            mock_call_llm.assert_called_once()
    
    @patch('utils.call_llm.call_llm')
    def test_test_provider_failure(self, mock_call_llm):
        """Test provider test failure."""
        mock_call_llm.side_effect = Exception("API Error")
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-valid-key'
        }):
            result = test_provider('openai')
            
            assert result is False
    
    def test_test_provider_restores_original_provider(self):
        """Test that test_provider restores the original LLM_PROVIDER setting."""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'gemini',
            'OPENAI_API_KEY': 'sk-valid-key'
        }):
            with patch('utils.call_llm.call_llm'):
                test_provider('openai')
                
                # Should restore to original provider
                assert os.environ['LLM_PROVIDER'] == 'gemini'


if __name__ == "__main__":
    pytest.main([__file__])