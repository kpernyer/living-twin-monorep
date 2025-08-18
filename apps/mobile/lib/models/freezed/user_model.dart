import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_model.freezed.dart';
part 'user_model.g.dart';

/// User preferences as an immutable model
@freezed
class UserPreferences with _$UserPreferences {
  const factory UserPreferences({
    @Default('auto') String theme,
    @Default(true) bool notifications,
    @Default('en') String language,
  }) = _UserPreferences;

  factory UserPreferences.fromJson(Map<String, dynamic> json) =>
      _$UserPreferencesFromJson(json);
}

/// Immutable User model with freezed
/// 
/// Key benefits over mutable models:
/// - Thread-safe: Cannot be accidentally modified
/// - Predictable: State changes only through copyWith()
/// - Cache-friendly: Can safely cache without defensive copying
/// - Redux/BLoC friendly: Perfect for state management
@freezed
class UserModel with _$UserModel {
  const factory UserModel({
    required String id,
    required String tenantId,
    required String email,
    required String displayName,
    required String role,
    required String firebaseUid,
    required DateTime createdAt,
    required DateTime updatedAt,
    @Default('active') String status,
    String? createdBy,
    String? avatarUrl,
    DateTime? lastLogin,
    UserPreferences? preferences,
    Map<String, dynamic>? metadata,
  }) = _UserModel;

  factory UserModel.fromJson(Map<String, dynamic> json) =>
      _$UserModelFromJson(json);
}

/// Example showing immutability benefits:
/// ```dart
/// // Original user (immutable)
/// final user = UserModel(
///   id: 'user-123',
///   tenantId: 'tenant-456',
///   email: 'user@example.com',
///   displayName: 'John Doe',
///   role: 'member',
///   firebaseUid: 'firebase-789',
///   createdAt: DateTime.now(),
///   updatedAt: DateTime.now(),
/// );
/// 
/// // Update user - creates NEW instance, original unchanged
/// final updatedUser = user.copyWith(
///   displayName: 'Jane Doe',
///   preferences: UserPreferences(
///     theme: 'dark',
///     notifications: false,
///   ),
///   updatedAt: DateTime.now(),
/// );
/// 
/// // Original is unchanged (immutable)
/// print(user.displayName); // Still "John Doe"
/// print(updatedUser.displayName); // "Jane Doe"
/// 
/// // Deep copy with nested updates
/// final withNewPrefs = updatedUser.copyWith(
///   preferences: updatedUser.preferences?.copyWith(
///     language: 'es',
///   ),
/// );
/// 
/// // Equality checking built-in
/// print(user == updatedUser); // false
/// 
/// // Pattern matching (Dart 3+)
/// final status = switch(user.role) {
///   'admin' => 'Full access',
///   'member' => 'Limited access',
///   _ => 'No access',
/// };
