/// Sealed class for type-safe API results
/// Replaces Map<String, dynamic> returns from API calls
sealed class ApiResult<T> {
  const ApiResult();
  
  /// Transform the success value
  ApiResult<U> map<U>(U Function(T) transform) {
    return switch (this) {
      ApiSuccess(:final data, :final metadata) => ApiSuccess(
          data: transform(data),
          metadata: metadata,
        ),
      ApiError() => ApiError(
          message: (this as ApiError).message,
          statusCode: (this as ApiError).statusCode,
          type: (this as ApiError).type,
          details: (this as ApiError).details,
        ),
      ApiLoading() => ApiLoading<U>(),
    };
  }
  
  /// Get the value or return a default
  T getOrElse(T defaultValue) {
    return switch (this) {
      ApiSuccess(:final data) => data,
      _ => defaultValue,
    };
  }
  
  /// Get the value or null
  T? getOrNull() {
    return switch (this) {
      ApiSuccess(:final data) => data,
      _ => null,
    };
  }
  
  /// Execute functions based on the result type
  R fold<R>({
    required R Function(T data) onSuccess,
    required R Function(String message, ApiErrorType type) onError,
    R Function()? onLoading,
  }) {
    return switch (this) {
      ApiSuccess(:final data) => onSuccess(data),
      ApiError(:final message, :final type) => onError(message, type),
      ApiLoading() => onLoading?.call() ?? onError('Loading...', ApiErrorType.unknown),
    };
  }
}

/// Successful API response
class ApiSuccess<T> extends ApiResult<T> {
  final T data;
  final Map<String, dynamic>? metadata;
  
  const ApiSuccess({
    required this.data,
    this.metadata,
  });
}

/// API error response
class ApiError<T> extends ApiResult<T> {
  final String message;
  final int? statusCode;
  final ApiErrorType type;
  final Map<String, dynamic>? details;
  
  const ApiError({
    required this.message,
    this.statusCode,
    required this.type,
    this.details,
  });
  
  /// Create error from status code
  factory ApiError.fromStatusCode(int statusCode) {
    final (message, type) = switch (statusCode) {
      400 => ('Bad request', ApiErrorType.badRequest),
      401 => ('Unauthorized', ApiErrorType.unauthorized),
      403 => ('Forbidden', ApiErrorType.forbidden),
      404 => ('Not found', ApiErrorType.notFound),
      408 => ('Request timeout', ApiErrorType.timeout),
      429 => ('Too many requests', ApiErrorType.rateLimited),
      500 => ('Internal server error', ApiErrorType.serverError),
      502 => ('Bad gateway', ApiErrorType.serverError),
      503 => ('Service unavailable', ApiErrorType.serverError),
      _ => ('Unknown error', ApiErrorType.unknown),
    };
    
    return ApiError(
      message: message,
      statusCode: statusCode,
      type: type,
    );
  }
  
  /// Create network error
  factory ApiError.network([String? message]) {
    return ApiError(
      message: message ?? 'No internet connection',
      type: ApiErrorType.network,
    );
  }
  
  /// Create timeout error
  factory ApiError.timeout([Duration? duration]) {
    return ApiError(
      message: duration != null 
        ? 'Request timed out after ${duration.inSeconds} seconds'
        : 'Request timed out',
      type: ApiErrorType.timeout,
    );
  }
  
  /// Create parsing error
  factory ApiError.parsing([String? details]) {
    return ApiError(
      message: details ?? 'Failed to parse response',
      type: ApiErrorType.parseError,
    );
  }
}

/// Loading state for API calls
class ApiLoading<T> extends ApiResult<T> {
  const ApiLoading();
}

/// Types of API errors
enum ApiErrorType {
  network,
  timeout,
  unauthorized,
  forbidden,
  notFound,
  badRequest,
  rateLimited,
  serverError,
  parseError,
  cancelled,
  unknown,
}

/// Extension to convert Future to ApiResult
extension FutureToApiResult<T> on Future<T> {
  /// Convert a Future to ApiResult, catching exceptions
  Future<ApiResult<T>> toApiResult() async {
    try {
      final value = await this;
      return ApiSuccess(data: value);
    } catch (e) {
      return ApiError(
        message: e.toString(),
        type: ApiErrorType.unknown,
      );
    }
  }
}
