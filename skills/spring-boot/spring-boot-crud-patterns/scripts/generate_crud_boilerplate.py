#!/usr/bin/env python3
"""
Spring Boot CRUD boilerplate generator

Given an entity spec, scaffold a feature-based CRUD template aligned with the
"Spring Boot CRUD Patterns" skill (domain/application/presentation/infrastructure).

Usage:
  python skills/spring-boot/spring-boot-crud-patterns/scripts/generate_crud_boilerplate.py \
    --spec entity.json --package com.example.product --output ./generated

Spec format (JSON preferred; YAML supported if PyYAML is installed and file ends with .yml/.yaml):
{
  "entity": "Product",
  "id": {"name": "id", "type": "Long", "generated": true},
  "fields": [
    {"name": "name", "type": "String"},
    {"name": "price", "type": "BigDecimal"},
    {"name": "inStock", "type": "Boolean"}
  ]
}

Notes:
- Generates a feature folder with domain/application/presentation/infrastructure subpackages
- Uses Java records for DTOs, constructor injection, @Transactional, and standard REST codes
- Keep output as a starting point; adapt to your conventions
"""

import argparse
import json
import os
import re
import sys
from textwrap import dedent
from string import Template

try:
    import yaml  # type: ignore
    _HAS_YAML = True
except Exception:
    _HAS_YAML = False

# ------------------------- Helpers -------------------------

JAVA_TYPE_IMPORTS = {
    "BigDecimal": "import java.math.BigDecimal;",
    "UUID": "import java.util.UUID;",
    "LocalDate": "import java.time.LocalDate;",
    "LocalDateTime": "import java.time.LocalDateTime;",
}

JPA_IMPORTS = dedent(
    """
    import jakarta.persistence.*;
    import jakarta.validation.constraints.*;
    """
).strip()

COLLECTION_IMPORTS = "import java.util.Set;"

SPRING_IMPORTS = dedent(
    """
    import org.springframework.stereotype.Service;
    import org.springframework.transaction.annotation.Transactional;
    """
).strip()

CONTROLLER_IMPORTS = dedent(
    """
    import org.springframework.http.ResponseEntity;
    import org.springframework.web.bind.annotation.*;
    import jakarta.validation.Valid;
    """
).strip()

REPOSITORY_IMPORTS = "import org.springframework.data.jpa.repository.JpaRepository;"

SUPPORTED_SIMPLE_TYPES = {
    # primitive/object pairs default to wrapper types for null-safety in DTOs
    "String": "String",
    "Long": "Long",
    "Integer": "Integer",
    "Boolean": "Boolean",
    "BigDecimal": "BigDecimal",
    "UUID": "UUID",
    "LocalDate": "LocalDate",
    "LocalDateTime": "LocalDateTime",
}


def load_spec(spec_path: str) -> dict:
    with open(spec_path, "r", encoding="utf-8") as f:
        text = f.read()
    if spec_path.endswith('.yml') or spec_path.endswith('.yaml'):
        if not _HAS_YAML:
            raise SystemExit("PyYAML not installed. Install with `pip install pyyaml` or provide JSON spec.")
        return yaml.safe_load(text)
    return json.loads(text)


def camel_to_snake(name: str) -> str:
    import re as _re
    s1 = _re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return _re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def lower_first(s: str) -> str:
    return s[:1].lower() + s[1:] if s else s


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_file(path: str, content: str) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.rstrip() + "\n")

def write_file_if_absent(path: str, content: str) -> None:
    if os.path.exists(path):
        return
    write_file(path, content)


def qualify_imports(types: list[str]) -> str:
    imports = []
    for t in types:
        imp = JAVA_TYPE_IMPORTS.get(t)
        if imp and imp not in imports:
            imports.append(imp)
    return "\n".join(imports)


def indent_block(s: str, n: int = 4) -> str:
    prefix = " " * n
    return "\n".join((prefix + line if line.strip() else line) for line in (s or "").splitlines())


# ------------------------- Template loading -------------------------

def load_template_text(templates_dir: str | None, filename: str) -> str | None:
    if not templates_dir:
        return None
    candidate = os.path.join(templates_dir, filename)
    if os.path.isfile(candidate):
        with open(candidate, "r", encoding="utf-8") as f:
            return f.read()
    return None


def render_template_file(templates_dir: str | None, filename: str, placeholders: dict) -> str | None:
    text = load_template_text(templates_dir, filename)
    if text is None:
        return None
    try:
        return Template(text).safe_substitute(placeholders).rstrip() + "\n"
    except Exception:
        # On any template error, fall back to defaults
        return None

# ------------------------- Templates -------------------------

def tmpl_domain_model(pkg: str, entity: str, id: dict, fields: list[dict], use_lombok: bool = False) -> str:
    used_types = {id["type"]} | {f["type"] for f in fields}
    extra_imports = qualify_imports(sorted(used_types))
    fields_src = []
    for f in [id, *fields]:
        fields_src.append(f"    private final {f['type']} {f['name']};")
    ctor_params = ", ".join([f"{f['type']} {f['name']}" for f in [id, *fields]])
    assigns = "\n".join([f"        this.{f['name']} = {f['name']};" for f in [id, *fields]])
    lombok_import = "import lombok.Getter;" if use_lombok else ""
    extra_imports_full = "\n".join(filter(None, [extra_imports, lombok_import]))
    class_annot = "@Getter\n" if use_lombok else ""
    getters = "\n".join([f"    public {f['type']} {('get' + f['name'][0].upper() + f['name'][1:])}() {{ return {f['name']}; }}" for f in [id, *fields]]) if not use_lombok else ""

    return dedent(f"""
package {pkg}.domain.model;

{extra_imports_full}

/**
 * Domain aggregate for {entity}.
 * Keep framework-free; capture invariants in factories/methods.
 */
{class_annot}public class {entity} {{
    {os.linesep.join(fields_src)}

        private {entity}({ctor_params}) {{
    {assigns}
        }}

        public static {entity} create({ctor_params}) {{
            // TODO: add invariant checks
            return new {entity}({', '.join([f['name'] for f in [id, *fields]])});
        }}

    {getters}
    }}
    """)


def tmpl_domain_repository(pkg: str, entity: str, id_type: str) -> str:
    return dedent(f"""
    package {pkg}.domain.repository;

    import java.util.Optional;
    import java.util.List;
    import {pkg}.domain.model.{entity};

    public interface {entity}Repository {{
        {entity} save({entity} aggregate);
        Optional<{entity}> findById({id_type} id);
        List<{entity}> findAll(int page, int size);
        void deleteById({id_type} id);
        boolean existsById({id_type} id);
        long count();
    }}
    """)


def tmpl_jpa_entity(pkg: str, entity: str, id: dict, fields: list[dict], relationships: list[dict], use_lombok: bool = False) -> str:
    used_types = {id["type"]} | {f["type"] for f in fields}
    extra_imports = qualify_imports(sorted(used_types))
    id_ann = "@GeneratedValue(strategy = GenerationType.IDENTITY)" if id["type"] == "Long" and id.get("generated", True) else ""
    all_fields = [id, *fields]
    fields_src = [
        f"    private {f['type']} {f['name']};" if f is id else f"    @Column(nullable = false)\n    private {f['type']} {f['name']};"
        for f in all_fields
    ]

    # Relationship fields and imports
    rel_fields_src = []
    target_imports = []
    need_set = False
    for r in relationships or []:
        rtype = (r.get("type") or "").upper()
        name = r.get("name")
        target = r.get("target")
        if not name or not target or rtype not in {"ONE_TO_ONE", "ONE_TO_MANY", "MANY_TO_MANY"}:
            continue
        target_import = f"import {pkg}.infrastructure.persistence.{target}Entity;"
        if target_import not in target_imports:
            target_imports.append(target_import)
        annotations = []
        if rtype == "ONE_TO_ONE":
            mapped_by = r.get("mappedBy")
            optional = r.get("optional", True)
            if mapped_by:
                annotations.append(f"    @OneToOne(mappedBy = \"{mapped_by}\", fetch = FetchType.LAZY)")
            else:
                annotations.append(f"    @OneToOne(fetch = FetchType.LAZY, optional = {str(optional).lower()})")
                join_col = r.get("joinColumn")
                if join_col:
                    annotations.append(f"    @JoinColumn(name = \"{join_col}\")")
            field_type = f"{target}Entity"
            init = ""
        elif rtype == "ONE_TO_MANY":
            need_set = True
            mapped_by = r.get("mappedBy")
            if mapped_by:
                annotations.append(f"    @OneToMany(mappedBy = \"{mapped_by}\", fetch = FetchType.LAZY)")
            else:
                annotations.append("    @OneToMany(fetch = FetchType.LAZY)")
                join_col = r.get("joinColumn")
                if join_col:
                    annotations.append(f"    @JoinColumn(name = \"{join_col}\")")
            field_type = f"Set<{target}Entity>"
            init = " = new java.util.LinkedHashSet<>()"
        else:  # MANY_TO_MANY
            need_set = True
            annotations.append("    @ManyToMany(fetch = FetchType.LAZY)")
            jt = r.get("joinTable") or {}
            jt_name = jt.get("name")
            join_col = jt.get("joinColumn")
            inv_join_col = jt.get("inverseJoinColumn")
            if jt_name and join_col and inv_join_col:
                annotations.append(
                    f"    @JoinTable(name = \"{jt_name}\", joinColumns = @JoinColumn(name = \"{join_col}\"), inverseJoinColumns = @JoinColumn(name = \"{inv_join_col}\"))"
                )
            field_type = f"Set<{target}Entity>"
            init = " = new java.util.LinkedHashSet<>()"
        rel_fields_src.append("\n".join(annotations + [f"    private {field_type} {name}{init};"]))

    rel_block = ("\n" + os.linesep.join(rel_fields_src)) if rel_fields_src else ""

    lombok_imports = ("\n".join([
        "import lombok.Getter;",
        "import lombok.Setter;",
        "import lombok.NoArgsConstructor;",
        "import lombok.AccessLevel;",
    ]) if use_lombok else "")
    imports_block = "\n".join(filter(None, [JPA_IMPORTS, extra_imports, COLLECTION_IMPORTS if need_set else "", "\n".join(target_imports), lombok_imports]))
    imports_block_indented = indent_block(imports_block)

    rel_getters = os.linesep.join([
        f"        public {('Set<' + r['target'] + 'Entity>' if r['type'].upper() != 'ONE_TO_ONE' else r['target'] + 'Entity')} get{r['name'][0].upper() + r['name'][1:]}() {{ return {r['name']}; }}"
        for r in (relationships or []) if r.get('name') and r.get('target') and r.get('type', '').upper() in {"ONE_TO_ONE", "ONE_TO_MANY", "MANY_TO_MANY"}
    ]) if not use_lombok else ""
    rel_setters = os.linesep.join([
        f"        public void set{r['name'][0].upper() + r['name'][1:]}({('Set<' + r['target'] + 'Entity>' if r['type'].upper() != 'ONE_TO_ONE' else r['target'] + 'Entity')} {r['name']}) {{ this.{r['name']} = {r['name']}; }}"
        for r in (relationships or []) if r.get('name') and r.get('target') and r.get('type', '').upper() in {"ONE_TO_ONE", "ONE_TO_MANY", "MANY_TO_MANY"}
    ]) if not use_lombok else ""

    class_annots = ("\n".join([
        "@Getter",
        "@Setter",
        "@NoArgsConstructor(access = AccessLevel.PROTECTED)",
    ]) + "\n") if use_lombok else ""
    class_annots_block = indent_block(class_annots.strip()) if use_lombok else ""

    fields_getters = os.linesep.join([f"        public {f['type']} {('get' + f['name'][0].upper() + f['name'][1:])}() {{ return {f['name']}; }}" for f in all_fields]) if not use_lombok else ""
    fields_setters = os.linesep.join([f"        public void set{f['name'][0].upper() + f['name'][1:]}({f['type']} {f['name']}) {{ this.{f['name']} = {f['name']}; }}" for f in all_fields]) if not use_lombok else ""

    return dedent(f"""
package {pkg}.infrastructure.persistence;

{imports_block}

@Entity
@Table(name = "{camel_to_snake(entity)}")
{class_annots}public class {entity}Entity {{
    @Id
    {id_ann}
    private {id['type']} {id['name']};
{os.linesep.join(fields_src[1:])}
{rel_block}

        {'' if use_lombok else f'protected {entity}Entity() {{ /* for JPA */ }}'}

        public {entity}Entity({', '.join([f['type'] + ' ' + f['name'] for f in all_fields])}) {{
{os.linesep.join([f"            this.{f['name']} = {f['name']};" for f in all_fields])}
        }}

{fields_getters}
{fields_setters}
{rel_getters}
{rel_setters}
    }}
    """)


def tmpl_spring_data_repo(pkg: str, entity: str, id_type: str) -> str:
    return dedent(f"""
    package {pkg}.infrastructure.persistence;

{indent_block(REPOSITORY_IMPORTS)}

    public interface {entity}JpaRepository extends JpaRepository<{entity}Entity, {id_type}> {{}}
    """)


def tmpl_persistence_adapter(pkg: str, entity: str, id: dict, fields: list[dict], use_lombok: bool = False) -> str:
    return dedent(f"""
package {pkg}.infrastructure.persistence;

import java.util.Optional;
import java.util.List;
import java.util.stream.Collectors;

import {pkg}.domain.model.{entity};
import {pkg}.domain.repository.{entity}Repository;

import org.springframework.stereotype.Component;
{('import lombok.RequiredArgsConstructor;' if use_lombok else '')}

@Component
{('@RequiredArgsConstructor' if use_lombok else '')}
public class {entity}RepositoryAdapter implements {entity}Repository {{

        private final {entity}JpaRepository jpa;

        {'' if use_lombok else f'public {entity}RepositoryAdapter({entity}JpaRepository jpa) {{\n            this.jpa = jpa;\n        }}'}

        @Override
        public {entity} save({entity} aggregate) {{
            {entity}Entity e = toEntity(aggregate);
            e = jpa.save(e);
            return toDomain(e);
        }}

        @Override
        public Optional<{entity}> findById({id['type']} id) {{
            return jpa.findById(id).map(this::toDomain);
        }}

        @Override
        public List<{entity}> findAll(int page, int size) {{
            return jpa.findAll(org.springframework.data.domain.PageRequest.of(page, size))
                    .stream().map(this::toDomain).collect(java.util.stream.Collectors.toList());
        }}

        @Override
        public void deleteById({id['type']} id) {{
            jpa.deleteById(id);
        }}

        @Override
        public boolean existsById({id['type']} id) {{
            return jpa.existsById(id);
        }}

        @Override
        public long count() {{
            return jpa.count();
        }}

        private {entity}Entity toEntity({entity} a) {{
            return new {entity}Entity({', '.join(['a.get' + id['name'][0].upper() + id['name'][1:] + '()'] + ['a.get' + f['name'][0].upper() + f['name'][1:] + '()' for f in fields])});
        }}

        private {entity} toDomain({entity}Entity e) {{
            return {entity}.create({', '.join(['e.get' + id['name'][0].upper() + id['name'][1:] + '()'] + ['e.get' + f['name'][0].upper() + f['name'][1:] + '()' for f in fields])});
        }}
    }}
    """)


def tmpl_application_service(pkg: str, entity: str, id: dict, fields: list[dict], use_lombok: bool = False) -> str:
    lc_entity = lower_first(entity)
    dto_req = f"{entity}Request"
    dto_res = f"{entity}Response"
    params = ", ".join([f"request.{f['name']}()" for f in [id, *fields]])
    update_params = ", ".join([f"request.{f['name']}()" for f in [*fields]])

    return dedent(f"""
    package {pkg}.application.service;

{indent_block(SPRING_IMPORTS)}

    import java.util.List;

    import {pkg}.domain.model.{entity};
    import {pkg}.domain.repository.{entity}Repository;
    import {pkg}.presentation.dto.{dto_req};
    import {pkg}.presentation.dto.{dto_res};

    @Service
    @Transactional
    public class {entity}Service {{

        private final {entity}Repository repository;

        public {entity}Service({entity}Repository repository) {{
            this.repository = repository;
        }}

        public {dto_res} create({dto_req} request) {{
            {entity} {lc_entity} = {entity}.create({params});
            {lc_entity} = repository.save({lc_entity});
            return {dto_res}.from({lc_entity});
        }}

        @Transactional(readOnly = true)
        public {dto_res} get({id['type']} id) {{
            return repository.findById(id).map({dto_res}::from)
                    .orElseThrow(() -> new org.springframework.web.server.ResponseStatusException(org.springframework.http.HttpStatus.NOT_FOUND));
        }}

        public {dto_res} update({dto_req} request) {{
            // In a real app, load existing aggregate and apply changes
            {entity} updated = {entity}.create(request.{id['name']}(), {update_params});
            updated = repository.save(updated);
            return {dto_res}.from(updated);
        }}

        public void delete({id['type']} id) {{
            repository.deleteById(id);
        }}

        @Transactional(readOnly = true)
        public java.util.List<{dto_res}> list(int page, int size) {{
            return repository.findAll(page, size).stream().map({dto_res}::from).collect(java.util.stream.Collectors.toList());
        }}
    }}
    """)


def tmpl_dto_request(pkg: str, entity: str, id: dict, fields: list[dict]) -> str:
    used_types = {id["type"]} | {f["type"] for f in fields}
    extra_imports = qualify_imports(sorted(used_types))
    comps = ", ".join([f"{f['type']} {f['name']}" for f in [id, *fields]])
    return dedent(f"""
package {pkg}.presentation.dto;

{extra_imports}

public record {entity}Request({comps}) {{ }}
    """)


def tmpl_dto_response(pkg: str, entity: str, id: dict, fields: list[dict]) -> str:
    used_types = {id["type"]} | {f["type"] for f in fields}
    extra_imports = qualify_imports(sorted(used_types))
    comps = ", ".join([f"{f['type']} {f['name']}" for f in [id, *fields]])
    getters = ", ".join([f"aggregate.get{f['name'][0].upper() + f['name'][1:]}()" for f in [id, *fields]])
    return dedent(f"""
    package {pkg}.presentation.dto;

{indent_block(extra_imports)}

    import {pkg}.domain.model.{entity};

    public record {entity}Response({comps}) {{
        public static {entity}Response from({entity} aggregate) {{
            return new {entity}Response({getters});
        }}
    }}
    """)


def tmpl_controller(pkg: str, entity: str, id: dict, use_lombok: bool = False) -> str:
    base = f"/api/{camel_to_snake(entity)}s"  # naive pluralization with 's'
    dto_req = f"{entity}Request"
    dto_res = f"{entity}Response"
    var_name = lower_first(id['name'])
    path_seg = "/{" + var_name + "}"

    return dedent(f"""
    package {pkg}.presentation.rest;

{indent_block(CONTROLLER_IMPORTS)}

    import {pkg}.application.service.{entity}Service;
    import {pkg}.presentation.dto.{dto_req};
    import {pkg}.presentation.dto.{dto_res};

    @RestController
    @RequestMapping("{base}")
    public class {entity}Controller {{

        private final {entity}Service service;

        public {entity}Controller({entity}Service service) {{
            this.service = service;
        }}

        @PostMapping
        public ResponseEntity<{dto_res}> create(@RequestBody @Valid {dto_req} request) {{
            var created = service.create(request);
            return ResponseEntity.status(201).body(created);
        }}

        @GetMapping("{path_seg}")
        public ResponseEntity<{dto_res}> get(@PathVariable {id['type']} {var_name}) {{
            return ResponseEntity.ok(service.get({var_name}));
        }}

        @PutMapping("{path_seg}")
        public ResponseEntity<{dto_res}> update(@PathVariable {id['type']} {var_name},
                                                @RequestBody @Valid {dto_req} request) {{
            // In a real app: ensure path id == request id
            return ResponseEntity.ok(service.update(request));
        }}

        @DeleteMapping("{path_seg}")
        public ResponseEntity<Void> delete(@PathVariable {id['type']} {var_name}) {{
            service.delete({var_name});
            return ResponseEntity.noContent().build();
        }}

        @GetMapping
        public ResponseEntity<java.util.List<{dto_res}>> list(@RequestParam(defaultValue = "0") int page,
                                                               @RequestParam(defaultValue = "20") int size) {{
            return ResponseEntity.ok(service.list(page, size));
        }}
    }}
    """)


# ------------------------- Main -------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate Spring Boot CRUD boilerplate from entity spec")
    parser.add_argument("--spec", required=True, help="Path to entity spec (JSON or YAML)")
    parser.add_argument("--package", required=True, help="Base package, e.g., com.example.product")
    parser.add_argument("--output", default="./generated", help="Output root directory")
    parser.add_argument("--lombok", action="store_true", help="Use Lombok annotations for getters/setters where applicable")
    parser.add_argument("--templates-dir", help="Directory with override templates (*.tpl). If omitted, auto-detects ../templates relative to this script if present.")
    args = parser.parse_args()

    spec = load_spec(args.spec)

    entity = spec.get("entity")
    if not entity or not re.match(r"^[A-Z][A-Za-z0-9_]*$", entity):
        raise SystemExit("Spec 'entity' must be a PascalCase identifier, e.g., 'Product'")

    id_spec = spec.get("id") or {"name": "id", "type": "Long", "generated": True}
    if id_spec["type"] not in SUPPORTED_SIMPLE_TYPES:
        raise SystemExit(f"Unsupported id type: {id_spec['type']}")

    fields = spec.get("fields", [])
    relationships = spec.get("relationships", [])
    for f in fields:
        if f["type"] not in SUPPORTED_SIMPLE_TYPES:
            raise SystemExit(f"Unsupported field type: {f['name']} -> {f['type']}")

    feature_name = entity.lower()
    base_pkg = args.package

    out_root = os.path.abspath(args.output)
    java_root = os.path.join(out_root, "src/main/java", base_pkg.replace(".", "/"))

    # Paths
    paths = {
        "domain_model": os.path.join(java_root, "domain/model", f"{entity}.java"),
        "domain_repo": os.path.join(java_root, "domain/repository", f"{entity}Repository.java"),
        "domain_service": os.path.join(java_root, "domain/service", f"{entity}Service.java"),
        "jpa_entity": os.path.join(java_root, "infrastructure/persistence", f"{entity}Entity.java"),
        "spring_data_repo": os.path.join(java_root, "infrastructure/persistence", f"{entity}JpaRepository.java"),
        "persistence_adapter": os.path.join(java_root, "infrastructure/persistence", f"{entity}RepositoryAdapter.java"),
        "app_service_create": os.path.join(java_root, "application/service", f"Create{entity}Service.java"),
        "app_service_get": os.path.join(java_root, "application/service", f"Get{entity}Service.java"),
        "app_service_update": os.path.join(java_root, "application/service", f"Update{entity}Service.java"),
        "app_service_delete": os.path.join(java_root, "application/service", f"Delete{entity}Service.java"),
        "app_service_list": os.path.join(java_root, "application/service", f"List{entity}Service.java"),
        "dto_req": os.path.join(java_root, "presentation/dto", f"{entity}Request.java"),
        "dto_res": os.path.join(java_root, "presentation/dto", f"{entity}Response.java"),
        "controller": os.path.join(java_root, "presentation/rest", f"{entity}Controller.java"),
        "ex_not_found": os.path.join(java_root, "application/exception", f"{entity}NotFoundException.java"),
        "ex_exist": os.path.join(java_root, "application/exception", f"{entity}ExistException.java"),
        "entity_exception_handler": os.path.join(java_root, "presentation/rest", f"{entity}ExceptionHandler.java"),
    }

    # Resolve templates directory (required; no fallback to built-ins)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_templates_dir = os.path.normpath(os.path.join(script_dir, "..", "templates"))
    templates_dir = args.templates_dir or (default_templates_dir if os.path.isdir(default_templates_dir) else None)
    if not templates_dir or not os.path.isdir(templates_dir):
        raise SystemExit("Templates directory not found. Provide --templates-dir or create: " + default_templates_dir)

    required_templates = [
        "DomainModel.java.tpl",
        "DomainRepository.java.tpl",
        "DomainService.java.tpl",
        "JpaEntity.java.tpl",
        "SpringDataRepository.java.tpl",
        "PersistenceAdapter.java.tpl",
        "CreateService.java.tpl",
        "GetService.java.tpl",
        "UpdateService.java.tpl",
        "DeleteService.java.tpl",
        "ListService.java.tpl",
        "DtoRequest.java.tpl",
        "DtoResponse.java.tpl",
        "Controller.java.tpl",
        "NotFoundException.java.tpl",
        "ExistException.java.tpl",
        "EntityExceptionHandler.java.tpl",
    ]
    missing = [name for name in required_templates if load_template_text(templates_dir, name) is None]
    if missing:
        raise SystemExit("Missing required templates: " + ", ".join(missing) + " in " + templates_dir)

    # Build dynamic code fragments for templates
    all_fields = [id_spec, *fields]
    used_types = {f["type"] for f in all_fields}
    extra_imports = qualify_imports(sorted(used_types))

    def cap(s: str) -> str:
        return s[:1].upper() + s[1:] if s else s

    # Domain fragments
    final_kw = "" if args.lombok else "final "
    domain_fields_decls = "\n".join([f"    private {final_kw}{f['type']} {f['name']};" for f in all_fields])
    domain_ctor_params = ", ".join([f"{f['type']} {f['name']}" for f in all_fields])
    domain_assigns = "\n".join([f"        this.{f['name']} = {f['name']};" for f in all_fields])
    domain_getters = ("\n".join([f"    public {f['type']} get{cap(f['name'])}() {{ return {f['name']}; }}" for f in all_fields]) if not args.lombok else "")
    model_constructor_block = (f"    private {entity}({domain_ctor_params}) {{\n{domain_assigns}\n    }}" if not args.lombok else "")
    all_names_csv = ", ".join([f["name"] for f in all_fields])

    # JPA fragments
    def _jpa_field_decl(f: dict) -> str:
        if f is id_spec:
            lines = ["    @Id"]
            if bool(id_spec.get("generated", False)) and id_spec["type"] in ("Long", "Integer"):
                lines.append("    @GeneratedValue(strategy = GenerationType.IDENTITY)")
            lines.append(f"    private {f['type']} {f['name']};")
            return "\n".join(lines)
        return f"    @Column(nullable = false)\n    private {f['type']} {f['name']};"
    jpa_fields_decls = "\n".join([_jpa_field_decl(f) for f in all_fields])
    jpa_ctor_params = domain_ctor_params
    jpa_assigns = "\n".join([f"        this.{f['name']} = {f['name']};" for f in all_fields])
    jpa_getters_setters = "\n".join([
        f"    public {f['type']} get{cap(f['name'])}() {{ return {f['name']}; }}\n    public void set{cap(f['name'])}({f['type']} {f['name']}) {{ this.{f['name']} = {f['name']}; }}" for f in all_fields
    ])

    # DTO components
    id_generated = bool(id_spec.get("generated", False))
    dto_response_components = ", ".join([f"{f['type']} {f['name']}" for f in all_fields])
    dto_request_fields = (fields if id_generated else all_fields)
    dto_request_components = ", ".join([f"{f['type']} {f['name']}" for f in dto_request_fields])

    # Mapping fragments
    adapter_to_entity_args = ", ".join([f"a.get{cap(f['name'])}()" for f in all_fields])
    adapter_to_domain_args = ", ".join([f"e.get{cap(f['name'])}()" for f in all_fields])
    if id_generated:
        request_all_args = ", ".join(["null", *[f"request.{f['name']}()" for f in fields]])
    else:
        request_all_args = ", ".join([f"request.{id_spec['name']}()", *[f"request.{f['name']}()" for f in fields]])
    response_from_agg_args = ", ".join([f"agg.get{cap(f['name'])}()" for f in all_fields])
    list_map_response_args = ", ".join([f"a.get{cap(f['name'])}()" for f in all_fields])
    update_create_args = ", ".join([id_spec["name"], *[f"request.{f['name']}()" for f in fields]])
    mapper_create_args = ", ".join(["id", *[f"request.{f['name']}()" for f in fields]])
    create_id_arg = ("null" if id_generated else f"request.{id_spec['name']}()")

    table_name = camel_to_snake(entity)
    base_path = f"/api/{table_name}"

    # Common placeholders for external templates
    # Lombok-related placeholders
    # Domain model should only have @Getter for DDD immutability
    lombok_domain_imports = "import lombok.Getter;" if args.lombok else ""
    lombok_domain_annotations = "@Getter" if args.lombok else ""
    lombok_domain_annotations_block = ("\n" + lombok_domain_annotations) if lombok_domain_annotations else ""

    lombok_model_imports = "import lombok.Getter;\nimport lombok.Setter;\nimport lombok.AllArgsConstructor;" if args.lombok else ""
    lombok_common_imports = "import lombok.RequiredArgsConstructor;\nimport lombok.extern.slf4j.Slf4j;" if args.lombok else ""
    model_annotations = "@Getter\n@Setter\n@AllArgsConstructor" if args.lombok else ""
    service_annotations = "@RequiredArgsConstructor\n@Slf4j" if args.lombok else ""
    controller_annotations = "@RequiredArgsConstructor\n@Slf4j" if args.lombok else ""
    adapter_annotations = "@RequiredArgsConstructor\n@Slf4j" if args.lombok else ""
    # annotation blocks that include a leading newline when present to avoid empty lines
    service_annotations_block = ("\n" + service_annotations) if service_annotations else ""
    controller_annotations_block = ("\n" + controller_annotations) if controller_annotations else ""
    adapter_annotations_block = ("\n" + adapter_annotations) if adapter_annotations else ""
    model_annotations_block = ("\n" + model_annotations) if model_annotations else ""

    

    # Common placeholders for external templates
    placeholders = {
        "entity": entity,
        "Entity": entity,
        "EntityRequest": f"{entity}Request",
        "EntityResponse": f"{entity}Response",
        "entity_lower": lower_first(entity),
        "package": base_pkg,
        "Package": base_pkg.replace(".", "/"),
        "table_name": table_name,
        "base_path": base_path,
        "id_type": id_spec["type"],
        "id_name": id_spec["name"],
        "id_name_lower": lower_first(id_spec["name"]),
        "id_generated": str(id_generated).lower(),
        "fields": fields,
        "all_fields": all_fields,
        "extra_imports": extra_imports,
        "final_kw": final_kw,
        "domain_fields_decls": domain_fields_decls,
        "domain_ctor_params": domain_ctor_params,
        "domain_assigns": domain_assigns,
        "domain_getters": domain_getters,
        "model_constructor_block": model_constructor_block,
        "all_names_csv": all_names_csv,
        "jpa_fields_decls": jpa_fields_decls,
        "jpa_ctor_params": jpa_ctor_params,
        "jpa_assigns": jpa_assigns,
        "jpa_getters_setters": jpa_getters_setters,
        "dto_response_components": dto_response_components,
        "dto_request_components": dto_request_components,
        "adapter_to_entity_args": adapter_to_entity_args,
        "adapter_to_domain_args": adapter_to_domain_args,
        "request_all_args": request_all_args,
        "response_from_agg_args": response_from_agg_args,
        "list_map_response_args": list_map_response_args,
        "update_create_args": update_create_args,
        "mapper_create_args": mapper_create_args,
        "create_id_arg": create_id_arg,
        # Domain-specific Lombok placeholders (DDD-compliant)
        "lombok_domain_imports": lombok_domain_imports,
        "lombok_domain_annotations_block": lombok_domain_annotations_block,
        # Infrastructure/infrastructure Lombok placeholders
        "lombok_model_imports": lombok_model_imports,
        "lombok_common_imports": lombok_common_imports,
        "model_annotations": model_annotations,
        "service_annotations": service_annotations,
        "controller_annotations": controller_annotations,
        "adapter_annotations": adapter_annotations,
        "service_annotations_block": service_annotations_block,
        "controller_annotations_block": controller_annotations_block,
        "adapter_annotations_block": adapter_annotations_block,
        "model_annotations_block": model_annotations_block,
        # Constructor placeholders
        "controller_constructor": "",
        "adapter_constructor": "",
        "create_constructor": "",
        "update_constructor": "",
        "get_constructor": "",
        "list_constructor": "",
        "delete_constructor": "",
        "domain_service_constructor": "",
    }

    def _render(name, placeholders_dict):
        c = render_template_file(templates_dir, name, placeholders_dict)
        if c is None: raise SystemExit(f"Template render failed: {name}")
        c = (c.replace("$controller_constructor", placeholders_dict.get("controller_constructor", ""))
               .replace("$adapter_constructor", placeholders_dict.get("adapter_constructor", ""))
               .replace("$create_constructor", placeholders_dict.get("create_constructor", ""))
               .replace("$update_constructor", placeholders_dict.get("update_constructor", ""))
               .replace("$get_constructor", placeholders_dict.get("get_constructor", ""))
               .replace("$list_constructor", placeholders_dict.get("list_constructor", ""))
               .replace("$delete_constructor", placeholders_dict.get("delete_constructor", ""))
               .replace("$domain_service_constructor", placeholders_dict.get("domain_service_constructor", "")))
        return c

    # Write files (templates only, fail on error)
    content = _render("DomainModel.java.tpl", placeholders)
    write_file(paths["domain_model"], content)

    content = _render("DomainRepository.java.tpl", placeholders)
    write_file(paths["domain_repo"], content)

    content = _render("DomainService.java.tpl", placeholders)
    write_file(paths["domain_service"], content)

    content = _render("JpaEntity.java.tpl", placeholders)
    write_file(paths["jpa_entity"], content)

    content = _render("SpringDataRepository.java.tpl", placeholders)
    write_file(paths["spring_data_repo"], content)

    content = _render("PersistenceAdapter.java.tpl", placeholders)
    write_file(paths["persistence_adapter"], content)

    content = _render("CreateService.java.tpl", placeholders)
    write_file(paths["app_service_create"], content)

    content = _render("GetService.java.tpl", placeholders)
    write_file(paths["app_service_get"], content)

    content = _render("UpdateService.java.tpl", placeholders)
    write_file(paths["app_service_update"], content)

    content = _render("DeleteService.java.tpl", placeholders)
    write_file(paths["app_service_delete"], content)

    content = _render("ListService.java.tpl", placeholders)
    write_file(paths["app_service_list"], content)

    content = _render("DtoRequest.java.tpl", placeholders)
    write_file(paths["dto_req"], content)

    content = _render("DtoResponse.java.tpl", placeholders)
    write_file(paths["dto_res"], content)

    content = _render("Controller.java.tpl", placeholders)
    write_file(paths["controller"], content)

    # Exceptions
    content = _render("NotFoundException.java.tpl", placeholders)
    write_file(paths["ex_not_found"], content)

    content = _render("ExistException.java.tpl", placeholders)
    write_file(paths["ex_exist"], content)

    content = _render("EntityExceptionHandler.java.tpl", placeholders)
    write_file(paths["entity_exception_handler"], content)

    # Helpful README
    readme = dedent(f"""
    # Generated CRUD Feature: {entity}

    Base package: {base_pkg}

    Structure:
    - domain/model/{entity}.java
    - domain/repository/{entity}Repository.java
    - infrastructure/persistence/{entity}Entity.java
    - infrastructure/persistence/{entity}JpaRepository.java
    - infrastructure/persistence/{entity}RepositoryAdapter.java
    - application/service/Create{entity}Service.java
    - application/service/Get{entity}Service.java
    - application/service/Update{entity}Service.java
    - application/service/Delete{entity}Service.java
    - application/service/List{entity}Service.java
    - presentation/dto/{entity}Request.java
    - presentation/dto/{entity}Response.java
    - presentation/rest/{entity}Controller.java

    Next steps:
    - Add validation and invariants in domain aggregate
    - Secure endpoints and add tests (unit + @DataJpaTest + Testcontainers)
    - Wire into your Spring Boot app (component scan should pick up beans)
    """)
    write_file(os.path.join(out_root, "README-GENERATED.md"), readme)

    print(f"CRUD boilerplate generated under: {out_root}")



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
