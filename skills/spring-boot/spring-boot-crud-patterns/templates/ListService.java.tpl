package $package.application.service;

$lombok_common_imports
import java.util.stream.Collectors;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import $package.domain.repository.${entity}Repository;
import $package.presentation.dto.$dto_response;

@Service$service_annotations_block
@Transactional(readOnly = true)
public class List${entity}Service {

    private final ${entity}Repository repository;

    public List${entity}Service(${entity}Repository repository) {
        this.repository = repository;
    }

    public java.util.List<$dto_response> list(int page, int size) {
        return repository.findAll(page, size)
            .stream()
            .map(a -> new $dto_response($list_map_response_args))
            .collect(java.util.stream.Collectors.toList());
    }
}
