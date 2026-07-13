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


# ---------------------------------------------------------
# Groq (hosts open models: Llama, Gemma, Qwen, Mixtral, DeepSeek-distill)
# Examples:
#   llama-3.3-70b-versatile
#   llama-3.1-8b-instant
#   gemma2-9b-it
#   qwen-2.5-32b
#   mixtral-8x7b-32768
#   deepseek-r1-distill-llama-70b
# Capture group 1 = size (e.g. "70", "8", "8x7"); group 2 = optional suffix.
# ---------------------------------------------------------
GROQ_PATTERN = re.compile(
    r"^(?:llama|gemma2?|qwen|mixtral|deepseek-r1-distill-llama)"
    r"(?:-[0-9]+(?:\.[0-9]+)?)?"
    r"-([0-9]+x?[0-9]*)b"
    r"(?:-([a-z0-9]+))?$"
)


# ---------------------------------------------------------
# xAI (Grok)
# Examples:
#   grok-4
#   grok-3
#   grok-3-mini
#   grok-2-vision-1212
# Capture group 1 = optional suffix (mini, vision, fast).
# ---------------------------------------------------------
XAI_PATTERN = re.compile(
    r"^grok-[0-9]+(?:\.[0-9]+)?" r"(?:-(mini|vision|fast))?" r"(?:-[0-9]+)?$"
)
