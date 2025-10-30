package $package.application.service;

$lombok_common_imports
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import $package.domain.service.${entity}Service;
import $package.application.exception.${entity}NotFoundException;

@Service$service_annotations_block
@Transactional
public class Delete${entity}Service {

    private final ${entity}Service ${entity_lower}Service;

    $delete_constructor

    public void delete($id_type $id_name) {
        if (!${entity_lower}Service.existsById($id_name)) {
            throw new ${entity}NotFoundException($id_name);
        }
        ${entity_lower}Service.deleteById($id_name);
    }
}
