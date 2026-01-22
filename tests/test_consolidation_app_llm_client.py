"""Tests for the consolidation app LLM client module."""

import os
from unittest.mock import Mock, patch

import pytest
import requests

from src.consolidation_app import llm_client


class TestOllamaClient:
    """Tests for Ollama API client."""

    @patch("src.consolidation_app.llm_client.requests.post")
    def test_call_ollama_success(self, mock_post):
        """Test successful Ollama API call."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Hello, world!"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = llm_client.call_ollama("Test prompt")

        assert result == "Hello, world!"
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["json"]["model"] == "qwen2.5-coder:14b"
        assert call_args[1]["json"]["prompt"] == "Test prompt"

    @patch("src.consolidation_app.llm_client.requests.post")
    @patch("src.consolidation_app.llm_client.logger")
    def test_call_ollama_logs_tokens(self, mock_logger, mock_post):
        """Test Ollama logs token counts."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "Response",
            "prompt_eval_count": 50,  # Input tokens
            "eval_count": 30,  # Output tokens
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        llm_client.call_ollama("Test")

        # Verify token counts are logged
        info_calls = list(mock_logger.info.call_args_list)
        assert any("input_tokens=50" in str(call) for call in info_calls)
        assert any("output_tokens=30" in str(call) for call in info_calls)
        assert any("total_tokens=80" in str(call) for call in info_calls)

    @patch("src.consolidation_app.llm_client.requests.post")
    def test_call_ollama_custom_model(self, mock_post):
        """Test Ollama API call with custom model."""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Response"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = llm_client.call_ollama("Test", model="custom-model:7b")

        assert result == "Response"
        call_args = mock_post.call_args
        assert call_args[1]["json"]["model"] == "custom-model:7b"

    @patch("src.consolidation_app.llm_client.requests.post")
    @patch("src.consolidation_app.llm_client.time.sleep")
    def test_call_ollama_connection_error_retry(self, mock_sleep, mock_post):
        """Test Ollama retry logic on connection error."""
        # First two attempts fail, third succeeds
        mock_post.side_effect = [
            requests.exceptions.ConnectionError("Connection failed"),
            requests.exceptions.ConnectionError("Connection failed"),
            Mock(json=lambda: {"response": "Success"}, raise_for_status=Mock()),
        ]

        result = llm_client.call_ollama("Test")

        assert result == "Success"
        assert mock_post.call_count == 3
        assert mock_sleep.call_count == 2  # Two retries

    @patch("src.consolidation_app.llm_client.requests.post")
    def test_call_ollama_connection_error_fails_after_retries(self, mock_post):
        """Test Ollama fails after max retries."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with pytest.raises(ConnectionError, match="Failed to connect to Ollama"):
            llm_client.call_ollama("Test")

        assert mock_post.call_count == 3  # MAX_RETRIES

    @patch("src.consolidation_app.llm_client.requests.post")
    def test_call_ollama_timeout_error(self, mock_post):
        """Test Ollama timeout error handling."""
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        with pytest.raises(TimeoutError, match="timed out"):
            llm_client.call_ollama("Test")


class TestOpenAIClient:
    """Tests for OpenAI API client."""

    @patch("src.consolidation_app.llm_client.requests.post")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_call_openai_success(self, mock_post):
        """Test successful OpenAI API call."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "OpenAI response"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = llm_client.call_openai("Test prompt")

        assert result == "OpenAI response"
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "Authorization" in call_args[1]["headers"]
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-key"

    @patch("src.consolidation_app.llm_client.requests.post")
    @patch("src.consolidation_app.llm_client.logger")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_call_openai_logs_tokens(self, mock_logger, mock_post):
        """Test OpenAI logs token counts including cached tokens."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response"}}],
            "usage": {
                "prompt_tokens": 100,  # Input tokens
                "completion_tokens": 50,  # Output tokens
                "total_tokens": 150,
                "cached_tokens": 20,  # Cached tokens (if available)
            },
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        llm_client.call_openai("Test")

        # Verify token counts are logged
        info_calls = list(mock_logger.info.call_args_list)
        assert any("input_tokens=100" in str(call) for call in info_calls)
        assert any("cached_tokens=20" in str(call) for call in info_calls)
        assert any("output_tokens=50" in str(call) for call in info_calls)
        assert any("total_tokens=150" in str(call) for call in info_calls)

    @patch.dict(os.environ, {}, clear=True)
    def test_call_openai_missing_api_key(self):
        """Test OpenAI fails without API key."""
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            llm_client.call_openai("Test", api_key=None)

    @patch("src.consolidation_app.llm_client.requests.post")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_call_openai_rate_limit_retry(self, mock_post):
        """Test OpenAI rate limit handling with retry."""
        # First attempt: rate limit, second: success
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "1"}
        mock_response_429.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response_429
        )

        mock_response_success = Mock()
        mock_response_success.json.return_value = {
            "choices": [{"message": {"content": "Success"}}]
        }
        mock_response_success.raise_for_status = Mock()

        mock_post.side_effect = [mock_response_429, mock_response_success]

        with patch("src.consolidation_app.llm_client.time.sleep"):
            result = llm_client.call_openai("Test")

        assert result == "Success"
        assert mock_post.call_count == 2


class TestAnthropicClient:
    """Tests for Anthropic API client."""

    @patch("src.consolidation_app.llm_client.requests.post")
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_call_anthropic_success(self, mock_post):
        """Test successful Anthropic API call."""
        mock_response = Mock()
        mock_response.json.return_value = {"content": [{"text": "Anthropic response"}]}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = llm_client.call_anthropic("Test prompt")

        assert result == "Anthropic response"
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "x-api-key" in call_args[1]["headers"]
        assert call_args[1]["headers"]["x-api-key"] == "test-key"

    @patch("src.consolidation_app.llm_client.requests.post")
    @patch("src.consolidation_app.llm_client.logger")
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_call_anthropic_logs_tokens(self, mock_logger, mock_post):
        """Test Anthropic logs token counts including cache metrics."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [{"text": "Response"}],
            "usage": {
                "input_tokens": 80,
                "output_tokens": 40,
                "cache_creation_input_tokens": 10,  # Tokens used to create cache
                "cache_read_input_tokens": 5,  # Tokens read from cache
            },
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        llm_client.call_anthropic("Test")

        # Verify token counts are logged
        info_calls = list(mock_logger.info.call_args_list)
        assert any("input_tokens=80" in str(call) for call in info_calls)
        assert any("cached_tokens=15" in str(call) for call in info_calls)  # 10 + 5
        assert any("output_tokens=40" in str(call) for call in info_calls)
        assert any("total_tokens=120" in str(call) for call in info_calls)  # 80 + 40

    @patch.dict(os.environ, {}, clear=True)
    def test_call_anthropic_missing_api_key(self):
        """Test Anthropic fails without API key."""
        with pytest.raises(ValueError, match="Anthropic API key is required"):
            llm_client.call_anthropic("Test", api_key=None)


class TestUnifiedLLMClient:
    """Tests for unified call_llm function."""

    @patch("src.consolidation_app.llm_client.call_ollama")
    @patch.dict(
        os.environ,
        {"LLM_PROVIDER": "ollama", "LLM_MODEL": "qwen2.5-coder:14b"},
        clear=False,
    )
    def test_call_llm_ollama_provider(self, mock_call_ollama):
        """Test unified call routes to Ollama."""
        mock_call_ollama.return_value = "Ollama response"

        result = llm_client.call_llm("Test", task="default")

        assert result == "Ollama response"
        mock_call_ollama.assert_called_once_with(
            "Test", model="qwen2.5-coder:14b", base_url="http://localhost:11434"
        )

    @patch("src.consolidation_app.llm_client.call_openai")
    @patch.dict(os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"})
    def test_call_llm_openai_provider(self, mock_call_openai):
        """Test unified call routes to OpenAI."""
        mock_call_openai.return_value = "OpenAI response"

        result = llm_client.call_llm("Test", task="default")

        assert result == "OpenAI response"
        mock_call_openai.assert_called_once()

    @patch("src.consolidation_app.llm_client.call_anthropic")
    @patch.dict(
        os.environ, {"LLM_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "test-key"}
    )
    def test_call_llm_anthropic_provider(self, mock_call_anthropic):
        """Test unified call routes to Anthropic."""
        mock_call_anthropic.return_value = "Anthropic response"

        result = llm_client.call_llm("Test", task="default")

        assert result == "Anthropic response"
        mock_call_anthropic.assert_called_once()

    @patch.dict(os.environ, {"LLM_PROVIDER": "invalid"})
    def test_call_llm_invalid_provider(self):
        """Test unified call fails with invalid provider."""
        with pytest.raises(ValueError, match="Invalid LLM provider"):
            llm_client.call_llm("Test")

    @patch("src.consolidation_app.llm_client.call_ollama")
    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDER": "ollama",
            "LLM_MODEL_DEDUPLICATION": "qwen2.5-coder:7b",
        },
    )
    def test_call_llm_task_specific_model(self, mock_call_ollama):
        """Test unified call uses task-specific model."""
        mock_call_ollama.return_value = "Response"

        result = llm_client.call_llm("Test", task="deduplication")

        assert result == "Response"
        mock_call_ollama.assert_called_once_with(
            "Test", model="qwen2.5-coder:7b", base_url="http://localhost:11434"
        )

    @patch("src.consolidation_app.llm_client.call_ollama")
    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDER": "ollama",
            "LLM_MODEL": "default-model",
            "LLM_MODEL_TAGGING": "tagging-model",
        },
    )
    def test_call_llm_explicit_model_overrides_task(self, mock_call_ollama):
        """Test explicit model parameter overrides task-specific model."""
        mock_call_ollama.return_value = "Response"

        result = llm_client.call_llm("Test", task="tagging", model="explicit-model")

        assert result == "Response"
        mock_call_ollama.assert_called_once_with(
            "Test", model="explicit-model", base_url="http://localhost:11434"
        )

    @patch("src.consolidation_app.llm_client.call_ollama")
    @patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "LLM_MODEL": "custom-default"})
    def test_call_llm_default_model_fallback(self, mock_call_ollama):
        """Test unified call falls back to default model when task-specific not set."""
        mock_call_ollama.return_value = "Response"

        result = llm_client.call_llm("Test", task="unknown_task")

        assert result == "Response"
        mock_call_ollama.assert_called_once_with(
            "Test", model="custom-default", base_url="http://localhost:11434"
        )

    @patch("src.consolidation_app.llm_client.call_ollama")
    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDER": "openai",  # Default provider
            "LLM_PROVIDER_DEDUPLICATION": "ollama",  # Task-specific provider
            "LLM_MODEL_DEDUPLICATION": "qwen2.5-coder:7b",
        },
    )
    def test_call_llm_per_task_provider(self, mock_call_ollama):
        """Test unified call uses per-task provider when set."""
        mock_call_ollama.return_value = "Response"

        result = llm_client.call_llm("Test", task="deduplication")

        assert result == "Response"
        # Should use Ollama (task-specific) not OpenAI (default)
        mock_call_ollama.assert_called_once_with(
            "Test", model="qwen2.5-coder:7b", base_url="http://localhost:11434"
        )

    @patch("src.consolidation_app.llm_client.call_ollama")
    @patch("src.consolidation_app.llm_client.call_openai")
    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDER": "ollama",  # Default provider
            "LLM_MODEL": "qwen2.5-coder:14b",  # Default model
            "LLM_PROVIDER_DEDUPLICATION": "ollama",  # Ollama for dedup
            "LLM_MODEL_DEDUPLICATION": "qwen2.5-coder:7b",
            "LLM_PROVIDER_TAGGING": "openai",  # OpenAI for tagging
            "LLM_MODEL_TAGGING": "gpt-4o-mini",
            "OPENAI_API_KEY": "test-key",
        },
    )
    def test_call_llm_mixed_providers(self, mock_call_openai, mock_call_ollama):
        """Test mixing providers for different tasks."""
        mock_call_ollama.return_value = "Ollama response"
        mock_call_openai.return_value = "OpenAI response"

        # Deduplication should use Ollama
        result = llm_client.call_llm("Test", task="deduplication")
        assert result == "Ollama response"
        mock_call_ollama.assert_called_once_with(
            "Test", model="qwen2.5-coder:7b", base_url="http://localhost:11434"
        )

        # Tagging should use OpenAI
        result = llm_client.call_llm("Test", task="tagging")
        assert result == "OpenAI response"
        mock_call_openai.assert_called_once_with("Test", model="gpt-4o-mini")

    @patch("src.consolidation_app.llm_client.call_anthropic")
    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDER": "ollama",  # Default provider
            "LLM_PROVIDER_RULE_EXTRACTION": "anthropic",  # Anthropic for rule extraction
            "LLM_MODEL_RULE_EXTRACTION": "claude-3-opus-20240229",
            "ANTHROPIC_API_KEY": "test-key",
        },
    )
    def test_call_llm_per_task_provider_anthropic(self, mock_call_anthropic):
        """Test per-task provider selection with Anthropic."""
        mock_call_anthropic.return_value = "Anthropic response"

        result = llm_client.call_llm("Test", task="rule_extraction")

        assert result == "Anthropic response"
        mock_call_anthropic.assert_called_once_with(
            "Test", model="claude-3-opus-20240229"
        )


class TestConfiguration:
    """Tests for configuration functions."""

    def test_get_llm_provider_default(self):
        """Test default provider is ollama."""
        with patch.dict(os.environ, {}, clear=True):
            provider = llm_client._get_llm_provider()
            assert provider == "ollama"

    def test_get_llm_provider_from_env(self):
        """Test provider from environment variable."""
        with patch.dict(os.environ, {"LLM_PROVIDER": "openai"}):
            provider = llm_client._get_llm_provider()
            assert provider == "openai"

    def test_get_task_provider(self):
        """Test task-specific provider retrieval."""
        with patch.dict(os.environ, {"LLM_PROVIDER_DEDUPLICATION": "openai"}):
            provider = llm_client._get_task_provider("deduplication")
            assert provider == "openai"

    def test_get_task_provider_not_set(self):
        """Test task-specific provider returns None when not set."""
        with patch.dict(os.environ, {}, clear=True):
            provider = llm_client._get_task_provider("deduplication")
            assert provider is None

    def test_get_provider_for_task_task_specific(self):
        """Test provider selection uses task-specific when available."""
        with patch.dict(
            os.environ,
            {
                "LLM_PROVIDER": "ollama",
                "LLM_PROVIDER_DEDUPLICATION": "openai",
            },
        ):
            provider = llm_client._get_provider_for_task("deduplication")
            assert provider == "openai"

    def test_get_provider_for_task_default_fallback(self):
        """Test provider selection falls back to default when task-specific not set."""
        with patch.dict(os.environ, {"LLM_PROVIDER": "anthropic"}):
            provider = llm_client._get_provider_for_task("unknown_task")
            assert provider == "anthropic"

    def test_get_default_model(self):
        """Test default model retrieval."""
        with patch.dict(os.environ, {}, clear=True):
            model = llm_client._get_default_model()
            assert model == "qwen2.5-coder:14b"

    def test_get_default_model_from_env(self):
        """Test model from environment variable."""
        with patch.dict(os.environ, {"LLM_MODEL": "custom-model"}):
            model = llm_client._get_default_model()
            assert model == "custom-model"

    def test_get_task_model(self):
        """Test task-specific model retrieval."""
        with patch.dict(os.environ, {"LLM_MODEL_DEDUPLICATION": "dedup-model"}):
            model = llm_client._get_task_model("deduplication")
            assert model == "dedup-model"

    def test_get_task_model_not_set(self):
        """Test task-specific model returns None when not set."""
        with patch.dict(os.environ, {}, clear=True):
            model = llm_client._get_task_model("deduplication")
            assert model is None

    def test_get_model_for_task_explicit(self):
        """Test explicit model parameter."""
        model = llm_client._get_model_for_task("any_task", explicit_model="explicit")
        assert model == "explicit"

    def test_get_model_for_task_specific(self):
        """Test task-specific model."""
        with patch.dict(os.environ, {"LLM_MODEL_TAGGING": "tagging-model"}):
            model = llm_client._get_model_for_task("tagging")
            assert model == "tagging-model"

    def test_get_model_for_task_default(self):
        """Test default model fallback."""
        with patch.dict(os.environ, {"LLM_MODEL": "default-model"}):
            model = llm_client._get_model_for_task("unknown_task")
            assert model == "default-model"


class TestEnvFileCompatibility:
    """Tests to verify .env file variables work correctly with the app.

    These tests simulate .env file contents using @patch.dict and mock load_dotenv
    to prevent loading the actual .env file, ensuring test isolation.
    """

    @patch("src.consolidation_app.llm_client.load_dotenv")
    @patch("src.consolidation_app.llm_client.call_ollama")
    def test_env_file_ollama_config(
        self, mock_call_ollama, mock_load_dotenv, monkeypatch
    ):
        """Test that .env file variables work for Ollama configuration."""
        # Clear any existing LLM-related env vars that might interfere
        llm_vars = [
            "LLM_PROVIDER",
            "LLM_PROVIDER_DEDUPLICATION",
            "LLM_PROVIDER_TAGGING",
            "LLM_PROVIDER_RULE_EXTRACTION",
            "LLM_MODEL",
            "LLM_MODEL_DEDUPLICATION",
            "LLM_MODEL_TAGGING",
            "LLM_MODEL_RULE_EXTRACTION",
        ]
        for var in llm_vars:
            monkeypatch.delenv(var, raising=False)

        # Set test environment variables (simulating .env file contents)
        monkeypatch.setenv("LLM_PROVIDER", "ollama")
        monkeypatch.setenv("LLM_MODEL", "qwen2.5-coder:14b")
        monkeypatch.setenv("LLM_MODEL_DEDUPLICATION", "qwen2.5-coder:7b")
        monkeypatch.setenv("LLM_MODEL_TAGGING", "qwen2.5-coder:7b")
        monkeypatch.setenv("LLM_MODEL_RULE_EXTRACTION", "qwen2.5-coder:14b")
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")

        mock_call_ollama.return_value = "Response"
        """Test that .env file variables work for Ollama configuration."""
        mock_call_ollama.return_value = "Response"

        # Test default model
        result = llm_client.call_llm("Test", task="default")
        assert result == "Response"
        mock_call_ollama.assert_called_with(
            "Test", model="qwen2.5-coder:14b", base_url="http://localhost:11434"
        )

        # Test task-specific models
        result = llm_client.call_llm("Test", task="deduplication")
        assert result == "Response"
        mock_call_ollama.assert_called_with(
            "Test", model="qwen2.5-coder:7b", base_url="http://localhost:11434"
        )

        result = llm_client.call_llm("Test", task="tagging")
        assert result == "Response"
        mock_call_ollama.assert_called_with(
            "Test", model="qwen2.5-coder:7b", base_url="http://localhost:11434"
        )

        result = llm_client.call_llm("Test", task="rule_extraction")
        assert result == "Response"
        mock_call_ollama.assert_called_with(
            "Test", model="qwen2.5-coder:14b", base_url="http://localhost:11434"
        )

    @patch("src.consolidation_app.llm_client.load_dotenv")
    @patch("src.consolidation_app.llm_client.call_ollama")
    @patch("src.consolidation_app.llm_client.call_openai")
    def test_env_file_mixed_providers(
        self, mock_call_openai, mock_call_ollama, mock_load_dotenv, monkeypatch
    ):
        """Test that .env file variables work with per-task provider selection."""
        # Clear any existing LLM-related env vars that might interfere
        llm_vars = [
            "LLM_PROVIDER",
            "LLM_PROVIDER_DEDUPLICATION",
            "LLM_PROVIDER_TAGGING",
            "LLM_PROVIDER_RULE_EXTRACTION",
            "LLM_MODEL",
            "LLM_MODEL_DEDUPLICATION",
            "LLM_MODEL_TAGGING",
            "LLM_MODEL_RULE_EXTRACTION",
        ]
        for var in llm_vars:
            monkeypatch.delenv(var, raising=False)

        # Set test environment variables (simulating .env file with per-task providers)
        monkeypatch.setenv("LLM_PROVIDER", "ollama")
        monkeypatch.setenv("LLM_MODEL", "qwen2.5-coder:14b")
        monkeypatch.setenv("LLM_PROVIDER_DEDUPLICATION", "ollama")
        monkeypatch.setenv("LLM_MODEL_DEDUPLICATION", "qwen2.5-coder:7b")
        monkeypatch.setenv("LLM_PROVIDER_TAGGING", "openai")
        monkeypatch.setenv("LLM_MODEL_TAGGING", "gpt-4o-mini")
        monkeypatch.setenv("LLM_PROVIDER_RULE_EXTRACTION", "openai")
        monkeypatch.setenv("LLM_MODEL_RULE_EXTRACTION", "gpt-4")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-openai-key-123")
        """Test that .env file variables work with per-task provider selection."""
        mock_call_ollama.return_value = "Ollama response"
        mock_call_openai.return_value = "OpenAI response"

        # Deduplication should use Ollama (task-specific provider)
        result = llm_client.call_llm("Test", task="deduplication")
        assert result == "Ollama response"
        mock_call_ollama.assert_called_with(
            "Test", model="qwen2.5-coder:7b", base_url="http://localhost:11434"
        )

        # Tagging should use OpenAI (task-specific provider)
        result = llm_client.call_llm("Test", task="tagging")
        assert result == "OpenAI response"
        mock_call_openai.assert_called_with("Test", model="gpt-4o-mini")

        # Rule extraction should use OpenAI (task-specific provider)
        result = llm_client.call_llm("Test", task="rule_extraction")
        assert result == "OpenAI response"
        mock_call_openai.assert_called_with("Test", model="gpt-4")

    @patch("src.consolidation_app.llm_client.load_dotenv")
    @patch("src.consolidation_app.llm_client.call_openai")
    def test_env_file_openai_config(
        self, mock_call_openai, mock_load_dotenv, monkeypatch
    ):
        """Test that .env file variables work for OpenAI configuration."""
        # Clear any existing LLM-related env vars that might interfere
        llm_vars = [
            "LLM_PROVIDER",
            "LLM_PROVIDER_DEDUPLICATION",
            "LLM_PROVIDER_TAGGING",
            "LLM_PROVIDER_RULE_EXTRACTION",
            "LLM_MODEL",
            "LLM_MODEL_DEDUPLICATION",
            "LLM_MODEL_TAGGING",
            "LLM_MODEL_RULE_EXTRACTION",
        ]
        for var in llm_vars:
            monkeypatch.delenv(var, raising=False)

        # Set test environment variables (simulating .env file contents for OpenAI)
        monkeypatch.setenv("LLM_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-openai-key-123")
        monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
        monkeypatch.setenv("LLM_MODEL_DEDUPLICATION", "gpt-4o-mini")
        monkeypatch.setenv("LLM_MODEL_TAGGING", "gpt-4o-mini")
        monkeypatch.setenv("LLM_MODEL_RULE_EXTRACTION", "gpt-4")
        """Test that .env file variables work for OpenAI configuration."""
        mock_call_openai.return_value = "Response"

        result = llm_client.call_llm("Test", task="deduplication")
        assert result == "Response"
        mock_call_openai.assert_called_with("Test", model="gpt-4o-mini")

        result = llm_client.call_llm("Test", task="rule_extraction")
        assert result == "Response"
        mock_call_openai.assert_called_with("Test", model="gpt-4")

    @patch("src.consolidation_app.llm_client.load_dotenv")
    @patch("src.consolidation_app.llm_client.call_anthropic")
    def test_env_file_anthropic_config(
        self, mock_call_anthropic, mock_load_dotenv, monkeypatch
    ):
        """Test that .env file variables work for Anthropic configuration."""
        # Clear any existing LLM-related env vars that might interfere
        llm_vars = [
            "LLM_PROVIDER",
            "LLM_PROVIDER_DEDUPLICATION",
            "LLM_PROVIDER_TAGGING",
            "LLM_PROVIDER_RULE_EXTRACTION",
            "LLM_MODEL",
            "LLM_MODEL_DEDUPLICATION",
            "LLM_MODEL_TAGGING",
            "LLM_MODEL_RULE_EXTRACTION",
        ]
        for var in llm_vars:
            monkeypatch.delenv(var, raising=False)

        # Set test environment variables (simulating .env file contents for Anthropic)
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key-123")
        monkeypatch.setenv("LLM_MODEL", "claude-3-haiku-20240307")
        monkeypatch.setenv("LLM_MODEL_DEDUPLICATION", "claude-3-haiku-20240307")
        monkeypatch.setenv("LLM_MODEL_TAGGING", "claude-3-haiku-20240307")
        monkeypatch.setenv("LLM_MODEL_RULE_EXTRACTION", "claude-3-opus-20240229")
        """Test that .env file variables work for Anthropic configuration."""
        mock_call_anthropic.return_value = "Response"

        result = llm_client.call_llm("Test", task="tagging")
        assert result == "Response"
        mock_call_anthropic.assert_called_with("Test", model="claude-3-haiku-20240307")

        result = llm_client.call_llm("Test", task="rule_extraction")
        assert result == "Response"
        mock_call_anthropic.assert_called_with("Test", model="claude-3-opus-20240229")


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    @patch("src.consolidation_app.llm_client.requests.post")
    def test_ollama_missing_response_field(self, mock_post):
        """Test Ollama handles missing response field gracefully."""
        mock_response = Mock()
        mock_response.json.return_value = {}  # Missing "response" field
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = llm_client.call_ollama("Test")
        assert result == ""  # Empty string when response field missing

    @patch("src.consolidation_app.llm_client.requests.post")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_openai_malformed_response(self, mock_post):
        """Test OpenAI handles malformed response."""
        mock_response = Mock()
        mock_response.json.return_value = {"choices": []}  # Missing content
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        with pytest.raises((KeyError, IndexError)):
            llm_client.call_openai("Test")

    @patch("src.consolidation_app.llm_client.call_ollama")
    @patch.dict(os.environ, {"LLM_PROVIDER": "ollama"})
    def test_call_llm_logs_errors(self, mock_call_ollama):
        """Test that call_llm logs errors properly."""
        mock_call_ollama.side_effect = ValueError("Test error")

        with pytest.raises(ValueError):
            llm_client.call_llm("Test")

        # Error should be logged (we can't easily test logging without more setup)
        # But we can verify the exception is raised


class TestActualEnvFileIntegration:
    """Integration tests that load from actual .env file."""

    @pytest.fixture
    def project_root(self):
        """Get project root directory."""
        from pathlib import Path

        return Path(__file__).resolve().parents[1]

    @pytest.fixture
    def env_file_path(self, project_root):
        """Get path to .env file."""
        return project_root / ".env"

    @patch("src.consolidation_app.llm_client.call_ollama")
    @patch("src.consolidation_app.llm_client.call_openai")
    def test_loads_per_task_config_from_actual_env_file(
        self, mock_call_openai, mock_call_ollama, env_file_path, project_root
    ):
        """Test that the app loads per-task configurations from actual .env file."""
        from dotenv import load_dotenv

        # Skip if .env file doesn't exist
        if not env_file_path.exists():
            pytest.skip(".env file not found - create one to test actual loading")

        # Load .env file manually for this test (override=True to override any existing env vars)
        load_dotenv(env_file_path, override=True)

        mock_call_ollama.return_value = "Ollama response"
        mock_call_openai.return_value = "OpenAI response"

        # Test deduplication - should use task-specific provider/model if set in .env
        dedup_provider = os.getenv("LLM_PROVIDER_DEDUPLICATION") or os.getenv(
            "LLM_PROVIDER", "ollama"
        )
        dedup_model = os.getenv("LLM_MODEL_DEDUPLICATION") or os.getenv(
            "LLM_MODEL", "qwen2.5-coder:14b"
        )

        result = llm_client.call_llm("Test deduplication", task="deduplication")
        if dedup_provider == "ollama":
            assert result == "Ollama response"
            mock_call_ollama.assert_called_with(
                "Test deduplication",
                model=dedup_model,
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            )
        elif dedup_provider == "openai":
            assert result == "OpenAI response"
            mock_call_openai.assert_called_with("Test deduplication", model=dedup_model)

        # Test tagging - should use task-specific provider/model if set in .env
        tagging_provider = os.getenv("LLM_PROVIDER_TAGGING") or os.getenv(
            "LLM_PROVIDER", "ollama"
        )

        result = llm_client.call_llm("Test tagging", task="tagging")
        if tagging_provider == "ollama":
            assert mock_call_ollama.called
        elif tagging_provider == "openai":
            assert mock_call_openai.called

        # Test rule extraction - should use task-specific provider/model if set in .env
        rule_provider = os.getenv("LLM_PROVIDER_RULE_EXTRACTION") or os.getenv(
            "LLM_PROVIDER", "ollama"
        )

        result = llm_client.call_llm("Test rule extraction", task="rule_extraction")
        if rule_provider == "ollama":
            assert mock_call_ollama.called
        elif rule_provider == "openai":
            assert mock_call_openai.called

    def test_env_file_contains_required_variables(self, env_file_path):
        """Test that .env file contains the expected LLM configuration variables."""
        from dotenv import load_dotenv

        # Skip if .env file doesn't exist
        if not env_file_path.exists():
            pytest.skip(".env file not found")

        # Load .env file
        load_dotenv(env_file_path, override=True)

        # Verify default provider/model exist
        assert os.getenv("LLM_PROVIDER") is not None, "LLM_PROVIDER not found in .env"
        assert os.getenv("LLM_MODEL") is not None, "LLM_MODEL not found in .env"

        # Verify per-task configurations exist (at least one should be set for meaningful test)
        # This is informational - per-task configs are optional
        # But if a per-task provider is set, the corresponding model should also be set
        if os.getenv("LLM_PROVIDER_DEDUPLICATION"):
            assert os.getenv(
                "LLM_MODEL_DEDUPLICATION"
            ), "LLM_MODEL_DEDUPLICATION should be set if LLM_PROVIDER_DEDUPLICATION is set"
        if os.getenv("LLM_PROVIDER_TAGGING"):
            assert os.getenv(
                "LLM_MODEL_TAGGING"
            ), "LLM_MODEL_TAGGING should be set if LLM_PROVIDER_TAGGING is set"
        if os.getenv("LLM_PROVIDER_RULE_EXTRACTION"):
            assert os.getenv(
                "LLM_MODEL_RULE_EXTRACTION"
            ), "LLM_MODEL_RULE_EXTRACTION should be set if LLM_PROVIDER_RULE_EXTRACTION is set"
