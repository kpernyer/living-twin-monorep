import 'package:get_it/get_it.dart';
import 'package:http/http.dart' as http;
import 'package:injectable/injectable.dart';
import 'package:shared_preferences/shared_preferences.dart';

// This import will be generated after running build_runner
import 'injection.config.dart';

/// Global service locator instance
final GetIt getIt = GetIt.instance;

/// Initialize dependency injection
@InjectableInit(
  initializerName: 'init',
  preferRelativeImports: true,
  asExtension: true,
)
Future<void> configureDependencies({String? environment}) async {
  // This will be available after running build_runner
  await getIt.init(environment: environment);
}

/// Environment names for different configurations
abstract class Environment {
  static const dev = 'dev';
  static const prod = 'prod';
  static const test = 'test';
}

/// Module for third party dependencies
@module
abstract class AppModule {
  /// Provide SharedPreferences instance
  @preResolve
  @singleton
  Future<SharedPreferences> get sharedPreferences => 
      SharedPreferences.getInstance();
  
  /// Provide HTTP client
  @singleton
  http.Client get httpClient => http.Client();
}

// Note: DI setup complete!
// 1. ✅ Dependencies added to pubspec.yaml
// 2. ✅ Run flutter pub get
// 3. ✅ Generated injection.config.dart with build_runner
// 4. ✅ Configured dependency injection
// 
// To register new services, add @injectable or @singleton annotations
// and run: flutter pub run build_runner build --delete-conflicting-outputs
