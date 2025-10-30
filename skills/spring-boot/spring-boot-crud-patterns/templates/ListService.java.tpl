package $package.application.service;

$lombok_common_imports
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import $package.domain.service.${entity}Service;
import $package.application.mapper.${entity}Mapper;
import $package.presentation.dto.$dto_response;
import $package.presentation.dto.PageResponse;
import java.util.List;
import java.util.stream.Collectors;

@Service$service_annotations_block
@Transactional(readOnly = true)
public class List${entity}Service {

    private final ${entity}Service ${entity_lower}Service;
    private final ${entity}Mapper mapper;

    $list_constructor

    public PageResponse<$dto_response> list(int page, int size) {
        List<$dto_response> content = ${entity_lower}Service.findAll(page, size)
            .stream()
            .map(mapper::toResponse)
            .collect(Collectors.toList());
        long total = ${entity_lower}Service.count();
        int totalPages = (int) Math.ceil(total / (double) size);
        return new PageResponse<>(content, page, size, total, totalPages);
    }
}
