package $package.presentation.rest;

import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import $package.application.exception.${entity}NotFoundException;
import $package.application.exception.${entity}ExistException;
import $package.presentation.dto.ErrorResponse;

@RestControllerAdvice
public class ${entity}ExceptionHandler {

    @ExceptionHandler(${entity}NotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(${entity}NotFoundException ex, org.springframework.web.context.request.WebRequest request) {
        ErrorResponse error = new ErrorResponse(
            HttpStatus.NOT_FOUND.value(),
            "Not Found",
            ex.getMessage(),
            request.getDescription(false).replaceFirst("uri=", "")
        );
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }

    @ExceptionHandler(${entity}ExistException.class)
    public ResponseEntity<ErrorResponse> handleExist(${entity}ExistException ex, org.springframework.web.context.request.WebRequest request) {
        ErrorResponse error = new ErrorResponse(
            HttpStatus.CONFLICT.value(),
            "Conflict",
            ex.getMessage(),
            request.getDescription(false).replaceFirst("uri=", "")
        );
        return ResponseEntity.status(HttpStatus.CONFLICT).body(error);
    }
}
