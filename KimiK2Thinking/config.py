"""Configuration for Kimi K2 refactor."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
# Note: The correct endpoint is api.moonshot.ai (not .cn)
MOONSHOT_BASE_URL = "https://api.moonshot.ai/v1"

# Model Configuration
# Note: Check Moonshot AI documentation for exact model names
# Common options: "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"
# For Kimi K2 thinking model, verify the exact model identifier in the API docs
KIMI_K2_MODEL = os.getenv("KIMI_MODEL", "moonshot-v1-8k")  # Default model

# Default settings
DEFAULT_MAX_TOKENS = 4000
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9

# Tool Configuration
USE_TOOLS = os.getenv("KIMI_USE_TOOLS", "true").lower() == "true"
TOOLS_ENABLED = USE_TOOLS  # Can be overridden per agent

# Thinking Mode Configuration
ENABLE_THINKING = os.getenv("KIMI_ENABLE_THINKING", "true").lower() == "true"

# Fallback to verbose instructions if tools not available
FALLBACK_TO_VERBOSE = True

