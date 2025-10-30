# CRUD Generator Templates

You must provide all templates (.tpl) required by the generator; there is no fallback.

How it works:
- The generator loads .tpl files from this directory (or a directory passed via --templates-dir).
- It uses Python string.Template placeholders (e.g., $package, $entity, $id_type, $id_name, $id_name_lower, $base_path, $dto_request, $dto_response).
- If any template is missing or fails to render, generation fails.

Required template filenames:
- DomainModel.java.tpl
- DomainRepository.java.tpl
- JpaEntity.java.tpl
- SpringDataRepository.java.tpl
- PersistenceAdapter.java.tpl
- CreateService.java.tpl
- GetService.java.tpl
- UpdateService.java.tpl
- DeleteService.java.tpl
- ListService.java.tpl
- DtoRequest.java.tpl
- DtoResponse.java.tpl
- Controller.java.tpl

Tip: Start simple and expand over time; these files are your team’s baseline.
