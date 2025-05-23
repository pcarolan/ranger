import sys
from unittest.mock import MagicMock
sys.modules['smolagents'] = MagicMock()
sys.modules['smolagents.models'] = MagicMock()
sys.modules['googlemaps'] = MagicMock()

import pytest
from unittest.mock import patch, MagicMock
import os

# Mock smolagents before importing CLI
with patch('smolagents.CodeAgent'):
    with patch('smolagents.models.OpenAIServerModel'):
        from ranger.cli import CLI
        from rich.console import Console

@pytest.fixture
def cli():
    """Create a CLI instance for testing."""
    return CLI()

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'ANTHROPIC_API_KEY': 'test_claude_key',
        'GMAPS_API_KEY': 'test_gmaps_key'
    }):
        yield

def test_status_with_no_keys(cli):
    """Test status when no API keys are configured."""
    with patch('requests.get') as mock_get:
        # Mock the console to capture output
        mock_console = MagicMock(spec=Console)
        cli.console = mock_console
        
        # Call the status method
        cli.status()
        
        # Verify the console was called with a panel
        mock_console.print.assert_called_once()
        panel_call = mock_console.print.call_args[0][0]
        
        # Check that the panel contains the expected text
        panel_text = str(panel_call.renderable)
        assert "OpenAI" in panel_text
        assert "Claude" in panel_text
        assert "Google Maps" in panel_text
        assert "❌ Not configured" in panel_text

def test_status_with_all_keys(cli, mock_env_vars):
    """Test status when all API keys are configured and working."""
    with patch('requests.get') as mock_get, \
         patch('googlemaps.Client') as mock_gmaps:
        
        # Mock successful API responses
        mock_get.return_value.status_code = 200
        mock_gmaps.return_value.geocode.return_value = [{'status': 'OK'}]
        
        # Mock the console to capture output
        mock_console = MagicMock(spec=Console)
        cli.console = mock_console
        
        # Call the status method
        cli.status()
        
        # Verify the console was called with a panel
        mock_console.print.assert_called_once()
        panel_call = mock_console.print.call_args[0][0]
        
        # Check that the panel contains the expected text
        panel_text = str(panel_call.renderable)
        assert "OpenAI" in panel_text
        assert "Claude" in panel_text
        assert "Google Maps" in panel_text
        assert "✅ Connected" in panel_text

def test_status_with_api_errors(cli, mock_env_vars):
    """Test status when API calls fail."""
    with patch('requests.get') as mock_get, \
         patch('googlemaps.Client') as mock_gmaps:
        
        # Mock failed API responses
        mock_get.side_effect = Exception("API Error")
        mock_gmaps.return_value.geocode.side_effect = Exception("Geocoding Error")
        
        # Mock the console to capture output
        mock_console = MagicMock(spec=Console)
        cli.console = mock_console
        
        # Call the status method
        cli.status()
        
        # Verify the console was called with a panel
        mock_console.print.assert_called_once()
        panel_call = mock_console.print.call_args[0][0]
        
        # Check that the panel contains the expected text
        panel_text = str(panel_call.renderable)
        assert "OpenAI" in panel_text
        assert "Claude" in panel_text
        assert "Google Maps" in panel_text
        assert "❌ Error" in panel_text

def test_repl_exit(cli):
    """Test that typing 'exit' exits the REPL."""
    with patch.object(cli, 'input', side_effect=["exit"]), \
         patch.object(cli.console, 'print') as mock_print:
        cli.repl()
        # Should print goodbye message
        assert any("Goodbye" in str(call) for call in mock_print.call_args_list)

def test_repl_quit(cli):
    """Test that typing 'quit' exits the REPL."""
    with patch.object(cli, 'input', side_effect=["quit"]), \
         patch.object(cli.console, 'print') as mock_print:
        cli.repl()
        assert any("Goodbye" in str(call) for call in mock_print.call_args_list)

def test_repl_normal_input(cli):
    """Test normal input and response rendering in the REPL."""
    with patch.object(cli, 'input', side_effect=["hello", "exit"]), \
         patch.object(cli.console, 'print') as mock_print, \
         patch.object(cli.router, 'route', return_value=("response", "thoughts")):
        cli.debug = True
        cli.repl()
        # Should print the response and thoughts
        found_response = False
        found_thoughts = False
        for call in mock_print.call_args_list:
            panel = call[0][0]
            # Check if it's a Panel and has a renderable attribute
            if hasattr(panel, 'renderable'):
                text = str(panel.renderable)
                if "response" in text:
                    found_response = True
                if "thoughts" in text:
                    found_thoughts = True
        assert found_response
        assert found_thoughts

def test_repl_keyboard_interrupt(cli):
    """Test REPL handles KeyboardInterrupt gracefully."""
    with patch.object(cli, 'input', side_effect=KeyboardInterrupt), \
         patch.object(cli.console, 'print') as mock_print:
        cli.repl()
        assert any("Goodbye" in str(call) for call in mock_print.call_args_list)

def test_repl_eof_error(cli):
    """Test REPL handles EOFError gracefully."""
    with patch.object(cli, 'input', side_effect=EOFError), \
         patch.object(cli.console, 'print') as mock_print:
        cli.repl()
        assert any("Goodbye" in str(call) for call in mock_print.call_args_list) 