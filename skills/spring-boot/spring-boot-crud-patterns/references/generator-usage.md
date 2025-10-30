# CRUD Generator Usage (Templates Required)

Run with a spec and templates directory:

```
python skills/spring-boot/spring-boot-crud-patterns/scripts/generate_crud_boilerplate.py \
  --spec skills/spring-boot/spring-boot-crud-patterns/assets/specs/product.json \
  --package com.example.product \
  --output ./generated \
  --templates-dir skills/spring-boot/spring-boot-crud-patterns/templates
```

Notes:
- All 9 templates must exist and render, or generation fails.
- Customize templates to your team’s conventions.
