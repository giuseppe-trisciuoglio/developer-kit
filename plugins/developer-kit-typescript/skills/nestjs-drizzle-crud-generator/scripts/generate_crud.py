#!/usr/bin/env python3
"""
NestJS Drizzle CRUD Generator

Usage:
    generate_crud.py --feature <feature-name> --fields <fields-json> [--output <output-dir>]

Example:
    generate_crud.py --feature user --fields '[{"name": "name", "type": "string", "required": true}, {"name": "email", "type": "string", "required": true}]' --output ./libs/server
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


def to_camel_case(text: str) -> str:
    """Convert to camelCase"""
    components = text.replace('-', '_').split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def to_pascal_case(text: str) -> str:
    """Convert to PascalCase"""
    return ''.join(x.title() for x in text.replace('-', '_').split('_'))


def to_snake_case(text: str) -> str:
    """Convert to snake_case"""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()


def read_template(template_name: str) -> str:
    """Read template file from assets/templates directory"""
    script_dir = Path(__file__).parent.parent
    template_path = script_dir / 'assets' / 'templates' / template_name

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    return template_path.read_text()


def map_field_type_to_drizzle(field_type: str) -> str:
    """Map TypeScript types to Drizzle column types"""
    type_mapping = {
        'string': 'text',
        'text': 'text',
        'number': 'real',
        'integer': 'integer',
        'boolean': 'boolean',
        'date': 'timestamp',
        'uuid': 'uuid',
        'email': 'text',
    }
    return type_mapping.get(field_type, 'text')


def map_field_type_to_zod(field_type: str) -> str:
    """Map field types to Zod schema types"""
    type_mapping = {
        'string': 'z.string()',
        'text': 'z.string()',
        'number': 'z.number()',
        'integer': 'z.number().int()',
        'boolean': 'z.boolean()',
        'date': 'z.date()',
        'uuid': 'z.string().uuid()',
        'email': 'z.string().email()',
    }
    return type_mapping.get(field_type, 'z.string()')


def generate_table_fields(fields: list[dict]) -> str:
    """Generate table field definitions"""
    lines = []
    for field in fields:
        name = field['name']
        field_type = field.get('type', 'string')
        required = field.get('required', False)
        default = field.get('default')

        drizzle_type = map_field_type_to_drizzle(field_type)

        if field_type == 'uuid':
            line = f"  {name}: {drizzle_type}('{name}').primaryKey().defaultRandom()"
        elif field_type == 'boolean':
            line = f"  {name}: {drizzle_type}('{name}')"
            if default is not None:
                line += f".default({default})"
            elif required:
                line += ".notNull()"
        elif field_type == 'number' or field_type == 'integer':
            line = f"  {name}: {drizzle_type}('{name}')"
            if default is not None:
                line += f".default({default})"
            elif required:
                line += ".notNull()"
        else:
            line = f"  {name}: {drizzle_type}('{name}')"
            if default:
                line += f".default('{default}')"
            elif required:
                line += ".notNull()"

        lines.append(line)

    if not lines:
        return ''

    # Add comma to all lines except the last one
    lines_with_commas = [line + ',' for line in lines[:-1]]
    if lines:
        lines_with_commas.append(lines[-1])

    return '\n'.join(lines_with_commas)


def generate_create_fields(fields: list[dict]) -> str:
    """Generate create schema fields"""
    lines = []
    for field in fields:
        name = field['name']
        field_type = field.get('type', 'string')
        required = field.get('required', False)
        max_length = field.get('maxLength')
        min_length = field.get('minLength')

        zod_type = map_field_type_to_zod(field_type)

        # Build chain
        if not required:
            zod_type = zod_type.replace('z.', 'z.')

        chain = zod_type
        if min_length:
            chain += f".min({min_length})"
        if max_length:
            chain += f".max({max_length})"
        if not required:
            chain += ".optional()"

        lines.append(f"  {name}: {chain}")

    return ',\n'.join(lines)


def generate_filter_fields(fields: list[dict]) -> str:
    """Generate filter query fields"""
    lines = []
    for field in fields:
        name = field['name']
        lines.append(f"  {name}: z.{map_field_type_to_zod(field.get('type', 'string')).replace('z.', '')}")

    return ',\n'.join(lines)


def generate_mock_fields(fields: list[dict]) -> str:
    """Generate mock fields for tests"""
    lines = []
    for field in fields:
        name = field['name']
        field_type = field.get('type', 'string')

        if field_type == 'boolean':
            lines.append(f"    {name}: true,")
        elif field_type == 'number' or field_type == 'integer':
            lines.append(f"    {name}: 1,")
        elif field_type == 'date':
            lines.append(f"    {name}: new Date(),")
        else:
            lines.append(f"    {name}: 'test_{name}',")

    return '\n'.join(lines)


def generate_create_dto(fields: list[dict]) -> str:
    """Generate create DTO mock for tests"""
    lines = []
    for field in fields:
        name = field['name']
        field_type = field.get('type', 'string')

        if field_type == 'boolean':
            lines.append(f"    {name}: true,")
        elif field_type == 'number' or field_type == 'integer':
            lines.append(f"    {name}: 1,")
        elif field_type == 'date':
            lines.append(f"    {name}: new Date(),")
        else:
            lines.append(f"    {name}: 'test_{name}',")

    return '\n'.join(lines)


def generate_update_dto(fields: list[dict]) -> str:
    """Generate update DTO mock for tests (all optional)"""
    lines = []
    for field in fields:
        name = field['name']
        field_type = field.get('type', 'string')

        if field_type == 'boolean':
            lines.append(f"    {name}: true,")
        elif field_type == 'number' or field_type == 'integer':
            lines.append(f"    {name}: 1,")
        else:
            lines.append(f"    {name}: 'updated_{name}',")

    return '\n'.join(lines)


def generate_relation_fields(fields: list[dict]) -> str:
    """Generate relation fields for Drizzle"""
    lines = []
    for field in fields:
        if field.get('relation') == 'hasMany':
            related = to_pascal_case(field.get('related', field['name'] + 's'))
            lines.append(f"  {to_camel_case(field['name'])}: many({related}Table),")

    return '\n'.join(lines) if lines else '  // No relations defined'


def replace_placeholders(template: str, feature_name: str, fields: list[dict]) -> str:
    """Replace all placeholders in template"""
    pascal_name = to_pascal_case(feature_name)
    camel_name = to_camel_case(feature_name)
    snake_name = to_snake_case(feature_name)
    table_name = snake_name + 's'

    result = template

    # Replace FeatureName -> PascalCase
    result = result.replace('{{FeatureName}}', pascal_name)

    # Replace featureName -> camelCase
    result = result.replace('{{featureName}}', camel_name)

    # Replace tableName
    result = result.replace('{{tableName}}', table_name)

    # Generate field-specific content
    result = result.replace('{{TableFields}}', generate_table_fields(fields))
    result = result.replace('{{TableFieldsSuffix}}', ',\n' if fields else '')
    result = result.replace('{{CreateFields}}', generate_create_fields(fields))
    result = result.replace('{{FilterFields}}', generate_filter_fields(fields))
    result = result.replace('{{MockFields}}', generate_mock_fields(fields))
    result = result.replace('{{CreateDtoMock}}', '{' + generate_create_dto(fields) + '}')
    result = result.replace('{{UpdateDtoMock}}', '{' + generate_update_dto(fields) + '}')
    result = result.replace('{{RelationFields}}', generate_relation_fields(fields))

    return result


def create_directory_structure(base_path: str, feature_name: str) -> Path:
    """Create the NestJS module directory structure"""
    camel_name = to_camel_case(feature_name)
    base = Path(base_path)

    # Create directory structure
    src_dir = base / camel_name / 'src'
    lib_dir = src_dir / 'lib'
    controllers_dir = lib_dir / 'controllers'
    services_dir = lib_dir / 'services'
    dto_dir = lib_dir / 'dto'
    schema_dir = lib_dir / 'schema'

    for dir_path in [src_dir, lib_dir, controllers_dir, services_dir, dto_dir, schema_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    return lib_dir


def generate_files(feature_name: str, fields: list[dict], output_dir: str):
    """Generate all CRUD files"""
    feature_dir = create_directory_structure(output_dir, feature_name)
    camel_name = to_camel_case(feature_name)
    pascal_name = to_pascal_case(feature_name)

    # Generate module
    module_template = read_template('module-template.ts')
    module_content = replace_placeholders(module_template, feature_name, fields)
    (feature_dir / f'{camel_name}-feature.module.ts').write_text(module_content)

    # Generate controller
    controller_template = read_template('controller-template.ts')
    controller_content = replace_placeholders(controller_template, feature_name, fields)
    (feature_dir / 'controllers' / f'{camel_name}.controller.ts').write_text(controller_content)

    # Generate controller index
    (feature_dir / 'controllers' / 'index.ts').write_text(
        f"export * from './{camel_name}.controller';\n"
    )

    # Generate service
    service_template = read_template('service-template.ts')
    service_content = replace_placeholders(service_template, feature_name, fields)
    (feature_dir / 'services' / f'{camel_name}.service.ts').write_text(service_content)

    # Generate service index
    (feature_dir / 'services' / 'index.ts').write_text(
        f"export * from './{camel_name}.service';\n"
    )

    # Generate DTO
    dto_template = read_template('dto-template.ts')
    dto_content = replace_placeholders(dto_template, feature_name, fields)
    (feature_dir / 'dto' / f'{camel_name}.dto.ts').write_text(dto_content)

    # Generate DTO index
    (feature_dir / 'dto' / 'index.ts').write_text(
        f"export * from './{camel_name}.dto';\n"
    )

    # Generate table/schema
    table_template = read_template('table-template.ts')
    table_content = replace_placeholders(table_template, feature_name, fields)
    (feature_dir / 'schema' / f'{camel_name}.table.ts').write_text(table_content)

    # Generate index
    (feature_dir / 'index.ts').write_text(
        f"""export * from './{camel_name}-feature.module';
export * from './controllers';
export * from './services';
export * from './dto';
export * from './schema/{camel_name}.table';
"""
    )

    # Generate test
    test_template = read_template('test-template.ts')
    test_content = replace_placeholders(test_template, feature_name, fields)
    (feature_dir / 'services' / f'{camel_name}.service.spec.ts').write_text(test_content)

    # Generate src index
    src_dir = feature_dir.parent.parent
    (src_dir / 'index.ts').write_text(
        f"export * from './lib';\n"
    )

    print(f"✅ Generated CRUD module for '{pascal_name}' at {feature_dir}")


def main():
    parser = argparse.ArgumentParser(description='Generate NestJS Drizzle CRUD module')
    parser.add_argument('--feature', required=True, help='Feature name (e.g., user, product)')
    parser.add_argument('--fields', required=True, help='JSON array of field definitions')
    parser.add_argument('--output', default='./libs/server', help='Output directory')

    args = parser.parse_args()

    try:
        fields = json.loads(args.fields)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing fields JSON: {e}")
        sys.exit(1)

    if not isinstance(fields, list):
        print("❌ Error: fields must be a JSON array")
        sys.exit(1)

    generate_files(args.feature, fields, args.output)


if __name__ == '__main__':
    main()
