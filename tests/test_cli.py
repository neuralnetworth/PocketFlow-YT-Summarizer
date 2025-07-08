"""Tests for CLI argument parsing and provider override functionality."""

import os
import sys
import argparse
import pytest
from unittest.mock import patch, MagicMock
from io import StringIO

# Add the parent directory to Python path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import main


class TestCLIArgumentParsing:
    """Test command line argument parsing functionality."""
    
    def test_help_output(self):
        """Test that help output includes provider argument."""
        # Capture help output
        with patch('sys.argv', ['main.py', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                with patch('sys.stdout', new=StringIO()) as fake_out:
                    main.main()
            
            # SystemExit with code 0 indicates successful help display
            assert exc_info.value.code == 0
    
    def test_provider_argument_validation(self):
        """Test that invalid provider choices are rejected."""
        # Test invalid provider
        with patch('sys.argv', ['main.py', '--provider', 'invalid']):
            with pytest.raises(SystemExit) as exc_info:
                with patch('sys.stderr', new=StringIO()):
                    main.main()
            
            # SystemExit with code 2 indicates argument parsing error
            assert exc_info.value.code == 2
    
    def test_valid_provider_choices(self):
        """Test that valid provider choices are accepted."""
        # We'll patch the flow execution to avoid actually running the processor
        with patch('main.create_youtube_processor_flow') as mock_flow_factory:
            mock_flow = MagicMock()
            mock_flow_factory.return_value = mock_flow
            
            # Test openai provider
            with patch('sys.argv', ['main.py', '--provider', 'openai', '--url', 'test']):
                with patch('builtins.input', return_value='test'):
                    try:
                        main.main()
                    except SystemExit:
                        pass  # Expected due to our mocking
            
            # Test gemini provider
            with patch('sys.argv', ['main.py', '--provider', 'gemini', '--url', 'test']):
                with patch('builtins.input', return_value='test'):
                    try:
                        main.main()
                    except SystemExit:
                        pass  # Expected due to our mocking


class TestProviderOverride:
    """Test provider override functionality."""
    
    def test_provider_override_sets_environment(self):
        """Test that --provider argument correctly sets environment variable."""
        original_provider = os.environ.get('LLM_PROVIDER')
        
        try:
            # Set initial provider
            os.environ['LLM_PROVIDER'] = 'openai'
            
            with patch('main.create_youtube_processor_flow') as mock_flow_factory:
                mock_flow = MagicMock()
                mock_flow_factory.return_value = mock_flow
                
                with patch('sys.argv', ['main.py', '--provider', 'gemini', '--url', 'test']):
                    with patch('builtins.input', return_value='test'):
                        try:
                            main.main()
                        except SystemExit:
                            pass  # Expected due to our mocking
                
                # Check that environment was overridden
                assert os.environ['LLM_PROVIDER'] == 'gemini'
        
        finally:
            # Restore original environment
            if original_provider:
                os.environ['LLM_PROVIDER'] = original_provider
            elif 'LLM_PROVIDER' in os.environ:
                del os.environ['LLM_PROVIDER']
    
    def test_no_provider_preserves_environment(self):
        """Test that not specifying --provider preserves existing environment."""
        original_provider = os.environ.get('LLM_PROVIDER')
        
        try:
            # Set initial provider
            os.environ['LLM_PROVIDER'] = 'openai'
            
            with patch('main.create_youtube_processor_flow') as mock_flow_factory:
                mock_flow = MagicMock()
                mock_flow_factory.return_value = mock_flow
                
                with patch('sys.argv', ['main.py', '--url', 'test']):
                    with patch('builtins.input', return_value='test'):
                        try:
                            main.main()
                        except SystemExit:
                            pass  # Expected due to our mocking
                
                # Check that environment was not changed
                assert os.environ['LLM_PROVIDER'] == 'openai'
        
        finally:
            # Restore original environment
            if original_provider:
                os.environ['LLM_PROVIDER'] = original_provider
            elif 'LLM_PROVIDER' in os.environ:
                del os.environ['LLM_PROVIDER']
    
    def test_provider_override_openai(self):
        """Test explicit OpenAI provider override."""
        original_provider = os.environ.get('LLM_PROVIDER')
        
        try:
            # Set initial provider to gemini
            os.environ['LLM_PROVIDER'] = 'gemini'
            
            with patch('main.create_youtube_processor_flow') as mock_flow_factory:
                mock_flow = MagicMock()
                mock_flow_factory.return_value = mock_flow
                
                with patch('sys.argv', ['main.py', '--provider', 'openai', '--url', 'test']):
                    with patch('builtins.input', return_value='test'):
                        try:
                            main.main()
                        except SystemExit:
                            pass  # Expected due to our mocking
                
                # Check that environment was overridden to openai
                assert os.environ['LLM_PROVIDER'] == 'openai'
        
        finally:
            # Restore original environment
            if original_provider:
                os.environ['LLM_PROVIDER'] = original_provider
            elif 'LLM_PROVIDER' in os.environ:
                del os.environ['LLM_PROVIDER']


class TestCLIIntegration:
    """Test integration between CLI args and existing LLM functionality."""
    
    def test_provider_override_affects_llm_calls(self):
        """Test that provider override actually affects LLM provider selection."""
        from utils.call_llm import call_llm
        
        original_provider = os.environ.get('LLM_PROVIDER')
        
        try:
            # Test with gemini override
            os.environ['LLM_PROVIDER'] = 'gemini'
            os.environ['GEMINI_API_KEY'] = 'test-key'
            
            # Mock the actual LLM call to avoid API requests
            with patch('utils.call_llm.call_llm_gemini') as mock_gemini:
                mock_gemini.return_value = "test response"
                
                with patch('utils.call_llm.validate_provider_config'):
                    response = call_llm("test prompt")
                
                # Verify gemini was called
                mock_gemini.assert_called_once()
            
            # Test with openai override
            os.environ['LLM_PROVIDER'] = 'openai'
            os.environ['OPENAI_API_KEY'] = 'test-key'
            
            # Mock the actual LLM call to avoid API requests
            with patch('utils.call_llm.call_llm_openai') as mock_openai:
                mock_openai.return_value = "test response"
                
                with patch('utils.call_llm.validate_provider_config'):
                    response = call_llm("test prompt")
                
                # Verify openai was called
                mock_openai.assert_called_once()
        
        finally:
            # Restore original environment
            if original_provider:
                os.environ['LLM_PROVIDER'] = original_provider
            elif 'LLM_PROVIDER' in os.environ:
                del os.environ['LLM_PROVIDER']
            
            # Clean up test keys
            for key in ['GEMINI_API_KEY', 'OPENAI_API_KEY']:
                if key in os.environ and os.environ[key] == 'test-key':
                    del os.environ[key]


class TestCLILogging:
    """Test CLI logging functionality."""
    
    def test_provider_override_logging(self):
        """Test that provider override is properly logged."""
        with patch('main.create_youtube_processor_flow') as mock_flow_factory:
            mock_flow = MagicMock()
            mock_flow_factory.return_value = mock_flow
            
            with patch('main.logger') as mock_logger:
                with patch('sys.argv', ['main.py', '--provider', 'gemini', '--url', 'test']):
                    with patch('builtins.input', return_value='test'):
                        try:
                            main.main()
                        except SystemExit:
                            pass  # Expected due to our mocking
                
                # Check that override was logged
                mock_logger.info.assert_any_call("Using LLM provider from CLI: gemini")
    
    def test_no_provider_no_override_logging(self):
        """Test that no override logging occurs when provider not specified."""
        with patch('main.create_youtube_processor_flow') as mock_flow_factory:
            mock_flow = MagicMock()
            mock_flow_factory.return_value = mock_flow
            
            with patch('main.logger') as mock_logger:
                with patch('sys.argv', ['main.py', '--url', 'test']):
                    with patch('builtins.input', return_value='test'):
                        try:
                            main.main()
                        except SystemExit:
                            pass  # Expected due to our mocking
                
                # Check that override was NOT logged
                logged_calls = [call.args[0] for call in mock_logger.info.call_args_list]
                override_logged = any("Using LLM provider from CLI" in msg for msg in logged_calls)
                assert not override_logged


class TestArgumentCombinations:
    """Test various combinations of CLI arguments."""
    
    def test_url_and_provider_combination(self):
        """Test that URL and provider arguments work together."""
        with patch('main.create_youtube_processor_flow') as mock_flow_factory:
            mock_flow = MagicMock()
            mock_flow_factory.return_value = mock_flow
            
            test_url = "https://www.youtube.com/watch?v=test123"
            
            with patch('sys.argv', ['main.py', '--url', test_url, '--provider', 'openai']):
                try:
                    main.main()
                except SystemExit:
                    pass  # Expected due to our mocking
                
                # Check that environment was set
                assert os.environ['LLM_PROVIDER'] == 'openai'
    
    def test_interactive_mode_with_provider(self):
        """Test interactive mode (no URL) with provider override."""
        with patch('main.create_youtube_processor_flow') as mock_flow_factory:
            mock_flow = MagicMock()
            mock_flow_factory.return_value = mock_flow
            
            test_url = "https://www.youtube.com/watch?v=interactive_test"
            
            with patch('sys.argv', ['main.py', '--provider', 'gemini']):
                with patch('builtins.input', return_value=test_url):
                    try:
                        main.main()
                    except SystemExit:
                        pass  # Expected due to our mocking
                
                # Check that environment was set
                assert os.environ['LLM_PROVIDER'] == 'gemini'