## TextFSM‑AI DSL Engine  
This directory contains the full implementation of the **TextFSM‑AI DSL**, a structured, reversible, machine‑friendly language for describing token patterns, variable extraction rules, and canonical template transformations.

The DSL engine is built on a layered architecture:

---

## 1. Categories & Patterns

### `categories.py`  
Defines the `BaseCategory` enum and the global `SPECIFICITY_ORDER` used for token classification and keyword inference.

### `aliases.py`  
Maps human‑friendly keyword names to canonical categories.

### `patterns.py`  
Defines the authoritative mapping of keyword → regex and keyword → BaseCategory.

---

## 2. Token & Category Inference

### `charclass.py`  
Character‑level helpers (`is_digit`, `is_letter`, etc.).

### `tokenclass.py`  
Token‑level classification (digit, word, mixed‑word, number, etc.).

### `category_matcher.py`  
Maps tokens to possible BaseCategories.

### `infer.py`  
Infers the most specific keyword for a list of literal tokens.

---

## 3. Normalization & Expressions

### `normalize.py`  
Converts raw text into Node objects using `ExpressionNodeFactory`.

### `expression.py`  
Defines `KeywordExpression`, the canonical semantic representation of a keyword pattern.

### `expression_builder.py`  
Converts `KeywordCall` objects into `KeywordExpression` via `create_node()`.

---

## 4. Node System

### `nodes.py`  
Core of the DSL engine. Contains:

- `KeywordNode`, `VariableKeywordNode`, `CustomKeywordNode`
- `LiteralNode`
- Quantifier nodes: `OptionalNode`, `ZeroOrMoreNode`, `OneOrMoreNode`
- Quantity nodes: `ExactCountNode`, `RangeQuantityNode`
- Negation: `NotNode`
- Node factory: `create_node()`

All DSL transformations ultimately route through this module.

---

## 5. DSL Rendering & Parsing

### `dsl_renderer.py`  
Converts Node lists into human‑readable DSL strings.

### `dsl_reverse.py`  
Parses DSL strings back into Node lists.

---

## 6. Template & Variable Inference

### `variable_infer.py`  
Infers variable keyword + regex from sample TextFSM records.

### `template_canonicalizer.py`  
Canonicalizes TextFSM `Value` lines using inferred regexes.

### `dsl_extractor.py`  
Extracts machine DSL (variables + states) from a TextFSM template.

---

## 7. Design Principles

- **Strict layering**: lexical → inference → nodes → DSL transforms  
- **Reversible**: DSL → nodes → DSL round‑trip stability  
- **Generalization‑aware**: keyword generalization is centralized in `create_node()`  
- **Pattern‑driven**: all regexes come from `patterns.py`  
- **Extensible**: new keywords and node types can be added without modifying core logic  
