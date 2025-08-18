import 'package:flutter/material.dart';

/// Extension methods for BuildContext to provide convenient access to theme and navigation
extension ContextX on BuildContext {
  /// Quick access to Theme
  ThemeData get theme => Theme.of(this);
  
  /// Quick access to TextTheme
  TextTheme get textTheme => theme.textTheme;
  
  /// Quick access to ColorScheme
  ColorScheme get colors => theme.colorScheme;
  
  /// Quick access to screen width
  double get screenWidth => MediaQuery.of(this).size.width;
  
  /// Quick access to screen height
  double get screenHeight => MediaQuery.of(this).size.height;
  
  /// Quick access to screen size
  Size get screenSize => MediaQuery.of(this).size;
  
  /// Quick access to view insets (keyboard height, etc.)
  EdgeInsets get viewInsets => MediaQuery.of(this).viewInsets;
  
  /// Quick access to padding (safe areas)
  EdgeInsets get padding => MediaQuery.of(this).padding;
  
  /// Quick access to device pixel ratio
  double get devicePixelRatio => MediaQuery.of(this).devicePixelRatio;
  
  /// Quick access to platform brightness
  Brightness get platformBrightness => MediaQuery.of(this).platformBrightness;
  
  /// Check if dark mode is enabled
  bool get isDarkMode => platformBrightness == Brightness.dark;
  
  /// Check if keyboard is visible
  bool get isKeyboardVisible => viewInsets.bottom > 0;
  
  /// Check if device is in landscape mode
  bool get isLandscape => screenWidth > screenHeight;
  
  /// Check if device is in portrait mode
  bool get isPortrait => screenHeight > screenWidth;
  
  /// Check if device is a tablet (width > 600)
  bool get isTablet => screenWidth > 600;
  
  /// Check if device is a phone
  bool get isPhone => screenWidth <= 600;
  
  /// Show a SnackBar with a message
  void showSnackBar(
    String message, {
    Duration duration = const Duration(seconds: 3),
    SnackBarAction? action,
    Color? backgroundColor,
    Color? textColor,
  }) {
    ScaffoldMessenger.of(this).showSnackBar(
      SnackBar(
        content: Text(
          message,
          style: TextStyle(color: textColor),
        ),
        duration: duration,
        action: action,
        backgroundColor: backgroundColor,
      ),
    );
  }
  
  /// Show an error SnackBar
  void showErrorSnackBar(String message) {
    showSnackBar(
      message,
      backgroundColor: Colors.red.shade700,
      textColor: Colors.white,
    );
  }
  
  /// Show a success SnackBar
  void showSuccessSnackBar(String message) {
    showSnackBar(
      message,
      backgroundColor: Colors.green.shade700,
      textColor: Colors.white,
    );
  }
  
  /// Show a loading dialog
  Future<void> showLoadingDialog({String? message}) async {
    showDialog(
      context: this,
      barrierDismissible: false,
      builder: (context) => PopScope(
        canPop: false,
        child: AlertDialog(
          content: Row(
            children: [
              const CircularProgressIndicator(),
              const SizedBox(width: 16),
              Expanded(
                child: Text(message ?? 'Loading...'),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  /// Hide the loading dialog
  void hideLoadingDialog() {
    if (Navigator.canPop(this)) {
      Navigator.pop(this);
    }
  }
  
  /// Show a confirmation dialog
  Future<bool> showConfirmDialog({
    required String title,
    required String message,
    String confirmText = 'Confirm',
    String cancelText = 'Cancel',
    Color? confirmColor,
  }) async {
    final result = await showDialog<bool>(
      context: this,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(cancelText),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: confirmColor != null
                ? TextButton.styleFrom(foregroundColor: confirmColor)
                : null,
            child: Text(confirmText),
          ),
        ],
      ),
    );
    
    return result ?? false;
  }
  
  /// Navigate to a new page
  Future<T?> push<T>(Widget page) {
    return Navigator.push<T>(
      this,
      MaterialPageRoute<T>(builder: (_) => page),
    );
  }
  
  /// Navigate to a new page and remove all previous routes
  Future<T?> pushReplacement<T>(Widget page) {
    return Navigator.pushReplacement<T, void>(
      this,
      MaterialPageRoute<T>(builder: (_) => page),
    );
  }
  
  /// Navigate to a new page and remove all previous routes
  Future<T?> pushAndRemoveUntil<T>(
    Widget page,
    bool Function(Route<dynamic>) predicate,
  ) {
    return Navigator.pushAndRemoveUntil<T>(
      this,
      MaterialPageRoute<T>(builder: (_) => page),
      predicate,
    );
  }
  
  /// Pop the current route
  void pop<T>([T? result]) {
    Navigator.pop(this, result);
  }
  
  /// Pop until a specific route
  void popUntil(bool Function(Route<dynamic>) predicate) {
    Navigator.popUntil(this, predicate);
  }
  
  /// Check if can pop
  bool get canPop => Navigator.canPop(this);
  
  /// Focus scope shortcuts
  void unfocus() {
    FocusScope.of(this).unfocus();
  }
  
  /// Request focus for a specific node
  void requestFocus(FocusNode node) {
    FocusScope.of(this).requestFocus(node);
  }
  
  /// Hide keyboard
  void hideKeyboard() {
    unfocus();
  }
  
  /// Get responsive value based on screen size
  T responsive<T>({
    required T mobile,
    T? tablet,
    T? desktop,
  }) {
    if (screenWidth >= 1200 && desktop != null) {
      return desktop;
    } else if (screenWidth >= 600 && tablet != null) {
      return tablet;
    }
    return mobile;
  }
  
  /// Get text style with responsive font size
  TextStyle responsiveTextStyle({
    required TextStyle baseStyle,
    double? tabletScale,
    double? desktopScale,
  }) {
    final scale = responsive<double>(
      mobile: 1.0,
      tablet: tabletScale ?? 1.1,
      desktop: desktopScale ?? 1.2,
    );
    
    return baseStyle.copyWith(
      fontSize: (baseStyle.fontSize ?? 14) * scale,
    );
  }
  
  /// Get responsive padding
  EdgeInsets responsivePadding({
    EdgeInsets mobile = const EdgeInsets.all(16),
    EdgeInsets? tablet,
    EdgeInsets? desktop,
  }) {
    return responsive(
      mobile: mobile,
      tablet: tablet ?? const EdgeInsets.all(24),
      desktop: desktop ?? const EdgeInsets.all(32),
    );
  }
  
  /// Show a bottom sheet
  Future<T?> showBottomSheet<T>({
    required Widget Function(BuildContext) builder,
    bool isDismissible = true,
    bool enableDrag = true,
    bool isScrollControlled = false,
    Color? backgroundColor,
  }) {
    return showModalBottomSheet<T>(
      context: this,
      builder: builder,
      isDismissible: isDismissible,
      enableDrag: enableDrag,
      isScrollControlled: isScrollControlled,
      backgroundColor: backgroundColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
    );
  }
}
