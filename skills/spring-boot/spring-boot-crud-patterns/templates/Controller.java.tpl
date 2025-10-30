package $package.presentation.rest;

$lombok_common_imports
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;

import $package.application.service.Create${entity}Service;
import $package.application.service.Get${entity}Service;
import $package.application.service.Update${entity}Service;
import $package.application.service.Delete${entity}Service;
import $package.application.service.List${entity}Service;
import $package.presentation.dto.$dto_request;
import $package.presentation.dto.$dto_response;

@RestController$controller_annotations_block
@RequestMapping("$base_path")
public class ${entity}Controller {

    private final Create${entity}Service createService;
    private final Get${entity}Service getService;
    private final Update${entity}Service updateService;
    private final Delete${entity}Service deleteService;
    private final List${entity}Service listService;

    public ${entity}Controller(Create${entity}Service createService,
                               Get${entity}Service getService,
                               Update${entity}Service updateService,
                               Delete${entity}Service deleteService,
                               List${entity}Service listService) {
        this.createService = createService;
        this.getService = getService;
        this.updateService = updateService;
        this.deleteService = deleteService;
        this.listService = listService;
    }

    @PostMapping
    public ResponseEntity<$dto_response> create(@RequestBody @Valid $dto_request request) {
        return ResponseEntity.status(201).body(createService.create(request));
    }

    @GetMapping("/{${id_name_lower}}")
    public ResponseEntity<$dto_response> get(@PathVariable $id_type ${id_name_lower}) {
        return ResponseEntity.ok(getService.get(${id_name_lower}));
    }

    @PutMapping("/{${id_name_lower}}")
    public ResponseEntity<$dto_response> update(@PathVariable $id_type ${id_name_lower},
                                                @RequestBody @Valid $dto_request request) {
        return ResponseEntity.ok(updateService.update(${id_name_lower}, request));
    }

    @DeleteMapping("/{${id_name_lower}}")
    public ResponseEntity<Void> delete(@PathVariable $id_type ${id_name_lower}) {
        deleteService.delete(${id_name_lower});
        return ResponseEntity.noContent().build();
    }

    @GetMapping
    public ResponseEntity<java.util.List<$dto_response>> list(@RequestParam(defaultValue = "0") int page,
                                                               @RequestParam(defaultValue = "20") int size) {
        return ResponseEntity.ok(listService.list(page, size));
    }
}
