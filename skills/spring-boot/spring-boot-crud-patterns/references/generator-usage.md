# CRUD Generator Usage

Quick start:

```
python skills/spring-boot/spring-boot-crud-patterns/scripts/generate_crud_boilerplate.py \
  --spec skills/spring-boot/spring-boot-crud-patterns/assets/specs/product.json \
  --package com.example.product \
  --output ./generated \
  --templates-dir skills/spring-boot/spring-boot-crud-patterns/templates [--lombok]
```

Spec (JSON/YAML):
- entity: PascalCase name (e.g., Product)
- id: { name, type (Long|UUID|...), generated: true|false }
- fields: array of { name, type }
- relationships: optional (currently model as FK ids in fields)

What gets generated:
- REST controller at /v1/{resources} with POST 201 + Location header
- Pageable list endpoint returning PageResponse<T>
- Application mapper (application/mapper/${Entity}Mapper) for DTO↔Domain
- Exception types: ${Entity}NotFoundException, ${Entity}ExistException + ${Entity}ExceptionHandler
- GlobalExceptionHandler with validation + DataIntegrityViolationException→409

DTOs:
- Request excludes id when id.generated=true
- Response always includes id

JPA entity:
- @Id with @GeneratedValue(IDENTITY) for numeric generated ids

Notes:
- Provide all templates in templates/ (see templates/README.md)
- Use --lombok to add Lombok annotations without introducing blank lines between annotations
