# 🧩 **Final DSL Architecture Diagram**

Below is a **text‑based architecture diagram** you can drop directly into your repo.  
It reflects the *actual* dependency flow of your modern DSL engine.

```
textfsm_ai/dsl/
│
├── categories.py
│     └─ BaseCategory enum + SPECIFICITY_ORDER
│
├── aliases.py
│     └─ human keyword aliases → BaseCategory
│
├── patterns.py
│     └─ keyword → regex + BaseCategory mapping
│
├── charclass.py
│     └─ character-level helpers
│
├── tokenclass.py
│     └─ token-level classification (digit, word, mixed-word, etc.)
│
├── category_matcher.py
│     └─ token → BaseCategory inference
│
├── infer.py
│     └─ literal tokens → keyword inference
│
├── normalize.py
│     └─ raw text → Node list (via ExpressionNodeFactory)
│
├── expression.py
│     └─ KeywordExpression dataclass (canonical semantic form)
│
├── nodes.py
│     ├─ KeywordNode / VariableKeywordNode / CustomKeywordNode
│     ├─ LiteralNode
│     ├─ Optional / Maybe / Not
│     ├─ ZeroOrMore / OneOrMore
│     ├─ ExactCount / RangeQuantity
│     └─ create_node() factory
│
├── expression_builder.py
│     └─ KeywordCall → KeywordExpression (via create_node)
│
├── dsl_renderer.py
│     └─ Node list → human DSL string
│
├── dsl_reverse.py
│     └─ human DSL string → Node list
│
├── variable_infer.py
│     └─ infer variable keyword + regex from sample records
│
├── template_canonicalizer.py
│     └─ canonicalize TextFSM Value lines using inferred regexes
│
└── dsl_extractor.py
      └─ TextFSM template → machine DSL (variables + states)
```

This diagram is intentionally **layered**:

- **Lexical layer**: charclass, tokenclass, category_matcher  
- **Inference layer**: infer, normalize  
- **Node system**: nodes, expression  
- **DSL transforms**: renderer, reverse, expression_builder  
- **Template transforms**: extractor, canonicalizer  
- **Variable inference**: variable_infer  
