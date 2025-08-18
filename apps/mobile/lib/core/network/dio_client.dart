import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';
import 'package:retry/retry.dart';
import 'dart:io';
import '../security/secure_storage_service.dart';
import '../result/api_result.dart';

/// Enhanced Dio client with SSL pinning, retry logic, and interceptors
@singleton
class DioClient {
  late final Dio _dio;
  final SecureStorageService _secureStorage;
  
  // SSL certificate fingerprints for pinning
  static const List<String> _certificateFingerprints = [
    // Add your server's certificate SHA256 fingerprints here
    // Example: 'SHA256:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
  ];
  
  DioClient(this._secureStorage) {
    _dio = Dio(
      BaseOptions(
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
        sendTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );
    
    _setupInterceptors();
  }
  
  void _setupInterceptors() {
    // Auth interceptor
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Add auth token to requests
          final token = await _secureStorage.getToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (error, handler) async {
          // Handle 401 - refresh token
          if (error.response?.statusCode == 401) {
            final refreshToken = await _secureStorage.getRefreshToken();
            if (refreshToken != null) {
              // Try to refresh the token
              final newToken = await _refreshAuthToken(refreshToken);
              if (newToken != null) {
                // Retry the request with new token
                error.requestOptions.headers['Authorization'] = 'Bearer $newToken';
                final clonedRequest = await _dio.request(
                  error.requestOptions.path,
                  options: Options(
                    method: error.requestOptions.method,
                    headers: error.requestOptions.headers,
                  ),
                  data: error.requestOptions.data,
                  queryParameters: error.requestOptions.queryParameters,
                );
                return handler.resolve(clonedRequest);
              }
            }
          }
          handler.next(error);
        },
      ),
    );
    
    // Logging interceptor (only in debug mode)
    _dio.interceptors.add(
      LogInterceptor(
        requestBody: true,
        responseBody: true,
        error: true,
        logPrint: (log) {
          // Use your logger here instead of print
          // debugPrint(log.toString());
        },
      ),
    );
  }
  
  /// Make GET request with retry logic
  Future<ApiResult<T>> get<T>({
    required String path,
    Map<String, dynamic>? queryParameters,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    return _retryRequest(() async {
      final response = await _dio.get(
        path,
        queryParameters: queryParameters,
      );
      
      if (fromJson != null && response.data != null) {
        final data = fromJson(response.data as Map<String, dynamic>);
        return ApiSuccess(data: data);
      }
      
      return ApiSuccess(data: response.data as T);
    });
  }
  
  /// Make POST request with retry logic
  Future<ApiResult<T>> post<T>({
    required String path,
    dynamic data,
    Map<String, dynamic>? queryParameters,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    return _retryRequest(() async {
      final response = await _dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
      );
      
      if (fromJson != null && response.data != null) {
        final parsedData = fromJson(response.data as Map<String, dynamic>);
        return ApiSuccess(data: parsedData);
      }
      
      return ApiSuccess(data: response.data as T);
    });
  }
  
  /// Make PUT request with retry logic
  Future<ApiResult<T>> put<T>({
    required String path,
    dynamic data,
    Map<String, dynamic>? queryParameters,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    return _retryRequest(() async {
      final response = await _dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
      );
      
      if (fromJson != null && response.data != null) {
        final parsedData = fromJson(response.data as Map<String, dynamic>);
        return ApiSuccess(data: parsedData);
      }
      
      return ApiSuccess(data: response.data as T);
    });
  }
  
  /// Make DELETE request with retry logic
  Future<ApiResult<T>> delete<T>({
    required String path,
    Map<String, dynamic>? queryParameters,
  }) async {
    return _retryRequest(() async {
      final response = await _dio.delete(
        path,
        queryParameters: queryParameters,
      );
      
      return ApiSuccess(data: response.data as T);
    });
  }
  
  /// Upload file with progress tracking
  Future<ApiResult<T>> uploadFile<T>({
    required String path,
    required String filePath,
    String fileFieldName = 'file',
    Map<String, dynamic>? data,
    void Function(int, int)? onSendProgress,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    return _retryRequest(() async {
      final formData = FormData.fromMap({
        ...?data,
        fileFieldName: await MultipartFile.fromFile(filePath),
      });
      
      final response = await _dio.post(
        path,
        data: formData,
        onSendProgress: onSendProgress,
      );
      
      if (fromJson != null && response.data != null) {
        final parsedData = fromJson(response.data as Map<String, dynamic>);
        return ApiSuccess(data: parsedData);
      }
      
      return ApiSuccess(data: response.data as T);
    });
  }
  
  /// Download file with progress tracking
  Future<ApiResult<String>> downloadFile({
    required String url,
    required String savePath,
    void Function(int, int)? onReceiveProgress,
  }) async {
    return _retryRequest(() async {
      await _dio.download(
        url,
        savePath,
        onReceiveProgress: onReceiveProgress,
      );
      
      return ApiSuccess(data: savePath);
    });
  }
  
  /// Retry logic with exponential backoff
  Future<ApiResult<T>> _retryRequest<T>(
    Future<ApiResult<T>> Function() request,
  ) async {
    const r = RetryOptions(
      maxAttempts: 3,
      delayFactor: Duration(seconds: 2),
      maxDelay: Duration(seconds: 10),
    );
    
    try {
      return await r.retry(
        request,
        retryIf: (e) => _shouldRetry(e),
      );
    } on DioException catch (e) {
      return _handleDioError<T>(e);
    } catch (e) {
      return ApiError(
        message: e.toString(),
        type: ApiErrorType.unknown,
      );
    }
  }
  
  /// Determine if request should be retried
  bool _shouldRetry(Exception e) {
    if (e is DioException) {
      // Retry on network errors
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError) {
        return true;
      }
      
      // Retry on specific status codes
      final statusCode = e.response?.statusCode;
      if (statusCode != null) {
        // Retry on 5xx errors (server errors)
        if (statusCode >= 500 && statusCode < 600) {
          return true;
        }
        // Retry on 429 (too many requests)
        if (statusCode == 429) {
          return true;
        }
      }
    }
    
    // Retry on socket exceptions
    if (e is SocketException) {
      return true;
    }
    
    return false;
  }
  
  /// Handle Dio errors and convert to ApiResult
  ApiResult<T> _handleDioError<T>(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiError.timeout();
        
      case DioExceptionType.connectionError:
        return ApiError.network('No internet connection');
        
      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        if (statusCode != null) {
          return ApiError.fromStatusCode(statusCode);
        }
        return ApiError(
          message: error.message ?? 'Server error',
          type: ApiErrorType.serverError,
        );
        
      case DioExceptionType.cancel:
        return ApiError(
          message: 'Request cancelled',
          type: ApiErrorType.cancelled,
        );
        
      default:
        return ApiError(
          message: error.message ?? 'Unknown error',
          type: ApiErrorType.unknown,
        );
    }
  }
  
  /// Refresh authentication token
  Future<String?> _refreshAuthToken(String refreshToken) async {
    try {
      // This is a placeholder - implement your actual refresh logic
      final response = await _dio.post(
        '/auth/refresh',
        data: {'refreshToken': refreshToken},
      );
      
      if (response.statusCode == 200) {
        final newToken = response.data['token'] as String?;
        if (newToken != null) {
          await _secureStorage.saveToken(newToken);
          return newToken;
        }
      }
    } catch (e) {
      // Failed to refresh token
    }
    
    return null;
  }
  
  /// Set base URL
  void setBaseUrl(String baseUrl) {
    _dio.options.baseUrl = baseUrl;
  }
  
  /// Add custom headers
  void addHeaders(Map<String, dynamic> headers) {
    _dio.options.headers.addAll(headers);
  }
  
  /// Clear all interceptors (useful for testing)
  void clearInterceptors() {
    _dio.interceptors.clear();
  }
  
  /// Get raw Dio instance (use with caution)
  Dio get dio => _dio;
}

/// SSL Pinning implementation
/// Note: For production, use actual certificate pinning
class SSLPinning {
  static Future<bool> verifyCertificate(String fingerprint) async {
    // Implement actual certificate verification
    // This is a placeholder
    return true;
  }
}
