package $package.presentation.rest;

$lombok_common_imports
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;

import $package.application.service.Create${entity}Service;
import $package.application.service.Get${entity}Service;
import $package.application.service.Update${entity}Service;
import $package.application.service.Delete${entity}Service;
import $package.application.service.List${entity}Service;
import $package.presentation.dto.$EntityRequest;
import $package.presentation.dto.$EntityResponse;
import $package.presentation.dto.PageResponse;
import org.springframework.data.domain.Pageable;

@RestController$controller_annotations_block
@RequestMapping("$base_path")
public class ${entity}Controller {

    private final Create${entity}Service createService;
    private final Get${entity}Service getService;
    private final Update${entity}Service updateService;
    private final Delete${entity}Service deleteService;
    private final List${entity}Service listService;

    $controller_constructor

    @PostMapping
    public ResponseEntity<$EntityResponse> create(@RequestBody @Valid $EntityRequest request) {
        $EntityResponse created = createService.create(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .header("Location", "$base_path/" + created.$id_name())
                .body(created);
    }

    @GetMapping("/{${id_name_lower}}")
    public ResponseEntity<$EntityResponse> get(@PathVariable $id_type ${id_name_lower}) {
        return ResponseEntity.ok(getService.get(${id_name_lower}));
    }

    @PutMapping("/{${id_name_lower}}")
    public ResponseEntity<$EntityResponse> update(@PathVariable $id_type ${id_name_lower},
                                                @RequestBody @Valid $EntityRequest request) {
        return ResponseEntity.ok(updateService.update(${id_name_lower}, request));
    }

    @DeleteMapping("/{${id_name_lower}}")
    public ResponseEntity<Void> delete(@PathVariable $id_type ${id_name_lower}) {
        deleteService.delete(${id_name_lower});
        return ResponseEntity.noContent().build();
    }

    @GetMapping
    public ResponseEntity<PageResponse<$EntityResponse>> list(Pageable pageable) {
        return ResponseEntity.ok(listService.list(pageable.getPageNumber(), pageable.getPageSize()));
    }
}
