"""
LLM Client Integration Module

This module provides a unified interface for calling various LLM providers:
- Ollama (local, default)
- OpenAI API
- Anthropic API (optional)

Supports per-task model selection for optimization of performance, cost, and quality.

Version: 1.0
"""

from __future__ import annotations

import logging
import os
import time
from typing import Optional

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen2.5-coder:14b"
DEFAULT_OPENAI_MODEL = "gpt-4"
DEFAULT_ANTHROPIC_MODEL = "claude-3-opus-20240229"

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds
TIMEOUT = 120  # seconds


def _get_config_value(key: str, default: str) -> str:
    """Get configuration value from environment variable."""
    return os.getenv(key, default)


def _get_llm_provider() -> str:
    """Get LLM provider from environment variable, default to 'ollama'."""
    return _get_config_value("LLM_PROVIDER", "ollama").lower()


def _get_task_provider(task: str) -> Optional[str]:
    """
    Get task-specific provider from environment variable.

    Args:
        task: Task name (e.g., 'deduplication', 'tagging', 'rule_extraction')

    Returns:
        Provider name if set, None otherwise
    """
    task_key = f"LLM_PROVIDER_{task.upper()}"
    provider = os.getenv(task_key)
    return provider.lower() if provider else None


def _get_provider_for_task(task: str) -> str:
    """
    Determine which provider to use for a task.

    Priority:
    1. Task-specific provider from ENV (e.g., LLM_PROVIDER_DEDUPLICATION)
    2. Default provider from ENV (LLM_PROVIDER)
    3. Default to 'ollama'

    Args:
        task: Task name

    Returns:
        Provider name to use
    """
    # Try task-specific provider
    task_provider = _get_task_provider(task)
    if task_provider:
        logger.debug(f"Using task-specific provider for '{task}': {task_provider}")
        return task_provider

    # Fall back to default
    default_provider = _get_llm_provider()
    logger.debug(f"Using default provider for '{task}': {default_provider}")
    return default_provider


def _get_default_model() -> str:
    """Get default model from environment variable."""
    return _get_config_value("LLM_MODEL", DEFAULT_OLLAMA_MODEL)


def _get_task_model(task: str) -> Optional[str]:
    """
    Get task-specific model from environment variable.

    Args:
        task: Task name (e.g., 'deduplication', 'tagging', 'rule_extraction')

    Returns:
        Model name if set, None otherwise
    """
    task_key = f"LLM_MODEL_{task.upper()}"
    model = os.getenv(task_key)
    return model if model else None


def _get_model_for_task(task: str, explicit_model: Optional[str] = None) -> str:
    """
    Determine which model to use for a task.

    Priority:
    1. Explicit model parameter (if provided)
    2. Task-specific model from ENV (e.g., LLM_MODEL_DEDUPLICATION)
    3. Default model from ENV (LLM_MODEL)
    4. Provider-specific default

    Args:
        task: Task name
        explicit_model: Explicitly provided model (overrides all)

    Returns:
        Model name to use
    """
    if explicit_model:
        return explicit_model

    # Try task-specific model
    task_model = _get_task_model(task)
    if task_model:
        logger.debug(f"Using task-specific model for '{task}': {task_model}")
        return task_model

    # Fall back to default
    default_model = _get_default_model()
    logger.debug(f"Using default model for '{task}': {default_model}")
    return default_model


def call_ollama(
    prompt: str,
    model: str = DEFAULT_OLLAMA_MODEL,
    base_url: str = DEFAULT_OLLAMA_URL,
    timeout: int = TIMEOUT,
) -> str:
    """
    Call Ollama API (local LLM).

    Args:
        prompt: Input prompt text
        model: Model name (default: qwen2.5-coder:14b)
        base_url: Ollama API base URL (default: http://localhost:11434)
        timeout: Request timeout in seconds (default: 120)

    Returns:
        LLM response text

    Raises:
        ConnectionError: If Ollama service is not available
        TimeoutError: If request times out
        requests.RequestException: For other HTTP errors
    """
    url = f"{base_url}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    logger.info(f"Calling Ollama API: model={model}, prompt_length={len(prompt)}")

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()

            result = response.json()
            response_text = result.get("response", "")

            # Extract token counts from Ollama response
            prompt_eval_count = result.get("prompt_eval_count", 0)  # Input tokens
            eval_count = result.get("eval_count", 0)  # Output tokens
            total_tokens = prompt_eval_count + eval_count

            logger.info(
                f"Ollama API call successful: model={model}, "
                f"response_length={len(response_text)}, attempt={attempt + 1}, "
                f"input_tokens={prompt_eval_count}, output_tokens={eval_count}, "
                f"total_tokens={total_tokens}"
            )

            return response_text

        except requests.exceptions.ConnectionError as e:
            error_msg = f"Failed to connect to Ollama at {base_url}: {e}"
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"{error_msg} (retrying in {RETRY_DELAY}s...)")
                time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
            else:
                logger.error(error_msg)
                raise ConnectionError(error_msg) from e

        except requests.exceptions.Timeout as e:
            error_msg = f"Ollama API request timed out after {timeout}s"
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"{error_msg} (retrying in {RETRY_DELAY}s...)")
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                logger.error(error_msg)
                raise TimeoutError(error_msg) from e

        except requests.exceptions.RequestException as e:
            error_msg = f"Ollama API request failed: {e}"
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"{error_msg} (retrying in {RETRY_DELAY}s...)")
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                logger.error(error_msg)
                raise requests.RequestException(error_msg) from e

    # Should never reach here, but just in case
    raise RuntimeError("Failed to call Ollama API after all retries")


def call_openai(
    prompt: str,
    model: str = DEFAULT_OPENAI_MODEL,
    api_key: Optional[str] = None,
    timeout: int = TIMEOUT,
) -> str:
    """
    Call OpenAI API.

    Args:
        prompt: Input prompt text
        model: Model name (default: gpt-4)
        api_key: OpenAI API key (default: from OPENAI_API_KEY env var)
        timeout: Request timeout in seconds (default: 120)

    Returns:
        LLM response text

    Raises:
        ValueError: If API key is missing
        requests.RequestException: For HTTP errors (including rate limiting)
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        error_msg = (
            "OpenAI API key is required. Set OPENAI_API_KEY environment variable."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    logger.info(f"Calling OpenAI API: model={model}, prompt_length={len(prompt)}")

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=timeout
            )
            response.raise_for_status()

            result = response.json()
            response_text = result["choices"][0]["message"]["content"]

            # Extract token counts from OpenAI response
            usage = result.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)  # Input tokens
            completion_tokens = usage.get("completion_tokens", 0)  # Output tokens
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
            # OpenAI may include cached tokens in some models (e.g., GPT-4 with cache)
            cached_tokens = usage.get("cached_tokens", 0)

            logger.info(
                f"OpenAI API call successful: model={model}, "
                f"response_length={len(response_text)}, attempt={attempt + 1}, "
                f"input_tokens={prompt_tokens}, cached_tokens={cached_tokens}, "
                f"output_tokens={completion_tokens}, total_tokens={total_tokens}"
            )

            return response_text

        except requests.exceptions.HTTPError as e:
            status_code = response.status_code if hasattr(e, "response") else None
            if status_code == 429:  # Rate limit
                error_msg = "OpenAI API rate limit exceeded"
                if attempt < MAX_RETRIES - 1:
                    retry_after = int(
                        response.headers.get("Retry-After", RETRY_DELAY * 10)
                    )
                    logger.warning(f"{error_msg} (retrying after {retry_after}s...)")
                    time.sleep(retry_after)
                else:
                    logger.error(error_msg)
                    raise requests.RequestException(error_msg) from e
            else:
                error_msg = f"OpenAI API request failed with status {status_code}: {e}"
                logger.error(error_msg)
                raise requests.RequestException(error_msg) from e

        except requests.exceptions.RequestException as e:
            error_msg = f"OpenAI API request failed: {e}"
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"{error_msg} (retrying in {RETRY_DELAY}s...)")
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                logger.error(error_msg)
                raise requests.RequestException(error_msg) from e

    # Should never reach here
    raise RuntimeError("Failed to call OpenAI API after all retries")


def call_anthropic(
    prompt: str,
    model: str = DEFAULT_ANTHROPIC_MODEL,
    api_key: Optional[str] = None,
    timeout: int = TIMEOUT,
) -> str:
    """
    Call Anthropic API (Claude).

    Args:
        prompt: Input prompt text
        model: Model name (default: claude-3-opus-20240229)
        api_key: Anthropic API key (default: from ANTHROPIC_API_KEY env var)
        timeout: Request timeout in seconds (default: 120)

    Returns:
        LLM response text

    Raises:
        ValueError: If API key is missing
        requests.RequestException: For HTTP errors (including rate limiting)
    """
    api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        error_msg = (
            "Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}],
    }

    logger.info(f"Calling Anthropic API: model={model}, prompt_length={len(prompt)}")

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=timeout
            )
            response.raise_for_status()

            result = response.json()
            response_text = result["content"][0]["text"]

            # Extract token counts from Anthropic response
            usage = result.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            # Anthropic provides cache metrics separately
            cache_creation_input_tokens = usage.get("cache_creation_input_tokens", 0)
            cache_read_input_tokens = usage.get("cache_read_input_tokens", 0)
            cached_tokens = cache_creation_input_tokens + cache_read_input_tokens

            logger.info(
                f"Anthropic API call successful: model={model}, "
                f"response_length={len(response_text)}, attempt={attempt + 1}, "
                f"input_tokens={input_tokens}, cached_tokens={cached_tokens} "
                f"(creation={cache_creation_input_tokens}, read={cache_read_input_tokens}), "
                f"output_tokens={output_tokens}, total_tokens={input_tokens + output_tokens}"
            )

            return response_text

        except requests.exceptions.HTTPError as e:
            status_code = response.status_code if hasattr(e, "response") else None
            if status_code == 429:  # Rate limit
                error_msg = "Anthropic API rate limit exceeded"
                if attempt < MAX_RETRIES - 1:
                    retry_after = int(
                        response.headers.get("Retry-After", RETRY_DELAY * 10)
                    )
                    logger.warning(f"{error_msg} (retrying after {retry_after}s...)")
                    time.sleep(retry_after)
                else:
                    logger.error(error_msg)
                    raise requests.RequestException(error_msg) from e
            else:
                error_msg = (
                    f"Anthropic API request failed with status {status_code}: {e}"
                )
                logger.error(error_msg)
                raise requests.RequestException(error_msg) from e

        except requests.exceptions.RequestException as e:
            error_msg = f"Anthropic API request failed: {e}"
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"{error_msg} (retrying in {RETRY_DELAY}s...)")
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                logger.error(error_msg)
                raise requests.RequestException(error_msg) from e

    # Should never reach here
    raise RuntimeError("Failed to call Anthropic API after all retries")


def call_llm(
    prompt: str,
    task: str = "default",
    model: Optional[str] = None,
) -> str:
    """
    Unified LLM call function that routes to the appropriate provider.

    This function:
    1. Determines which provider to use (task-specific > default)
    2. Determines which model to use (explicit > task-specific > default)
    3. Routes to the appropriate provider
    4. Logs all calls for cost tracking

    Args:
        prompt: Input prompt text
        task: Task name for provider/model selection (e.g., 'deduplication', 'tagging', 'rule_extraction')
              Used to look up task-specific providers/models from ENV:
              - LLM_PROVIDER_DEDUPLICATION, LLM_MODEL_DEDUPLICATION
              - LLM_PROVIDER_TAGGING, LLM_MODEL_TAGGING
              - LLM_PROVIDER_RULE_EXTRACTION, LLM_MODEL_RULE_EXTRACTION
        model: Explicit model name (overrides task-specific and default models)

    Returns:
        LLM response text

    Raises:
        ValueError: If provider is invalid or API key is missing
        ConnectionError: If Ollama service is not available
        TimeoutError: If request times out
        requests.RequestException: For other HTTP errors

    Example:
        >>> # Use default provider and model
        >>> response = call_llm("Hello", task="default")
        >>> # Use task-specific provider and model
        >>> response = call_llm("Compare errors", task="deduplication")
        >>> # Use explicit model (with task-specific provider if set)
        >>> response = call_llm("Tag this", task="tagging", model="qwen2.5-coder:7b")
    """
    provider = _get_provider_for_task(task)
    selected_model = _get_model_for_task(task, model)

    logger.info(
        f"LLM call: provider={provider}, task={task}, model={selected_model}, "
        f"prompt_length={len(prompt)}"
    )

    start_time = time.time()

    try:
        if provider == "ollama":
            response = call_ollama(prompt, model=selected_model)
        elif provider == "openai":
            response = call_openai(prompt, model=selected_model)
        elif provider == "anthropic":
            response = call_anthropic(prompt, model=selected_model)
        else:
            error_msg = (
                f"Invalid LLM provider: {provider}. "
                f"Must be one of: ollama, openai, anthropic"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        elapsed_time = time.time() - start_time
        # Token counts are already logged by individual provider functions
        logger.info(
            f"LLM call completed: provider={provider}, task={task}, model={selected_model}, "
            f"response_length={len(response)}, duration={elapsed_time:.2f}s"
        )

        return response

    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(
            f"LLM call failed: provider={provider}, task={task}, model={selected_model}, "
            f"duration={elapsed_time:.2f}s, error={type(e).__name__}: {e}"
        )
        raise
