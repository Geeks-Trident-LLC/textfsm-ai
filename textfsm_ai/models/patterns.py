import re

# ---------------------------------------------------------
# OpenAI (GPT + O-series)
# Examples:
#   gpt-4.1
#   gpt-4.1-mini
#   gpt-5.4-flash-lite
#   gpt-5.5-pro
#   o1
#   o3-mini
# ---------------------------------------------------------
OPENAI_PATTERN = re.compile(
    r"^(gpt-[0-9]+[a-zA-Z]*(?:\.[0-9]+)?|o[0-9]+)"
    r"(?:-(mini|nano|pro|thinking|instant|flash|flash-lite))?$"
)


# ---------------------------------------------------------
# Gemini
# Examples:
#   gemini-2.0-flash
#   gemini-2.0-flash-lite
#   gemini-2.5-pro
#   gemini-3.1-flash
#   gemini-3.1-flash-image
# ---------------------------------------------------------
GEMINI_PATTERN = re.compile(
    r"^gemini-[0-9]+(?:\.[0-9]+)?-"
    "(pro|flash-lite|flash-image|flash-native-audio|"
    "flash-tts|flash-tts-preview|flash-live-preview|flash)"
    r"(?:[a-z0-9\-]*)?$"
)


# ---------------------------------------------------------
# Anthropic Claude 3 / 3.5
# Examples:
#   claude-opus-3-20240229
#   claude-sonnet-3-5
#   claude-haiku-3-5-20251001
# ---------------------------------------------------------
ANTHROPIC_PATTERN = re.compile(
    r"^claude-(opus|sonnet|haiku)-[0-9]+-[0-9]+(?:-[0-9]{8})?$"
)


# ---------------------------------------------------------
# DeepSeek v4
# Examples:
#   deepseek-v4-pro
#   deepseek-v4-flash
# ---------------------------------------------------------
DEEPSEEK_PATTERN_V4 = re.compile(r"^deepseek-v4-(pro|flash)$")


# ---------------------------------------------------------
# DeepSeek native models
# Examples:
#   deepseek-chat
#   deepseek-reasoner
#   deepseek-r1
#   deepseek-r1-distill
# ---------------------------------------------------------
DEEPSEEK_NATIVE_PATTERN = re.compile(r"^deepseek-(chat|reasoner|r1|r1-distill)$")
