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


# ---------------------------------------------------------
# Together AI (hosts many open-model families under vendor/model
# namespaces, e.g. "meta-llama/Llama-3.3-70B-Instruct-Turbo"). Unlike
# the other providers' patterns above, this is NOT a full-name anchor -
# it searches for a "<size>B" or "<n>x<size>B" token anywhere in the
# model name, since Together's catalog spans far too many vendor
# naming conventions for one anchored pattern to describe.
# Examples:
#   Llama-3.3-70B-Instruct-Turbo  -> size="70"
#   Llama-3.1-8B-Instruct-Turbo   -> size="8"
#   Qwen2.5-32B-Instruct          -> size="32"
#   Mixtral-8x7B-Instruct-v0.1    -> moe="8", moe_size="7"
# ---------------------------------------------------------
TOGETHER_PATTERN = re.compile(
    r"(?:(?P<moe>[0-9]+)x(?P<moe_size>[0-9]+)b" r"|(?P<size>[0-9]+(?:\.[0-9]+)?)b)",
    re.IGNORECASE,
)


# ---------------------------------------------------------
# Fireworks AI (hosts open models under
# "accounts/fireworks/models/<slug>", e.g.
# "accounts/fireworks/models/llama-v3p3-70b-instruct" - note Fireworks
# uses "p" in place of "." for version numbers, e.g. "v3p3" = "v3.3").
# Same search-based approach as TOGETHER_PATTERN, for the same reason:
# looks for a "<size>B" or "<n>x<size>B" token anywhere in the model
# name rather than anchoring the whole name.
# Examples:
#   accounts/fireworks/models/llama-v3p3-70b-instruct  -> size="70"
#   accounts/fireworks/models/llama-v3p1-8b-instruct    -> size="8"
#   accounts/fireworks/models/qwen2p5-32b-instruct      -> size="32"
#   accounts/fireworks/models/mixtral-8x22b-instruct    -> moe="8", moe_size="22"
# ---------------------------------------------------------
FIREWORKS_PATTERN = re.compile(
    r"(?:(?P<moe>[0-9]+)x(?P<moe_size>[0-9]+)b" r"|(?P<size>[0-9]+(?:\.[0-9]+)?)b)",
    re.IGNORECASE,
)


# ---------------------------------------------------------
# Cerebras (hosts open models under bare IDs, e.g. "qwen-3-32b",
# "llama3.1-8b" - note some Cerebras IDs drop the hyphen after
# "llama" that Groq/Together/Fireworks all use). Same search-based
# size-token approach as TOGETHER_PATTERN/FIREWORKS_PATTERN, used as
# the fallback path for dense models in classify_cerebras_models();
# Llama 4's MoE models (llama-4-scout/-maverick) are classified by
# codename instead, since their names only expose *active* params
# (e.g. "17b"), not total params, which would misclassify their tier.
# Examples:
#   qwen-3-32b       -> size="32"
#   llama3.1-8b       -> size="8"
#   qwen-3-235b-a22b-instruct-2507 -> size="235" (first size token wins)
# ---------------------------------------------------------
CEREBRAS_PATTERN = re.compile(r"(?P<size>[0-9]+(?:\.[0-9]+)?)b", re.IGNORECASE)


# ---------------------------------------------------------
# Perplexity (search-grounded "sonar" family). Unlike the open-model
# providers above, Perplexity's catalog is small and fixed with no
# parameter-size info in the name, so this is a full-name anchor with
# a tier suffix, same shape as XAI_PATTERN.
# Examples:
#   sonar
#   sonar-pro
#   sonar-reasoning
#   sonar-reasoning-pro
#   sonar-deep-research
# Capture group 1 = optional suffix (pro, reasoning, reasoning-pro,
# deep-research).
# ---------------------------------------------------------
PERPLEXITY_PATTERN = re.compile(
    r"^sonar(?:-(pro|reasoning-pro|reasoning|deep-research))?$"
)
