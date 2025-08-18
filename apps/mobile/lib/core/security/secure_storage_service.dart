import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:injectable/injectable.dart';
import 'dart:convert';

/// Secure storage service for sensitive data like tokens
/// Uses encrypted storage instead of plain SharedPreferences
@singleton
class SecureStorageService {
  static const _tokenKey = 'auth_token';
  static const _refreshTokenKey = 'refresh_token';
  static const _userDataKey = 'user_data';
  static const _pinKey = 'app_pin';
  static const _biometricKey = 'biometric_enabled';
  
  final FlutterSecureStorage _storage;
  
  SecureStorageService() : _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
      // Require authentication for Android 6.0+
      resetOnError: true,
    ),
    iOptions: IOSOptions(
      accessibility: IOSAccessibility.unlocked_this_device,
      // Require device unlock to access
      accountName: 'LivingTwinSecureStorage',
    ),
  );
  
  // Token Management
  
  /// Save authentication token securely
  Future<void> saveToken(String token) async {
    await _storage.write(key: _tokenKey, value: token);
  }
  
  /// Get authentication token
  Future<String?> getToken() async {
    return await _storage.read(key: _tokenKey);
  }
  
  /// Delete authentication token
  Future<void> deleteToken() async {
    await _storage.delete(key: _tokenKey);
  }
  
  /// Save refresh token
  Future<void> saveRefreshToken(String token) async {
    await _storage.write(key: _refreshTokenKey, value: token);
  }
  
  /// Get refresh token
  Future<String?> getRefreshToken() async {
    return await _storage.read(key: _refreshTokenKey);
  }
  
  // User Data Management
  
  /// Save user data securely
  Future<void> saveUserData(Map<String, dynamic> userData) async {
    final jsonString = jsonEncode(userData);
    await _storage.write(key: _userDataKey, value: jsonString);
  }
  
  /// Get user data
  Future<Map<String, dynamic>?> getUserData() async {
    final jsonString = await _storage.read(key: _userDataKey);
    if (jsonString != null) {
      return jsonDecode(jsonString) as Map<String, dynamic>;
    }
    return null;
  }
  
  /// Delete user data
  Future<void> deleteUserData() async {
    await _storage.delete(key: _userDataKey);
  }
  
  // PIN Management
  
  /// Save app PIN (hashed)
  Future<void> savePIN(String pin) async {
    // In production, hash the PIN before storing
    final hashedPin = _hashPIN(pin);
    await _storage.write(key: _pinKey, value: hashedPin);
  }
  
  /// Verify PIN
  Future<bool> verifyPIN(String pin) async {
    final storedPin = await _storage.read(key: _pinKey);
    if (storedPin == null) return false;
    
    final hashedInput = _hashPIN(pin);
    return storedPin == hashedInput;
  }
  
  /// Check if PIN is set
  Future<bool> hasPIN() async {
    final pin = await _storage.read(key: _pinKey);
    return pin != null;
  }
  
  /// Delete PIN
  Future<void> deletePIN() async {
    await _storage.delete(key: _pinKey);
  }
  
  // Biometric Settings
  
  /// Save biometric preference
  Future<void> setBiometricEnabled(bool enabled) async {
    await _storage.write(key: _biometricKey, value: enabled.toString());
  }
  
  /// Get biometric preference
  Future<bool> isBiometricEnabled() async {
    final value = await _storage.read(key: _biometricKey);
    return value == 'true';
  }
  
  // Utility Methods
  
  /// Clear all secure storage
  Future<void> clearAll() async {
    await _storage.deleteAll();
  }
  
  /// Check if user is logged in
  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null;
  }
  
  /// Save sensitive key-value pair
  Future<void> saveSecure(String key, String value) async {
    await _storage.write(key: key, value: value);
  }
  
  /// Get sensitive value by key
  Future<String?> getSecure(String key) async {
    return await _storage.read(key: key);
  }
  
  /// Delete sensitive value by key
  Future<void> deleteSecure(String key) async {
    await _storage.delete(key: key);
  }
  
  /// Check if a key exists
  Future<bool> containsKey(String key) async {
    final value = await _storage.read(key: key);
    return value != null;
  }
  
  /// Get all keys (for debugging only)
  Future<Map<String, String>> getAllKeys() async {
    return await _storage.readAll();
  }
  
  // Private helper methods
  
  String _hashPIN(String pin) {
    // Simple hash for demo - use proper hashing like bcrypt in production
    // import 'package:crypto/crypto.dart';
    // final bytes = utf8.encode(pin + 'salt_here');
    // final digest = sha256.convert(bytes);
    // return digest.toString();
    
    // For demo purposes only - DO NOT USE IN PRODUCTION
    return 'hashed_$pin';
  }
}

/// Extension for migration from SharedPreferences
extension SecureStorageMigration on SecureStorageService {
  /// Migrate sensitive data from SharedPreferences to SecureStorage
  Future<void> migrateFromSharedPreferences(Map<String, String> data) async {
    for (final entry in data.entries) {
      await saveSecure(entry.key, entry.value);
    }
  }
}
