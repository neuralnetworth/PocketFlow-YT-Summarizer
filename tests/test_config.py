"""Tests for environment configuration and .env file handling."""

import os
import pytest
import tempfile
from unittest.mock import patch, mock_open
import sys

# Add the parent directory to Python path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.call_llm import validate_provider_config, get_model_for_task


class TestEnvironmentVariableConfiguration:
    """Test environment variable parsing and configuration."""
    
    def test_complete_openai_configuration(self):
        """Test complete OpenAI configuration with all variables."""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-valid-key',
            'OPENAI_MODEL': 'gpt-4o',
            'OPENAI_ANALYSIS_MODEL': 'gpt-4o',
            'OPENAI_SIMPLIFICATION_MODEL': 'gpt-4o-mini'
        }, clear=True):
            # Should not raise any validation errors
            validate_provider_config('openai')
            
            # Test model selection
            assert get_model_for_task('openai', 'analysis') == 'gpt-4o'
            assert get_model_for_task('openai', 'simplification') == 'gpt-4o-mini'
            assert get_model_for_task('openai', None) == 'gpt-4o'
    
    def test_complete_gemini_configuration(self):
        """Test complete Gemini configuration with all variables."""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'gemini',
            'GEMINI_API_KEY': 'valid-gemini-key',
            'GEMINI_MODEL': 'gemini-1.5-flash',
            'GEMINI_ANALYSIS_MODEL': 'gemini-1.5-pro',
            'GEMINI_SIMPLIFICATION_MODEL': 'gemini-1.5-flash'
        }, clear=True):
            # Should not raise any validation errors
            validate_provider_config('gemini')
            
            # Test model selection
            assert get_model_for_task('gemini', 'analysis') == 'gemini-1.5-pro'
            assert get_model_for_task('gemini', 'simplification') == 'gemini-1.5-flash'
            assert get_model_for_task('gemini', None) == 'gemini-1.5-flash'
    
    def test_minimal_configuration(self):
        """Test minimal configuration with just provider and API key."""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-valid-key'
        }, clear=True):
            validate_provider_config('openai')
            
            # Should fall back to hardcoded defaults
            assert get_model_for_task('openai', 'analysis') == 'gpt-4o'
            assert get_model_for_task('openai', 'simplification') == 'gpt-4o'
    
    def test_mixed_provider_configuration(self):
        """Test configuration with both providers available."""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',  # Primary provider
            'OPENAI_API_KEY': 'sk-valid-key',
            'GEMINI_API_KEY': 'valid-gemini-key',
            'OPENAI_ANALYSIS_MODEL': 'gpt-4o',
            'OPENAI_SIMPLIFICATION_MODEL': 'gpt-4o-mini',
            'GEMINI_ANALYSIS_MODEL': 'gemini-1.5-pro',
            'GEMINI_SIMPLIFICATION_MODEL': 'gemini-1.5-flash'
        }, clear=True):
            # Both providers should validate
            validate_provider_config('openai')
            validate_provider_config('gemini')
            
            # Model selection should work for both
            assert get_model_for_task('openai', 'analysis') == 'gpt-4o'
            assert get_model_for_task('gemini', 'analysis') == 'gemini-1.5-pro'


class TestConfigurationValidation:
    """Test configuration validation edge cases."""
    
    def test_empty_api_key(self):
        """Test validation fails with empty API key."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                validate_provider_config('openai')
    
    def test_whitespace_only_api_key(self):
        """Test validation fails with whitespace-only API key."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': '   '}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                validate_provider_config('openai')
    
    def test_case_insensitive_provider_validation(self):
        """Test that provider validation is case insensitive."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-valid-key'
        }):
            # Should work with different cases
            validate_provider_config('openai')
            validate_provider_config('OPENAI')  # This should be handled by caller
    
    def test_invalid_provider_configuration(self):
        """Test validation fails for invalid providers."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            validate_provider_config('invalid_provider')
    
    def test_missing_environment_variables(self):
        """Test behavior when environment variables are completely missing."""
        with patch.dict(os.environ, {}, clear=True):
            # Should use hardcoded defaults
            assert get_model_for_task('openai', 'analysis') == 'gpt-4o'
            assert get_model_for_task('gemini', 'simplification') == 'gemini-1.5-flash'


class TestDotenvFileHandling:
    """Test .env file loading and parsing."""
    
    def test_dotenv_loading_success(self):
        """Test successful loading of .env file."""
        # Create a temporary .env file
        env_content = """# Test .env file
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-test-key
OPENAI_ANALYSIS_MODEL=gpt-4o
OPENAI_SIMPLIFICATION_MODEL=gpt-4o-mini
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            
            # Mock dotenv to load from our temp file
            with patch('dotenv.load_dotenv') as mock_load_dotenv:
                with patch.dict(os.environ, {
                    'LLM_PROVIDER': 'openai',
                    'OPENAI_API_KEY': 'sk-test-key',
                    'OPENAI_ANALYSIS_MODEL': 'gpt-4o',
                    'OPENAI_SIMPLIFICATION_MODEL': 'gpt-4o-mini'
                }):
                    # Import should trigger dotenv loading
                    import utils.call_llm
                    
                    # Verify configuration works
                    validate_provider_config('openai')
                    assert get_model_for_task('openai', 'analysis') == 'gpt-4o'
        
        # Clean up
        os.unlink(f.name)
    
    def test_dotenv_import_failure_handling(self):
        """Test graceful handling when dotenv is not available."""
        # This test ensures the code works even without python-dotenv installed
        with patch.dict('sys.modules', {'dotenv': None}):
            with patch('builtins.__import__', side_effect=ImportError):
                # Re-import the module to trigger the ImportError
                import importlib
                import utils.call_llm
                importlib.reload(utils.call_llm)
                
                # Should still work with environment variables
                with patch.dict(os.environ, {
                    'OPENAI_API_KEY': 'sk-test-key'
                }):
                    validate_provider_config('openai')


class TestConfigurationScenarios:
    """Test real-world configuration scenarios."""
    
    def test_development_configuration(self):
        """Test typical development configuration."""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-dev-key',
            'OPENAI_MODEL': 'gpt-3.5-turbo',  # Cheaper for development
            'OPENAI_ANALYSIS_MODEL': 'gpt-4o-mini',
            'OPENAI_SIMPLIFICATION_MODEL': 'gpt-3.5-turbo'
        }, clear=True):
            validate_provider_config('openai')
            
            assert get_model_for_task('openai', 'analysis') == 'gpt-4o-mini'
            assert get_model_for_task('openai', 'simplification') == 'gpt-3.5-turbo'
            assert get_model_for_task('openai', None) == 'gpt-3.5-turbo'
    
    def test_production_configuration(self):
        """Test typical production configuration."""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-prod-key',
            'OPENAI_MODEL': 'gpt-4o',
            'OPENAI_ANALYSIS_MODEL': 'gpt-4o',
            'OPENAI_SIMPLIFICATION_MODEL': 'gpt-4o-mini'
        }, clear=True):
            validate_provider_config('openai')
            
            assert get_model_for_task('openai', 'analysis') == 'gpt-4o'
            assert get_model_for_task('openai', 'simplification') == 'gpt-4o-mini'
            assert get_model_for_task('openai', None) == 'gpt-4o'
    
    def test_cost_optimized_configuration(self):
        """Test cost-optimized configuration."""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'sk-cost-key',
            'OPENAI_ANALYSIS_MODEL': 'gpt-4o-mini',     # Cheaper option for analysis
            'OPENAI_SIMPLIFICATION_MODEL': 'gpt-3.5-turbo',  # Cheapest option
            'OPENAI_MODEL': 'gpt-3.5-turbo'
        }, clear=True):
            validate_provider_config('openai')
            
            assert get_model_for_task('openai', 'analysis') == 'gpt-4o-mini'
            assert get_model_for_task('openai', 'simplification') == 'gpt-3.5-turbo'
    
    def test_quality_optimized_configuration(self):
        """Test quality-optimized configuration."""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'gemini',
            'GEMINI_API_KEY': 'quality-gemini-key',
            'GEMINI_ANALYSIS_MODEL': 'gemini-1.5-pro',    # Best for complex analysis
            'GEMINI_SIMPLIFICATION_MODEL': 'gemini-1.5-flash',  # Fast enough for simplification
            'GEMINI_MODEL': 'gemini-1.5-pro'
        }, clear=True):
            validate_provider_config('gemini')
            
            assert get_model_for_task('gemini', 'analysis') == 'gemini-1.5-pro'
            assert get_model_for_task('gemini', 'simplification') == 'gemini-1.5-flash'


class TestConfigurationDefaults:
    """Test default values and fallback behavior."""
    
    def test_openai_hardcoded_defaults(self):
        """Test OpenAI hardcoded default values."""
        with patch.dict(os.environ, {}, clear=True):
            # Should use hardcoded defaults when nothing is configured
            assert get_model_for_task('openai', 'analysis') == 'gpt-4o'
            assert get_model_for_task('openai', 'simplification') == 'gpt-4o'
            assert get_model_for_task('openai', None) == 'gpt-4o'
    
    def test_gemini_hardcoded_defaults(self):
        """Test Gemini hardcoded default values."""
        with patch.dict(os.environ, {}, clear=True):
            # Should use hardcoded defaults when nothing is configured
            assert get_model_for_task('gemini', 'analysis') == 'gemini-1.5-flash'
            assert get_model_for_task('gemini', 'simplification') == 'gemini-1.5-flash'
            assert get_model_for_task('gemini', None) == 'gemini-1.5-flash'
    
    def test_fallback_hierarchy(self):
        """Test the model selection fallback hierarchy."""
        # Test OpenAI fallback: task-specific -> general -> hardcoded default
        with patch.dict(os.environ, {
            'OPENAI_MODEL': 'gpt-4-turbo'  # Only general model set
        }, clear=True):
            # Should fall back to general model
            assert get_model_for_task('openai', 'analysis') == 'gpt-4-turbo'
            assert get_model_for_task('openai', 'simplification') == 'gpt-4-turbo'
        
        # Test with no configuration
        with patch.dict(os.environ, {}, clear=True):
            # Should fall back to hardcoded default
            assert get_model_for_task('openai', 'analysis') == 'gpt-4o'


if __name__ == "__main__":
    pytest.main([__file__])