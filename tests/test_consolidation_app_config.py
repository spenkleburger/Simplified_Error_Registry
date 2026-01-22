"""
Tests for consolidation app config module (Phase 5.2).

Covers ENV-first loading, optional YAML, ENV-overrides-YAML, and validation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from src.consolidation_app import config

# Ensure project root on path
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


@pytest.fixture
def consolidation_env(monkeypatch, temp_dir):
    """Set PROJECTS_ROOT to temp_dir and clear consolidation-related env vars."""
    monkeypatch.setenv("PROJECTS_ROOT", str(temp_dir))
    for key in (
        "CONFIG_PATH",
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_MODEL_DEDUPLICATION",
        "LLM_MODEL_TAGGING",
        "LLM_MODEL_RULE_EXTRACTION",
        "CONSOLIDATION_SCHEDULE",
        "SIMILARITY_THRESHOLD",
        "LLM_API_KEY",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(
        "src.consolidation_app.config.load_dotenv", lambda *a, **k: None
    )
    yield temp_dir


class TestEnvReading:
    """Test reading configuration from environment variables."""

    def test_projects_root_from_env(self, consolidation_env):
        """PROJECTS_ROOT is read from ENV and resolved."""
        cfg = config.load_config(validate=True)
        assert cfg.projects_root == consolidation_env.resolve()
        assert cfg.projects_root.is_dir()

    def test_defaults_when_env_unset(self, consolidation_env):
        """Defaults apply when optional ENV vars are unset."""
        cfg = config.load_config(validate=True)
        assert cfg.llm_provider == "ollama"
        assert cfg.llm_model == "qwen3:8b"
        assert cfg.llm_model_deduplication is None
        assert cfg.llm_model_tagging is None
        assert cfg.llm_model_rule_extraction is None
        assert cfg.consolidation_schedule == "0 2 * * *"
        assert cfg.similarity_threshold == 0.85
        assert cfg.llm_api_key is None
        assert cfg.extra_projects == []

    def test_optional_env_overrides(self, consolidation_env, monkeypatch):
        """Optional ENV vars override defaults."""
        monkeypatch.setenv("LLM_PROVIDER", "openai")
        monkeypatch.setenv("LLM_MODEL", "gpt-4")
        monkeypatch.setenv("LLM_MODEL_DEDUPLICATION", "gpt-4o-mini")
        monkeypatch.setenv("CONSOLIDATION_SCHEDULE", "0 3 * * *")
        monkeypatch.setenv("SIMILARITY_THRESHOLD", "0.9")
        monkeypatch.setenv("LLM_API_KEY", "sk-test")

        cfg = config.load_config(validate=True)
        assert cfg.llm_provider == "openai"
        assert cfg.llm_model == "gpt-4"
        assert cfg.llm_model_deduplication == "gpt-4o-mini"
        assert cfg.consolidation_schedule == "0 3 * * *"
        assert cfg.similarity_threshold == 0.9
        assert cfg.llm_api_key == "sk-test"

    def test_model_for_task(self, consolidation_env, monkeypatch):
        """model_for_task returns task override or default."""
        monkeypatch.setenv("LLM_MODEL", "base")
        monkeypatch.setenv("LLM_MODEL_TAGGING", "tag-model")

        cfg = config.load_config(validate=True)
        assert cfg.model_for_task("deduplication") == "base"
        assert cfg.model_for_task("tagging") == "tag-model"
        assert cfg.model_for_task("rule_extraction") == "base"
        assert cfg.model_for_task("unknown") == "base"


class TestYamlConfig:
    """Test optional YAML config loading."""

    def test_yaml_extra_projects(self, consolidation_env, monkeypatch, temp_dir):
        """YAML consolidation.projects loaded as extra_projects."""
        yaml_path = temp_dir / "consolidation_config.yaml"
        yaml_path.write_text(
            "consolidation:\n  projects:\n    - /extra/a\n    - /extra/b\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("CONFIG_PATH", str(yaml_path))

        cfg = config.load_config(validate=True)
        assert cfg.extra_projects == ["/extra/a", "/extra/b"]

    def test_yaml_llm_default_model(self, consolidation_env, monkeypatch, temp_dir):
        """YAML llm.default_model used when ENV LLM_MODEL unset."""
        yaml_path = temp_dir / "consolidation_config.yaml"
        yaml_path.write_text(
            "llm:\n  default_model: custom-model\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("CONFIG_PATH", str(yaml_path))

        cfg = config.load_config(validate=True)
        assert cfg.llm_model == "custom-model"

    def test_yaml_llm_models_per_task(self, consolidation_env, monkeypatch, temp_dir):
        """YAML llm.models per-task overrides applied."""
        yaml_path = temp_dir / "consolidation_config.yaml"
        yaml_path.write_text(
            "llm:\n  default_model: base\n  models:\n"
            "    deduplication: dedup-model\n    tagging: tag-model\n"
            "    rule_extraction: rule-model\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("CONFIG_PATH", str(yaml_path))

        cfg = config.load_config(validate=True)
        assert cfg.llm_model == "base"
        assert cfg.llm_model_deduplication == "dedup-model"
        assert cfg.llm_model_tagging == "tag-model"
        assert cfg.llm_model_rule_extraction == "rule-model"

    def test_yaml_missing_ignored(self, consolidation_env, monkeypatch, temp_dir):
        """Missing YAML path is ignored; config from ENV only."""
        missing = temp_dir / "nonexistent.yaml"
        monkeypatch.setenv("CONFIG_PATH", str(missing))

        cfg = config.load_config(validate=True)
        assert cfg.extra_projects == []


class TestEnvOverridesYaml:
    """Test that ENV overrides YAML when both exist."""

    def test_env_overrides_yaml_model(self, consolidation_env, monkeypatch, temp_dir):
        """LLM_MODEL from ENV overrides YAML default_model."""
        yaml_path = temp_dir / "consolidation_config.yaml"
        yaml_path.write_text(
            "llm:\n  default_model: yaml-model\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("CONFIG_PATH", str(yaml_path))
        monkeypatch.setenv("LLM_MODEL", "env-model")

        cfg = config.load_config(validate=True)
        assert cfg.llm_model == "env-model"

    def test_env_overrides_yaml_per_task_model(
        self, consolidation_env, monkeypatch, temp_dir
    ):
        """LLM_MODEL_TAGGING from ENV overrides YAML models.tagging."""
        yaml_path = temp_dir / "consolidation_config.yaml"
        yaml_path.write_text(
            "llm:\n  models:\n    tagging: yaml-tag\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("CONFIG_PATH", str(yaml_path))
        monkeypatch.setenv("LLM_MODEL_TAGGING", "env-tag")

        cfg = config.load_config(validate=True)
        assert cfg.llm_model_tagging == "env-tag"

    def test_env_overrides_yaml_schedule(
        self, consolidation_env, monkeypatch, temp_dir
    ):
        """CONSOLIDATION_SCHEDULE from ENV overrides YAML."""
        yaml_path = temp_dir / "consolidation_config.yaml"
        yaml_path.write_text(
            "consolidation:\n  schedule: '0 4 * * *'\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("CONFIG_PATH", str(yaml_path))
        monkeypatch.setenv("CONSOLIDATION_SCHEDULE", "0 5 * * *")

        cfg = config.load_config(validate=True)
        assert cfg.consolidation_schedule == "0 5 * * *"

    def test_env_overrides_yaml_threshold(
        self, consolidation_env, monkeypatch, temp_dir
    ):
        """SIMILARITY_THRESHOLD from ENV overrides YAML."""
        yaml_path = temp_dir / "consolidation_config.yaml"
        yaml_path.write_text(
            "consolidation:\n  similarity_threshold: 0.7\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("CONFIG_PATH", str(yaml_path))
        monkeypatch.setenv("SIMILARITY_THRESHOLD", "0.92")

        cfg = config.load_config(validate=True)
        assert cfg.similarity_threshold == 0.92


class TestValidation:
    """Test configuration validation."""

    def test_projects_root_required(self, monkeypatch):
        """load_config raises if PROJECTS_ROOT is not set."""
        monkeypatch.delenv("PROJECTS_ROOT", raising=False)
        monkeypatch.setattr(
            "src.consolidation_app.config.load_dotenv", lambda *a, **k: None
        )

        with pytest.raises(ValueError, match="PROJECTS_ROOT is required"):
            config.load_config(validate=True)

    def test_projects_root_must_exist(self, consolidation_env, monkeypatch):
        """load_config raises if PROJECTS_ROOT path does not exist."""
        monkeypatch.setenv("PROJECTS_ROOT", str(consolidation_env / "nonexistent"))

        with pytest.raises(ValueError, match="path does not exist"):
            config.load_config(validate=True)

    def test_projects_root_must_be_dir(self, consolidation_env, monkeypatch):
        """load_config raises if PROJECTS_ROOT is not a directory."""
        f = consolidation_env / "file.txt"
        f.write_text("x", encoding="utf-8")
        monkeypatch.setenv("PROJECTS_ROOT", str(f))

        with pytest.raises(ValueError, match="not a directory"):
            config.load_config(validate=True)

    def test_schedule_invalid_format(self, consolidation_env, monkeypatch):
        """load_config raises if CONSOLIDATION_SCHEDULE is not 5-field cron."""
        monkeypatch.setenv("CONSOLIDATION_SCHEDULE", "0 2 * *")  # only 4 fields

        with pytest.raises(ValueError, match="5-field cron"):
            config.load_config(validate=True)

    def test_schedule_valid_format(self, consolidation_env, monkeypatch):
        """Valid 5-field cron schedule passes validation."""
        monkeypatch.setenv("CONSOLIDATION_SCHEDULE", "0 2 * * *")
        cfg = config.load_config(validate=True)
        assert cfg.consolidation_schedule == "0 2 * * *"

    def test_threshold_out_of_range_low(self, consolidation_env, monkeypatch):
        """SIMILARITY_THRESHOLD < 0 raises."""
        monkeypatch.setenv("SIMILARITY_THRESHOLD", "-0.1")

        with pytest.raises(ValueError, match="0.0 and 1.0"):
            config.load_config(validate=True)

    def test_threshold_out_of_range_high(self, consolidation_env, monkeypatch):
        """SIMILARITY_THRESHOLD > 1 raises."""
        monkeypatch.setenv("SIMILARITY_THRESHOLD", "1.1")

        with pytest.raises(ValueError, match="0.0 and 1.0"):
            config.load_config(validate=True)

    def test_threshold_valid(self, consolidation_env, monkeypatch):
        """SIMILARITY_THRESHOLD in [0, 1] passes."""
        monkeypatch.setenv("SIMILARITY_THRESHOLD", "0.75")
        cfg = config.load_config(validate=True)
        assert cfg.similarity_threshold == 0.75

    def test_validate_false_skips_validation(self, monkeypatch):
        """With validate=False, path/schedule/threshold checks are skipped."""
        monkeypatch.setenv("PROJECTS_ROOT", "/nonexistent/path")
        monkeypatch.setattr(
            "src.consolidation_app.config.load_dotenv", lambda *a, **k: None
        )

        cfg = config.load_config(validate=False)
        assert cfg.projects_root == Path("/nonexistent/path").resolve()
