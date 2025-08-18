import 'package:flutter/material.dart';

/// Mixin to handle loading states in StatefulWidgets
mixin LoadingMixin<T extends StatefulWidget> on State<T> {
  bool _isLoading = false;
  
  /// Get the current loading state
  bool get isLoading => _isLoading;
  
  /// Set the loading state
  @protected
  void setLoading(bool value) {
    if (mounted) {
      setState(() => _isLoading = value);
    }
  }
  
  /// Run an async operation with loading state management
  @protected
  Future<void> runWithLoading(Future<void> Function() operation) async {
    setLoading(true);
    try {
      await operation();
    } finally {
      setLoading(false);
    }
  }
  
  /// Run an async operation with loading state and error handling
  @protected
  Future<T?> runWithLoadingAndResult<T>(Future<T> Function() operation) async {
    setLoading(true);
    try {
      final result = await operation();
      return result;
    } finally {
      setLoading(false);
    }
  }
  
  /// Build a widget that shows loading indicator when loading
  Widget buildWithLoading({
    required Widget child,
    Widget? loadingWidget,
    bool showChildWhileLoading = false,
  }) {
    if (isLoading && !showChildWhileLoading) {
      return loadingWidget ?? const Center(child: CircularProgressIndicator());
    }
    
    if (isLoading && showChildWhileLoading) {
      return Stack(
        children: [
          child,
          Positioned.fill(
            child: ColoredBox(
              color: Colors.black.withOpacity(0.3),
              child: loadingWidget ?? const Center(child: CircularProgressIndicator()),
            ),
          ),
        ],
      );
    }
    
    return child;
  }
  
  /// Show loading overlay on top of current content
  Widget withLoadingOverlay({
    required Widget child,
    Color? overlayColor,
    Widget? loadingIndicator,
  }) {
    return Stack(
      children: [
        child,
        if (isLoading)
          Positioned.fill(
            child: ColoredBox(
              color: overlayColor ?? Colors.black.withOpacity(0.5),
              child: Center(
                child: loadingIndicator ?? 
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const CircularProgressIndicator(),
                  ),
              ),
            ),
          ),
      ],
    );
  }
}

/// Extended loading mixin with multiple loading states
mixin MultiLoadingMixin<T extends StatefulWidget> on State<T> {
  final Map<String, bool> _loadingStates = {};
  
  /// Check if a specific operation is loading
  bool isLoading(String key) => _loadingStates[key] ?? false;
  
  /// Check if any operation is loading
  bool get isAnyLoading => _loadingStates.values.any((loading) => loading);
  
  /// Check if all operations are loading
  bool get isAllLoading => 
      _loadingStates.isNotEmpty && 
      _loadingStates.values.every((loading) => loading);
  
  /// Set loading state for a specific operation
  @protected
  void setLoading(String key, bool value) {
    if (mounted) {
      setState(() => _loadingStates[key] = value);
    }
  }
  
  /// Clear a loading state
  @protected
  void clearLoading(String key) {
    if (mounted) {
      setState(() => _loadingStates.remove(key));
    }
  }
  
  /// Clear all loading states
  @protected
  void clearAllLoading() {
    if (mounted) {
      setState(_loadingStates.clear);
    }
  }
  
  /// Run an operation with loading state for a specific key
  @protected
  Future<void> runWithLoading(
    String key,
    Future<void> Function() operation,
  ) async {
    setLoading(key, true);
    try {
      await operation();
    } finally {
      setLoading(key, false);
    }
  }
  
  /// Run an operation and get result with loading state
  @protected
  Future<T?> runWithLoadingAndResult<T>(
    String key,
    Future<T> Function() operation,
  ) async {
    setLoading(key, true);
    try {
      final result = await operation();
      return result;
    } finally {
      setLoading(key, false);
    }
  }
}
