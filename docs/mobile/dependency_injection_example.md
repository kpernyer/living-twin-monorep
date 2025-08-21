# Dependency Injection Implementation Example

## How to Add New Services with DI

### 1. Create a Service with DI Annotation

```dart
// lib/services/api_service_di.dart
import 'package:injectable/injectable.dart';
import 'package:http/http.dart' as http;
import '../core/result/api_result.dart';
import 'auth_service_di.dart';

@singleton
class ApiServiceDI {
  final http.Client _httpClient;
  final AuthServiceDI _authService;
  final String baseUrl;
  
  // Constructor injection - get_it will provide dependencies
  ApiServiceDI(
    this._httpClient,
    this._authService,
    @Named('baseUrl') this.baseUrl,
  );
  
  Future<ApiResult<T>> get<T>(String endpoint) async {
    try {
      final token = await _authService.getIdToken();
      final response = await _httpClient.get(
        Uri.parse('$baseUrl$endpoint'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        // Parse response
        return ApiSuccess(data: response.body as T);
      } else {
        return ApiError.fromStatusCode(response.statusCode);
      }
    } catch (e) {
      return ApiError.network(e.toString());
    }
  }
}
```

### 2. Run Build Runner

```bash
cd apps/mobile
flutter pub run build_runner build --delete-conflicting-outputs
```

### 3. Use the Service in Your Widget

```dart
// lib/features/home/home_screen.dart
import 'package:flutter/material.dart';
import '../../core/di/injection.dart';
import '../../services/api_service_di.dart';
import '../../services/auth_service_di.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  // Get services from DI container
  final apiService = getIt<ApiServiceDI>();
  final authService = getIt<AuthServiceDI>();
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Home'),
      ),
      body: Center(
        child: Column(
          children: [
            Text('User: ${authService.currentUser?['email'] ?? 'Not logged in'}'),
            ElevatedButton(
              onPressed: () async {
                final result = await apiService.get<Map<String, dynamic>>('/user/profile');
                result.fold(
                  onSuccess: (data) {
                    // Handle success
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Profile loaded')),
                    );
                  },
                  onError: (message, type) {
                    // Handle error
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Error: $message')),
                    );
                  },
                );
              },
              child: const Text('Load Profile'),
            ),
          ],
        ),
      ),
    );
  }
}
```

## Example: AuthService with DI (Already Created)

The `AuthServiceDI` demonstrates:
- ✅ `@singleton` annotation for single instance
- ✅ Constructor injection of `SharedPreferences`
- ✅ Type-safe returns using `AuthResult` sealed class
- ✅ Integration with `Organization` freezed model

```dart
@singleton
class AuthServiceDI {
  final SharedPreferences _prefs;
  
  AuthServiceDI(this._prefs) {
    _loadStoredAuth();
  }
  
  Future<AuthResult> signInWithEmailAndPassword({
    required String email,
    required String password,
  }) async {
    // Returns type-safe AuthSuccess or AuthFailure
  }
}
```

## Initialize DI in main.dart

```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'core/di/injection.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize dependency injection
  await configureDependencies();
  
  runApp(const LivingTwinApp());
}
```

## Available DI Annotations

| Annotation | Purpose | Scope |
|------------|---------|-------|
| `@singleton` | Single instance for entire app lifetime | Global |
| `@lazySingleton` | Single instance created on first use | Global |
| `@injectable` | New instance per injection | Transient |
| `@factoryMethod` | Custom factory for creating instances | Custom |
| `@module` | Group third-party dependencies | Module |
| `@Named('key')` | Named parameters for configuration | Parameter |

## Common Patterns

### 1. Environment-Specific Configuration

```dart
@module
abstract class AppModule {
  @Named('baseUrl')
  @dev
  String get devUrl => 'http://localhost:8000';
  
  @Named('baseUrl')
  @prod
  String get prodUrl => 'https://api.livingtwin.com';
}

// Initialize with environment
await configureDependencies(environment: Environment.dev);
```

### 2. Repository Pattern with DI

```dart
@injectable
class UserRepository {
  final ApiServiceDI _api;
  
  UserRepository(this._api);
  
  Future<ApiResult<User>> getUser(String id) async {
    final result = await _api.get<Map<String, dynamic>>('/users/$id');
    return result.map((data) => User.fromJson(data));
  }
}
```

### 3. Testing with Mock Dependencies

```dart
// In tests
getIt.registerSingleton<AuthServiceDI>(MockAuthService());
getIt.registerSingleton<ApiServiceDI>(MockApiService());
```

## Benefits of Using DI

1. **Testability** - Easy to mock dependencies
2. **Decoupling** - Classes don't create their dependencies
3. **Configuration** - Centralized dependency setup
4. **Lifecycle Management** - Automatic singleton handling
5. **Type Safety** -
