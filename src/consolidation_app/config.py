"""
config.py
ENV-first configuration for the consolidation app (Phase 5.2).
v1.0

Read configuration from environment variables (primary) and optional YAML file.
ENV overrides YAML when both exist. Validates required vars, paths, schedule, threshold.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

# Default config file path (relative to cwd)
DEFAULT_CONFIG_PATH = Path("consolidation_config.yaml")

# Cron pattern: 5 fields (min hour dom month dow), e.g. "0 2 * * *"
CRON_PATTERN = re.compile(r"^\s*\S+\s+\S+\s+\S+\s+\S+\s+\S+\s*$")


def _env(key: str, default: str | None = None) -> str | None:
    """Get environment variable; return default if unset or empty."""
    v = os.getenv(key)
    if v is not None and v.strip() != "":
        return v.strip()
    return default


def _load_yaml_config(path: Path) -> dict[str, Any]:
    """Load YAML config from path. Return {} if file missing or invalid."""
    if not path.is_file():
        return {}

    try:
        import yaml
    except ImportError:
        return {}

    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _cron_ok(schedule: str) -> bool:
    """Check schedule has 5 cron-like fields (min hour dom month dow)."""
    return bool(CRON_PATTERN.match(schedule))


@dataclass
class ConsolidationConfig:
    """
    Type-safe consolidation app configuration.

    ENV is primary; optional YAML supplies extra_projects and overrides.
    ENV overrides YAML when both exist.
    """

    projects_root: Path
    llm_provider: str = "ollama"
    llm_model: str = "qwen3:8b"
    llm_model_deduplication: str | None = None
    llm_model_tagging: str | None = None
    llm_model_rule_extraction: str | None = None
    consolidation_schedule: str = "0 2 * * *"
    similarity_threshold: float = 0.85
    llm_api_key: str | None = None
    extra_projects: list[str] = field(default_factory=list)

    def model_for_task(self, task: str) -> str:
        """Return model for task: task-specific override else llm_model."""
        m = {
            "deduplication": self.llm_model_deduplication,
            "tagging": self.llm_model_tagging,
            "rule_extraction": self.llm_model_rule_extraction,
        }.get(task)
        return m if m else self.llm_model


def _merge_from_yaml(
    raw: dict[str, Any],
    env_provider: str | None,
    env_model: str | None,
    env_dedup: str | None,
    env_tag: str | None,
    env_rule: str | None,
    env_schedule: str | None,
    env_threshold: str | None,
) -> tuple[str, str, str | None, str | None, str | None, str, float, list[str]]:
    """Extract config from YAML and merge with ENV; ENV wins when set."""
    cons = raw.get("consolidation") or {}
    projects: list[str] = cons.get("projects") or []
    if not isinstance(projects, list):
        projects = []

    llm = raw.get("llm") or {}
    def_model = llm.get("default_model")
    models = llm.get("models") or {}
    if not isinstance(models, dict):
        models = {}

    provider = env_provider or (llm.get("provider") or "ollama")
    provider = str(provider).lower() if provider else "ollama"

    model = env_model or def_model or "qwen3:8b"
    model = str(model).strip()

    dedup = env_dedup or models.get("deduplication")
    dedup = str(dedup).strip() if dedup else None
    tag = env_tag or models.get("tagging")
    tag = str(tag).strip() if tag else None
    rule = env_rule or models.get("rule_extraction")
    rule = str(rule).strip() if rule else None

    schedule = env_schedule or cons.get("schedule") or "0 2 * * *"
    schedule = str(schedule).strip()

    th = env_threshold or cons.get("similarity_threshold")
    if th is not None:
        try:
            threshold = float(th)
        except (TypeError, ValueError):
            threshold = 0.85
    else:
        threshold = 0.85

    extra = [str(p).strip() for p in projects if p]

    return provider, model, dedup, tag, rule, schedule, threshold, extra


def load_config(
    *,
    config_path: Path | None = None,
    validate: bool = True,
) -> ConsolidationConfig:
    """
    Load consolidation config from ENV and optional YAML.

    ENV is primary. If CONFIG_PATH (or config_path) points to an existing YAML
    file, it is read. ENV overrides YAML when both exist. extra_projects
    come only from YAML (consolidation.projects).

    Args:
        config_path: Override path to YAML config. Default: CONFIG_PATH env or
                     consolidation_config.yaml in cwd.
        validate: If True, validate required vars, paths, schedule, threshold.

    Returns:
        ConsolidationConfig

    Raises:
        ValueError: If validation fails (PROJECTS_ROOT missing, path invalid,
                    schedule format invalid, threshold out of range).
    """
    path = config_path or Path(_env("CONFIG_PATH") or "").expanduser().resolve()
    if not path or not path.suffix:
        path = Path.cwd() / DEFAULT_CONFIG_PATH

    raw = _load_yaml_config(path)

    env_root = _env("PROJECTS_ROOT")
    env_provider = _env("LLM_PROVIDER")
    env_model = _env("LLM_MODEL")
    env_dedup = _env("LLM_MODEL_DEDUPLICATION")
    env_tag = _env("LLM_MODEL_TAGGING")
    env_rule = _env("LLM_MODEL_RULE_EXTRACTION")
    env_schedule = _env("CONSOLIDATION_SCHEDULE")
    env_threshold = _env("SIMILARITY_THRESHOLD")
    env_api_key = _env("LLM_API_KEY")

    if not env_root:
        raise ValueError("PROJECTS_ROOT is required; set the environment variable")
    projects_root_str = env_root

    projects_root = Path(projects_root_str).expanduser().resolve()

    (
        provider,
        model,
        dedup,
        tag,
        rule,
        schedule,
        threshold,
        extra,
    ) = _merge_from_yaml(
        raw,
        env_provider,
        env_model,
        env_dedup,
        env_tag,
        env_rule,
        env_schedule,
        env_threshold,
    )

    cfg = ConsolidationConfig(
        projects_root=projects_root,
        llm_provider=provider,
        llm_model=model,
        llm_model_deduplication=dedup,
        llm_model_tagging=tag,
        llm_model_rule_extraction=rule,
        consolidation_schedule=schedule,
        similarity_threshold=threshold,
        llm_api_key=env_api_key,
        extra_projects=extra,
    )

    if validate:
        _validate_config(cfg)

    return cfg


def _validate_config(cfg: ConsolidationConfig) -> None:
    """Validate config: required vars, paths, schedule, threshold."""
    if not cfg.projects_root.exists():
        raise ValueError(f"PROJECTS_ROOT path does not exist: {cfg.projects_root}")
    if not cfg.projects_root.is_dir():
        raise ValueError(f"PROJECTS_ROOT is not a directory: {cfg.projects_root}")

    if not _cron_ok(cfg.consolidation_schedule):
        raise ValueError(
            f"CONSOLIDATION_SCHEDULE must be a 5-field cron string "
            f"(e.g. '0 2 * * *'); got: {cfg.consolidation_schedule!r}"
        )

    if not (0.0 <= cfg.similarity_threshold <= 1.0):
        raise ValueError(
            f"SIMILARITY_THRESHOLD must be between 0.0 and 1.0; "
            f"got: {cfg.similarity_threshold}"
        )
