package $package.presentation.dto;

public record PageResponse<T>(
    java.util.List<T> content,
    int page,
    int size,
    long totalElements,
    int totalPages
) { }
