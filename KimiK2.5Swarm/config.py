"""
Configuration for KimiK2Thinking - Dataclass-based configuration system.

This module provides centralized, type-safe configuration using dataclasses
and enums, following the K2.5 patterns.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# Mode Configuration
# =============================================================================


class KimiMode(Enum):
    """
    Operating modes for Kimi K2.5.

    Each mode is optimized for different use cases with specific
    temperature and token settings.
    """
    INSTANT = "instant"      # Fast responses, T=0.6
    THINKING = "thinking"    # Deep reasoning, T=1.0
    AGENT = "agent"          # Tool calling, T=0.6
    SWARM = "swarm"          # Multi-agent parallel, T=1.0


@dataclass
class ModeConfig:
    """
    Configuration parameters for a specific operating mode.

    Attributes:
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens to generate
        top_p: Nucleus sampling parameter
        extra_body: Additional API parameters (e.g., thinking mode settings)
    """
    temperature: float
    max_tokens: int
    top_p: float = 0.95
    extra_body: Optional[Dict[str, Any]] = None


# Mode-specific configurations
MODE_CONFIGS: Dict[KimiMode, ModeConfig] = {
    KimiMode.INSTANT: ModeConfig(
        temperature=0.6,
        max_tokens=4096,
        extra_body={"thinking": {"type": "disabled"}}
    ),
    KimiMode.THINKING: ModeConfig(
        temperature=1.0,
        max_tokens=8192,
    ),
    KimiMode.AGENT: ModeConfig(
        temperature=0.6,
        max_tokens=4096,
    ),
    KimiMode.SWARM: ModeConfig(
        temperature=1.0,
        max_tokens=16384,
    ),
}


# =============================================================================
# API Configuration
# =============================================================================


@dataclass
class APIConfig:
    """
    API configuration with factory method for environment loading.

    Attributes:
        base_url: API endpoint URL
        api_key: Authentication key
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts for failed requests
    """
    base_url: str
    api_key: str
    timeout: int = 120
    max_retries: int = 3

    @classmethod
    def from_env(cls, base_url: Optional[str] = None) -> "APIConfig":
        """
        Create APIConfig from environment variables.

        Args:
            base_url: Override base URL (defaults to MOONSHOT_BASE_URL)

        Returns:
            APIConfig instance

        Raises:
            ValueError: If MOONSHOT_API_KEY is not set
        """
        api_key = os.getenv("MOONSHOT_API_KEY")
        if not api_key:
            raise ValueError(
                "MOONSHOT_API_KEY environment variable not set. "
                "Please set it in your .env file or export it."
            )

        return cls(
            base_url=base_url or os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1"),
            api_key=api_key.strip(),
            timeout=int(os.getenv("KIMI_TIMEOUT", "120")),
            max_retries=int(os.getenv("KIMI_MAX_RETRIES", "3")),
        )


# =============================================================================
# Enrichment Configuration
# =============================================================================


@dataclass
class EnrichmentConfig:
    """
    Configuration for the enrichment pipeline.

    Attributes:
        max_concurrent_nodes: Maximum nodes to enrich in parallel
        enable_parallel_enrichment: Whether to use parallel processing
        cache_ttl_seconds: Cache time-to-live in seconds
        max_retries: Maximum retries for failed enrichments
        max_depth: Maximum prerequisite tree depth
    """
    max_concurrent_nodes: int = 10
    enable_parallel_enrichment: bool = True
    cache_ttl_seconds: int = 3600
    max_retries: int = 2
    max_depth: int = 4

    @classmethod
    def from_env(cls) -> "EnrichmentConfig":
        """Create EnrichmentConfig from environment variables."""
        return cls(
            max_concurrent_nodes=int(os.getenv("KIMI_MAX_CONCURRENT", "10")),
            enable_parallel_enrichment=os.getenv("KIMI_PARALLEL", "true").lower() == "true",
            cache_ttl_seconds=int(os.getenv("KIMI_CACHE_TTL", "3600")),
            max_retries=int(os.getenv("KIMI_MAX_RETRIES", "2")),
            max_depth=int(os.getenv("KIMI_MAX_DEPTH", "4")),
        )


# =============================================================================
# Model Configuration
# =============================================================================


@dataclass
class ModelInfo:
    """
    Information about a specific model variant.

    Attributes:
        model_id: The model identifier for API calls
        context_length: Maximum context window in tokens
        max_completion_tokens: Maximum completion tokens
        supports_tools: Whether the model supports function calling
        supports_thinking: Whether the model supports thinking mode
    """
    model_id: str
    context_length: int
    max_completion_tokens: int
    supports_tools: bool = True
    supports_thinking: bool = True


# Available model variants
MODEL_VARIANTS: Dict[str, ModelInfo] = {
    "8k": ModelInfo(
        model_id="moonshot-v1-8k",
        context_length=8192,
        max_completion_tokens=4096,
    ),
    "32k": ModelInfo(
        model_id="moonshot-v1-32k",
        context_length=32768,
        max_completion_tokens=8192,
    ),
    "128k": ModelInfo(
        model_id="moonshot-v1-128k",
        context_length=131072,
        max_completion_tokens=16384,
    ),
}


# =============================================================================
# Legacy Compatibility - Exported constants
# =============================================================================


# API Configuration (legacy exports)
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
MOONSHOT_BASE_URL = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1")

# Model Configuration (legacy exports)
KIMI_K2_MODEL = os.getenv("KIMI_MODEL", "moonshot-v1-8k")

# Default settings (legacy exports)
DEFAULT_MAX_TOKENS = 4000
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9

# Tool Configuration (legacy exports)
USE_TOOLS = os.getenv("KIMI_USE_TOOLS", "true").lower() == "true"
TOOLS_ENABLED = USE_TOOLS

# Thinking Mode Configuration (legacy exports)
ENABLE_THINKING = os.getenv("KIMI_ENABLE_THINKING", "true").lower() == "true"

# Fallback setting (legacy export)
FALLBACK_TO_VERBOSE = True


# =============================================================================
# Utility Functions
# =============================================================================


def get_mode_config(mode: KimiMode) -> ModeConfig:
    """
    Get configuration for a specific mode.

    Args:
        mode: The operating mode

    Returns:
        ModeConfig for the specified mode
    """
    return MODE_CONFIGS.get(mode, MODE_CONFIGS[KimiMode.THINKING])


def get_model_info(variant: str = "8k") -> ModelInfo:
    """
    Get information about a model variant.

    Args:
        variant: Model variant key (8k, 32k, 128k)

    Returns:
        ModelInfo for the specified variant
    """
    return MODEL_VARIANTS.get(variant, MODEL_VARIANTS["8k"])
