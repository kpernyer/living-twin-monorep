import 'dart:convert';
import 'package:injectable/injectable.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/result/auth_result.dart';
import '../models/organization.dart';

/// Authentication service with dependency injection
/// Using @singleton to ensure single instance across the app
@singleton
class AuthServiceDI {
  final SharedPreferences _prefs;
  
  static const String _userKey = 'user_data';
  static const String _tokenKey = 'auth_token';
  
  // Current user data
  Map<String, dynamic>? _currentUser;
  String? _authToken;
  
  /// Constructor with injected dependencies
  AuthServiceDI(this._prefs) {
    _loadStoredAuth();
  }
  
  /// Load stored authentication data
  void _loadStoredAuth() {
    final userData = _prefs.getString(_userKey);
    final token = _prefs.getString(_tokenKey);
    
    if (userData != null) {
      _currentUser = jsonDecode(userData);
    }
    _authToken = token;
  }
  
  /// Check if user is authenticated
  bool get isAuthenticated => _currentUser != null && _authToken != null;
  
  /// Get current user
  Map<String, dynamic>? get currentUser => _currentUser;
  
  /// Get auth token
  String? get authToken => _authToken;
  
  /// Sign in with email and password - returns type-safe result
  Future<AuthResult> signInWithEmailAndPassword({
    required String email,
    required String password,
  }) async {
    try {
      // Validation
      if (email.isEmpty || password.isEmpty) {
        return const AuthFailure(
          message: 'Email and password are required',
          type: AuthErrorType.invalidCredentials,
        );
      }
      
      if (password.length < 6) {
        return const AuthFailure(
          message: 'Password must be at least 6 characters',
          type: AuthErrorType.weakPassword,
        );
      }
      
      // Check email domain for organization
      final organization = await _checkEmailDomainOrganization(email);
      
      // Create mock user (replace with actual API call)
      final userData = {
        'uid': 'user_${email.hashCode}',
        'email': email,
        'displayName': email.split('@')[0],
        'isAnonymous': false,
        'tenantId': organization?.id ?? 'demo',
        'createdAt': DateTime.now().toIso8601String(),
      };
      
      if (organization != null) {
        userData['organizationId'] = organization.id;
        userData['organization'] = organization.toJson();
      }
      
      // Generate token
      final token = 'token_${email.hashCode}_${DateTime.now().millisecondsSinceEpoch}';
      
      // Save to storage
      await _prefs.setString(_userKey, jsonEncode(userData));
      await _prefs.setString(_tokenKey, token);
      
      _currentUser = userData;
      _authToken = token;
      
      return AuthSuccess(
        uid: userData['uid'] as String,
        email: email,
        displayName: userData['displayName'] as String?,
        token: token,
        organizationId: organization?.id,
        organization: organization?.toJson(),
        isAnonymous: false,
      );
    } catch (e) {
      return AuthFailure(
        message: e.toString(),
        type: AuthErrorType.unknown,
      );
    }
  }
  
  /// Check if email domain is registered with an organization
  Future<Organization?> _checkEmailDomainOrganization(String email) async {
    try {
      final domain = email.split('@')[1].toLowerCase();
      
      // Mock check - replace with actual API call
      await Future.delayed(const Duration(milliseconds: 500));
      
      // Mock registered domains
      final registeredDomains = {
        'acme.com': const Organization(
          id: 'aprio_org_acme',
          name: 'Acme Corporation',
          webUrl: 'https://acme.com',
          industry: 'Technology',
          size: '201-1000 employees',
          techContact: 'tech@acme.com',
          businessContact: 'hr@acme.com',
          adminPortalUrl: 'https://admin.acme.aprioone.com',
          status: 'active',
          features: ['chat', 'pulse', 'ingest', 'analytics'],
          emailDomains: ['acme.com'],
          autoBindNewUsers: true,
        ),
      };
      
      return registeredDomains[domain];
    } catch (e) {
      return null;
    }
  }
  
  /// Sign out
  Future<void> signOut() async {
    await _prefs.remove(_userKey);
    await _prefs.remove(_tokenKey);
    
    _currentUser = null;
    _authToken = null;
  }
  
  /// Get ID token for API calls
  Future<String?> getIdToken() async {
    return _authToken;
  }
}
