package $package.application.exception;

public class ${entity}NotFoundException extends RuntimeException {
    public ${entity}NotFoundException($id_type $id_name) {
        super("$entity not found: " + $id_name);
    }
}
