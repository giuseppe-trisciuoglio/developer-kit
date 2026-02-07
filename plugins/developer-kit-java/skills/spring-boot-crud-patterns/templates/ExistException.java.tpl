package $package.application.exception;

public class ${entity}ExistException extends RuntimeException {
    public ${entity}ExistException(String message) {
        super(message);
    }
    public ${entity}ExistException($id_type $id_name) {
        super("$entity already exists: " + $id_name);
    }
}
