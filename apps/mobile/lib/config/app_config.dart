import 'package:flutter/foundation.dart';

class AppConfig {
  static const String _devApiUrl = 'http://localhost:8000';
  static const String _stagingApiUrl = 'https://api-staging.livingtwin.com';
  static const String _prodApiUrl = 'https://api.livingtwin.com';

  static String get apiUrl {
    if (kDebugMode) {
      // In debug mode, check for environment override
      const envApiUrl = String.fromEnvironment('API_URL');
      if (envApiUrl.isNotEmpty) {
        return envApiUrl;
      }
      return _devApiUrl;
    }
    
    // In release mode, use production URL
    // TODO: Add staging detection logic if needed
    return _prodApiUrl;
  }

  static String get environment {
    if (kDebugMode) {
      return 'development';
    }
    return 'production';
  }

  // Firebase configuration
  static const String firebaseProjectId = String.fromEnvironment(
    'FIREBASE_PROJECT_ID',
    defaultValue: 'living-twin-demo',
  );

  // Feature flags
  static const bool enableSpeechRecognition = true;
  static const bool enableOfflineMode = true;
  static const bool enableAnalytics = !kDebugMode;

  // App settings
  static const int maxRetryAttempts = 3;
  static const Duration requestTimeout = Duration(seconds: 30);
  static const Duration speechTimeout = Duration(seconds: 30);
  static const int maxChatHistory = 100;
}
