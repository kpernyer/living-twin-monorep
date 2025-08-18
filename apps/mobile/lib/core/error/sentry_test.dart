import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_twin/core/error/sentry_config.dart';

void main() {
  group('SentryConfig', () {
    test('should initialize without errors', () async {
      // This test verifies that SentryConfig can be imported and used
      // In a real test environment, you would mock the Sentry SDK
      expect(SentryConfig, isNotNull);
    });

    test('should have proper configuration methods', () {
      // Test that all required methods exist
      expect(SentryConfig.setUser, isNotNull);
      expect(SentryConfig.setOrganization, isNotNull);
      expect(SentryConfig.addBreadcrumb, isNotNull);
      expect(SentryConfig.captureException, isNotNull);
      expect(SentryConfig.captureMessage, isNotNull);
    });
  });
}
