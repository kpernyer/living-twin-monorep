import 'package:flutter/foundation.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

/// Sentry configuration for crash reporting
class SentryConfig {
  static const String _dsn = String.fromEnvironment(
    'SENTRY_DSN',
    defaultValue: 'https://your-glitchtip-instance.com/1',
  );
  
  static const String _environment = String.fromEnvironment(
    'SENTRY_ENVIRONMENT',
    defaultValue: 'development',
  );
  
  /// Initialize Sentry with proper configuration
  static Future<void> init() async {
    await SentryFlutter.init(
      (options) {
        // DSN configuration
        options.dsn = _dsn;
        options.environment = _environment;
        
        // Performance monitoring
        options.tracesSampleRate = 1.0;
        options.profilesSampleRate = 1.0;
        
        // Debug configuration
        options.debug = kDebugMode;
        
        // Release configuration
        options.release = 'flutter_twin@1.0.0';
        
        // Before send callback to filter sensitive data
        options.beforeSend = (event, hint) {
          // Remove sensitive data from events
          event.extra?.remove('password');
          event.extra?.remove('token');
          event.extra?.remove('api_key');
          event.extra?.remove('secret');
          
          // Filter out certain error types in development
          if (kDebugMode) {
            // Don't send certain errors in debug mode
            if (event.exception?.values.first.type == 'FlutterError') {
              return null; // Don't send Flutter errors in debug
            }
          }
          
          return event;
        };
        
        // Configure breadcrumbs
        options.beforeBreadcrumb = (breadcrumb, hint) {
          // Filter out sensitive breadcrumbs
          if (breadcrumb.message?.contains('password') == true ||
              breadcrumb.message?.contains('token') == true) {
            return null;
          }
          return breadcrumb;
        };
        
        // Enable automatic instrumentation
        options.enableAutoSessionTracking = true;
        options.attachStacktrace = true;
        
        // Configure integrations
        options.addIntegration(
          SentryHttpClientIntegration(),
        );
      },
      appRunner: () {
        // This will be called after Sentry is initialized
        // The actual app will be started by the main function
      },
    );
  }
  
  /// Set user context for better error tracking
  static void setUser({
    required String id,
    String? email,
    String? username,
    Map<String, dynamic>? extras,
  }) {
    Sentry.configureScope((scope) {
      scope.setUser(SentryUser(
        id: id,
        email: email,
        username: username,
        extras: extras,
      ));
    });
  }
  
  /// Set organization context
  static void setOrganization(String organizationId) {
    Sentry.configureScope((scope) {
      scope.setTag('organization_id', organizationId);
    });
  }
  
  /// Add custom context data
  static void setContext(String key, dynamic value) {
    Sentry.configureScope((scope) {
      scope.setContext(key, value);
    });
  }
  
  /// Add breadcrumb for debugging
  static void addBreadcrumb({
    required String message,
    String? category,
    String? type,
    Map<String, dynamic>? data,
  }) {
    Sentry.addBreadcrumb(
      Breadcrumb(
        message: message,
        category: category,
        type: type,
        data: data,
        timestamp: DateTime.now(),
      ),
    );
  }
  
  /// Manually capture an exception
  static Future<SentryId> captureException(
    dynamic exception, {
    dynamic stackTrace,
    Map<String, dynamic>? extras,
    Map<String, String>? tags,
  }) async {
    return await Sentry.captureException(
      exception,
      stackTrace: stackTrace,
      withScope: (scope) {
        if (extras != null) {
          extras.forEach((key, value) {
            scope.setExtra(key, value);
          });
        }
        if (tags != null) {
          tags.forEach((key, value) {
            scope.setTag(key, value);
          });
        }
      },
    );
  }
  
  /// Capture a message
  static Future<SentryId> captureMessage(
    String message, {
    SentryLevel level = SentryLevel.info,
    Map<String, dynamic>? extras,
    Map<String, String>? tags,
  }) async {
    return await Sentry.captureMessage(
      message,
      level: level,
      withScope: (scope) {
        if (extras != null) {
          extras.forEach((key, value) {
            scope.setExtra(key, value);
          });
        }
        if (tags != null) {
          tags.forEach((key, value) {
            scope.setTag(key, value);
          });
        }
      },
    );
  }
  
  /// Close Sentry
  static Future<void> close() async {
    await Sentry.close();
  }
}
