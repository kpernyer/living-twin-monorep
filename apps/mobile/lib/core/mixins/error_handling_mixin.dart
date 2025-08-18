import 'package:flutter/material.dart';
import '../extensions/context_extensions.dart';

/// Mixin to handle error states and display in StatefulWidgets
mixin ErrorHandlingMixin<T extends StatefulWidget> on State<T> {
  String? _errorMessage;
  Object? _lastError;
  StackTrace? _lastStackTrace;
  
  /// Get the current error message
  String? get errorMessage => _errorMessage;
  
  /// Check if there's an error
  bool get hasError => _errorMessage != null;
  
  /// Get the last error object
  Object? get lastError => _lastError;
  
  /// Get the last stack trace
  StackTrace? get lastStackTrace => _lastStackTrace;
  
  /// Set an error message
  @protected
  void setError(String message, [Object? error, StackTrace? stackTrace]) {
    if (mounted) {
      setState(() {
        _errorMessage = message;
        _lastError = error;
        _lastStackTrace = stackTrace;
      });
    }
  }
  
  /// Clear the error state
  @protected
  void clearError() {
    if (mounted) {
      setState(() {
        _errorMessage = null;
        _lastError = null;
        _lastStackTrace = null;
      });
    }
  }
  
  /// Show error as a SnackBar
  @protected
  void showError(String message, {bool clearAfter = true}) {
    if (mounted) {
      context.showErrorSnackBar(message);
      if (clearAfter) {
        clearError();
      } else {
        setError(message);
      }
    }
  }
  
  /// Show error as a dialog
  @protected
  Future<void> showErrorDialog(String message, {String? title}) async {
    if (mounted) {
      await showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: Text(title ?? 'Error'),
          content: Text(message),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    }
  }
  
  /// Run an operation with error handling
  @protected
  Future<void> runWithErrorHandling(
    Future<void> Function() operation, {
    String? errorMessage,
    bool showSnackBar = true,
  }) async {
    clearError();
    try {
      await operation();
    } catch (e, stackTrace) {
      final message = errorMessage ?? e.toString();
      setError(message, e, stackTrace);
      
      if (showSnackBar) {
        showError(message, clearAfter: false);
      }
    }
  }
  
  /// Run an operation and return result with error handling
  @protected
  Future<T?> runWithErrorHandlingAndResult<T>(
    Future<T> Function() operation, {
    String? errorMessage,
    bool showSnackBar = true,
    T? defaultValue,
  }) async {
    clearError();
    try {
      final result = await operation();
      return result;
    } catch (e, stackTrace) {
      final message = errorMessage ?? e.toString();
      setError(message, e, stackTrace);
      
      if (showSnackBar) {
        showError(message, clearAfter: false);
      }
      
      return defaultValue;
    }
  }
  
  /// Build a widget that shows error state
  Widget buildWithError({
    required Widget child,
    Widget? errorWidget,
    bool showChildOnError = false,
  }) {
    if (hasError && !showChildOnError) {
      return errorWidget ?? _buildDefaultErrorWidget();
    }
    
    if (hasError && showChildOnError) {
      return Column(
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            color: Colors.red.shade100,
            child: Row(
              children: [
                Icon(Icons.error, color: Colors.red.shade700),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    errorMessage!,
                    style: TextStyle(color: Colors.red.shade700),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: clearError,
                  color: Colors.red.shade700,
                ),
              ],
            ),
          ),
          Expanded(child: child),
        ],
      );
    }
    
    return child;
  }
  
  /// Build default error widget
  Widget _buildDefaultErrorWidget() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red.shade300,
            ),
            const SizedBox(height: 16),
            Text(
              'Something went wrong',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              errorMessage ?? 'An unexpected error occurred',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey.shade600,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: clearError,
              icon: const Icon(Icons.refresh),
              label: const Text('Try Again'),
            ),
          ],
        ),
      ),
    );
  }
}

/// Extended error handling mixin with categorized errors
mixin CategorizedErrorMixin<T extends StatefulWidget> on State<T> {
  final Map<String, String> _errors = {};
  final Map<String, Object> _errorObjects = {};
  
  /// Check if a specific field has an error
  bool hasError(String field) => _errors.containsKey(field);
  
  /// Get error message for a specific field
  String? getError(String field) => _errors[field];
  
  /// Check if any field has an error
  bool get hasAnyError => _errors.isNotEmpty;
  
  /// Get all errors
  Map<String, String> get allErrors => Map.unmodifiable(_errors);
  
  /// Set error for a specific field
  @protected
  void setFieldError(String field, String message, [Object? error]) {
    if (mounted) {
      setState(() {
        _errors[field] = message;
        if (error != null) {
          _errorObjects[field] = error;
        }
      });
    }
  }
  
  /// Clear error for a specific field
  @protected
  void clearFieldError(String field) {
    if (mounted) {
      setState(() {
        _errors.remove(field);
        _errorObjects.remove(field);
      });
    }
  }
  
  /// Clear all errors
  @protected
  void clearAllErrors() {
    if (mounted) {
      setState(() {
        _errors.clear();
        _errorObjects.clear();
      });
    }
  }
  
  /// Validate a field with a validator function
  @protected
  bool validateField(
    String field,
    String? value,
    String? Function(String?) validator,
  ) {
    final error = validator(value);
    if (error != null) {
      setFieldError(field, error);
      return false;
    } else {
      clearFieldError(field);
      return true;
    }
  }
  
  /// Validate multiple fields
  @protected
  bool validateFields(Map<String, String? Function(String?)> validators, Map<String, String?> values) {
    var isValid = true;
    
    validators.forEach((field, validator) {
      final value = values[field];
      if (!validateField(field, value, validator)) {
        isValid = false;
      }
    });
    
    return isValid;
  }
  
  /// Build a form field with error display
  Widget buildFieldWithError({
    required String field,
    required Widget child,
  }) {
    final error = getError(field);
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        child,
        if (error != null)
          Padding(
            padding: const EdgeInsets.only(top: 4, left: 12),
            child: Text(
              error,
              style: TextStyle(
                color: Theme.of(context).colorScheme.error,
                fontSize: 12,
              ),
            ),
          ),
      ],
    );
  }
}
