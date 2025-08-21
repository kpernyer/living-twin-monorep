# Dart/Flutter Code Migration Guide

## Overview
After applying stricter linter rules, we found **482 issues** in the codebase. This guide helps you systematically address them to leverage Dart's language benefits.

## Issue Categories & Solutions

### 🔴 Critical Errors (Must Fix First)

#### 1. **Type Safety Violations** (~50 errors)
```dart
// ❌ Before: Dynamic types causing errors
final response = await api.get('/data');
if (response['success']) { // Error: non_bool_condition

// ✅ After: Proper typing
final Map<String, dynamic> response = await api.get('/data');
if (response['success'] == true) {
```

#### 2. **Non-Bool Conditions**
```dart
// ❌ Before
if (authService.isAuthenticated) { // When isAuthenticated returns dynamic

// ✅ After
if (authService.isAuthenticated == true) {
// Or better: ensure isAuthenticated returns bool
```

#### 3. **Argument Type Mismatches**
```dart
// ❌ Before
_showError(response['error']); // error is dynamic

// ✅ After
_showError(response['error']?.toString() ?? 'Unknown error');
```

### 🟡 Warnings (Important)

#### 1. **Inference Failures**
```dart
// ❌ Before
Navigator.push(context, MaterialPageRoute(
  builder: (context) => HomeScreen(),
));

// ✅ After
Navigator.push<void>(context, MaterialPageRoute<void>(
  builder: (context) => const HomeScreen(),
));
```

#### 2. **Unused Imports**
Remove all unused imports flagged by the analyzer.

### 🔵 Info (Best Practices)

#### 1. **Missing await**
```dart
// ❌ Before
_localStorage.saveData(data); // Missing await

// ✅ After
await _localStorage.saveData(data);
// Or if intentionally fire-and-forget:
unawaited(_localStorage.saveData(data)); // import 'dart:async';
```

#### 2. **Catch Without Type**
```dart
// ❌ Before
try {
  await api.call();
} catch (e) {
  print(e);
}

// ✅ After
try {
  await api.call();
} on SocketException catch (e) {
  debugPrint('Network error: $e');
} on TimeoutException catch (e) {
  debugPrint('Timeout: $e');
} catch (e) {
  debugPrint('Unknown error: $e');
}
```

#### 3. **Replace print with debugPrint**
```dart
// ❌ Before
print('Debug info');

// ✅ After
import 'package:flutter/foundation.dart';
debugPrint('Debug info');
```

#### 4. **Use final for locals**
```dart
// ❌ Before
var message = 'Hello';
String name = getName();

// ✅ After
final message = 'Hello';
final name = getName();
```

#### 5. **Add const constructors**
```dart
// ❌ Before
return MaterialApp(
  home: HomeScreen(),
);

// ✅ After
return const MaterialApp(
  home: HomeScreen(), // Make HomeScreen const too
);
```

## Migration Strategy

### Phase 1: Fix Errors (Day 1)
1. Fix all `non_bool_condition` errors
2. Fix all `argument_type_not_assignable` errors
3. Fix all `return_of_invalid_type` errors

### Phase 2: Address Warnings (Day 2)
1. Add type arguments to generic constructors
2. Remove unused imports and fields
3. Fix inference failures

### Phase 3: Apply Best Practices (Day 3-4)
1. Add `await` or use `unawaited()`
2. Replace `catch (e)` with typed catches
3. Replace `print` with `debugPrint`
4. Make local variables `final`
5. Add `const` constructors

### Phase 4: Advanced Improvements (Week 2)
1. Add immutability with `freezed`
2. Implement dependency injection
3. Use sealed classes for state management

## Quick Fixes Script

Run these commands to auto-fix some issues:

```bash
# Auto-fix many issues
cd apps/mobile
dart fix --apply

# Format code
dart format .

# Analyze again to see remaining issues
flutter analyze
```

## Common Patterns to Update

### API Response Handling
```dart
// Create typed response handler
class ApiResponse<T> {
  final bool success;
  final T? data;
  final String? error;
  
  const ApiResponse({
    required this.success,
    this.data,
    this.error,
  });
  
  factory ApiResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Map<String, dynamic>) fromJson,
  ) {
    return ApiResponse(
      success: json['success'] == true,
      data: json['data'] != null ? fromJson(json['data']) : null,
      error: json['error']?.toString(),
    );
  }
}
```

### Navigation Pattern
```dart
// Create navigation helper
extension NavigationX on BuildContext {
  Future<T?> navigateTo<T>(Widget page) {
    return Navigator.push<T>(
      this,
      MaterialPageRoute<T>(
        builder: (_) => page,
      ),
    );
  }
}

// Usage
context.navigateTo(const HomeScreen());
```

### State Management Pattern
```dart
// Use sealed classes for state
sealed class LoadingState<T> {
  const LoadingState();
}

class Loading<T> extends LoadingState<T> {
  const Loading();
}

class Loaded<T> extends LoadingState<T> {
  final T data;
  const Loaded(this.data);
}

class Error<T> extends LoadingState<T> {
  final String message;
  const Error(this.message);
}
```

## Disable Rules (If Needed)

If certain rules are too strict for your team, disable them in `analysis_options.yaml`:

```yaml
linter:
  rules:
    # Disable specific rules
    always_specify_types: false  # If type inference is preferred
    prefer_expression_function_bodies: false  # If you prefer block bodies
```

## Benefits After Migration

✅ **Type Safety**: Catch errors at compile-time instead of runtime  
✅ **Performance**: Better tree-shaking and const optimizations  
✅ **Maintainability**: Clear intent and fewer bugs  
✅ **Modern Dart**: Leverage latest language features  
✅ **Team Productivity**: Consistent code style across the team  

## Next Steps

1. **Run `dart fix --apply`** to auto-fix simple issues
2. **Fix errors** in order of priority
3. **Add tests** to ensure refactoring doesn't break functionality
4. **Consider adding**:
   - `freezed` for immutable models
   - `riverpod` or `get_it` for dependency injection
   - `json_serializable` for type-safe JSON handling

## Resources

- [Effective Dart](https://dart.dev/effective-dart)
- [Dart Lints](https://dart.dev/tools/linter-rules)
- [Flutter Best Practices](https://docs.flutter.dev/development/data-and-backend/state-mgmt/intro)
- [Freezed Package](https://pub.dev/packages/freezed)
- [Riverpod](https://riverpod.dev/)
