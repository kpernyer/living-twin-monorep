import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/error/sentry_config.dart';

class AuthService {
  static const String _userKey = 'user_data';
  static const String _tokenKey = 'auth_token';
  
  // Singleton pattern
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  // Mock user data for demo purposes
  Map<String, dynamic>? _currentUser;
  String? _authToken;

  // Initialize auth service
  Future<void> initialize() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userData = prefs.getString(_userKey);
      final token = prefs.getString(_tokenKey);
      
      if (userData != null) {
        _currentUser = jsonDecode(userData);
        _authToken = token;
        
        // Set user context in Sentry if authenticated
        if (isAuthenticated) {
          SentryConfig.setUser(
            id: _currentUser!['uid'],
            email: _currentUser!['email'],
            username: _currentUser!['displayName'],
          );
          
          if (_currentUser!['tenantId'] != null) {
            SentryConfig.setOrganization(_currentUser!['tenantId']);
          }
        }
      }
    } catch (e, stackTrace) {
      // Track initialization errors
      await SentryConfig.captureException(
        e,
        stackTrace: stackTrace,
        extras: {'operation': 'auth_initialize'},
        tags: {'feature': 'authentication'},
      );
      rethrow;
    }
  }

  // Check if user is authenticated
  bool get isAuthenticated => _currentUser != null && _authToken != null;

  // Get current user
  Map<String, dynamic>? get currentUser => _currentUser;

  // Get auth token
  String? get authToken => _authToken;

  // Mock sign in (for demo purposes)
  Future<Map<String, dynamic>> signInAnonymously() async {
    try {
      // Create a mock user
      final mockUser = {
        'uid': 'demo_user_${DateTime.now().millisecondsSinceEpoch}',
        'email': 'demo@livingtwin.app',
        'displayName': 'Demo User',
        'isAnonymous': true,
        'tenantId': 'demo',
        'createdAt': DateTime.now().toIso8601String(),
      };

      // Generate a mock token
      final mockToken = 'demo_token_${DateTime.now().millisecondsSinceEpoch}';

      // Save to preferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userKey, jsonEncode(mockUser));
      await prefs.setString(_tokenKey, mockToken);

      _currentUser = mockUser;
      _authToken = mockToken;

      return {
        'success': true,
        'user': mockUser,
        'token': mockToken,
      };
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  // Mock sign in with email/password (with organization binding)
  Future<Map<String, dynamic>> signInWithEmailAndPassword({
    required String email,
    required String password,
  }) async {
    try {
      // Add breadcrumb for authentication attempt
      SentryConfig.addBreadcrumb(
        message: 'User attempting to sign in',
        category: 'authentication',
        data: {'email': email, 'method': 'email_password'},
      );

      // Simple validation for demo
      if (email.isEmpty || password.isEmpty) {
        throw Exception('Email and password are required');
      }

      if (password.length < 6) {
        throw Exception('Password must be at least 6 characters');
      }

      // Check if email domain is registered with AprioOne system
      final organization = await _checkEmailDomainOrganization(email);
      
      // Create a mock user
      final mockUser = {
        'uid': 'user_${email.hashCode}',
        'email': email,
        'displayName': email.split('@')[0],
        'isAnonymous': false,
        'tenantId': organization?['id'] ?? 'demo',
        'createdAt': DateTime.now().toIso8601String(),
      };

      // If organization found, bind user to it
      if (organization != null) {
        mockUser['organizationId'] = organization['id'];
        mockUser['organization'] = organization;
        mockUser['role'] = 'employee';
        mockUser['department'] = 'General';
        mockUser['permissions'] = ['read', 'write'];
        mockUser['source'] = 'email_domain_binding';
      }

      // Generate a mock token
      final mockToken = 'token_${email.hashCode}_${DateTime.now().millisecondsSinceEpoch}';

      // Save to preferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userKey, jsonEncode(mockUser));
      await prefs.setString(_tokenKey, mockToken);

      _currentUser = mockUser;
      _authToken = mockToken;

      // Set user context in Sentry
      SentryConfig.setUser(
        id: mockUser['uid'],
        email: mockUser['email'],
        username: mockUser['displayName'],
      );
      
      if (organization != null) {
        SentryConfig.setOrganization(organization['id']);
      }

      // Add success breadcrumb
      SentryConfig.addBreadcrumb(
        message: 'User successfully signed in',
        category: 'authentication',
        data: {'user_id': mockUser['uid'], 'organization': organization?['id']},
      );

      return {
        'success': true,
        'user': mockUser,
        'token': mockToken,
        'organization': organization,
      };
    } catch (e, stackTrace) {
      // Track authentication errors
      await SentryConfig.captureException(
        e,
        stackTrace: stackTrace,
        extras: {
          'operation': 'sign_in_email_password',
          'email': email,
        },
        tags: {'feature': 'authentication'},
      );

      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  // Check if email domain is registered with an organization in AprioOne system
  Future<Map<String, dynamic>?> _checkEmailDomainOrganization(String email) async {
    try {
      final domain = email.split('@')[1].toLowerCase();
      
      // Mock API call to AprioOne system to check domain registration
      await Future.delayed(const Duration(milliseconds: 500));
      
      // Mock registered domains (in real system, this would be an API call)
      final registeredDomains = {
        'acme.com': {
          'id': 'aprio_org_acme',
          'name': 'Acme Corporation',
          'webUrl': 'https://acme.com',
          'industry': 'Technology',
          'size': '201-1000 employees',
          'techContact': 'tech@acme.com',
          'businessContact': 'hr@acme.com',
          'adminPortalUrl': 'https://admin.acme.aprioone.com',
          'status': 'active',
          'features': ['chat', 'pulse', 'ingest', 'analytics'],
          'branding': {
            'primaryColor': '#1976D2',
            'logo': 'https://acme.com/logo.png',
            'theme': 'corporate'
          },
          'emailDomains': ['acme.com'],
          'autoBindNewUsers': true,
        },
        'techcorp.io': {
          'id': 'aprio_org_techcorp',
          'name': 'TechCorp Solutions',
          'webUrl': 'https://techcorp.io',
          'industry': 'Software',
          'size': '51-200 employees',
          'techContact': 'admin@techcorp.io',
          'businessContact': 'hr@techcorp.io',
          'adminPortalUrl': 'https://admin.techcorp.aprioone.com',
          'status': 'active',
          'features': ['chat', 'pulse', 'ingest'],
          'branding': {
            'primaryColor': '#4CAF50',
            'logo': 'https://techcorp.io/logo.png',
            'theme': 'modern'
          },
          'emailDomains': ['techcorp.io'],
          'autoBindNewUsers': true,
        }
      };
      
      return registeredDomains[domain];
    } catch (e) {
      // If domain check fails, continue without organization binding
      return null;
    }
  }

  // Mock sign up
  Future<Map<String, dynamic>> createUserWithEmailAndPassword({
    required String email,
    required String password,
    String? displayName,
  }) async {
    try {
      // Simple validation for demo
      if (email.isEmpty || password.isEmpty) {
        throw Exception('Email and password are required');
      }

      if (password.length < 6) {
        throw Exception('Password must be at least 6 characters');
      }

      if (!email.contains('@')) {
        throw Exception('Please enter a valid email address');
      }

      // Create a mock user
      final mockUser = {
        'uid': 'user_${email.hashCode}',
        'email': email,
        'displayName': displayName ?? email.split('@')[0],
        'isAnonymous': false,
        'tenantId': 'demo',
        'createdAt': DateTime.now().toIso8601String(),
      };

      // Generate a mock token
      final mockToken = 'token_${email.hashCode}_${DateTime.now().millisecondsSinceEpoch}';

      // Save to preferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userKey, jsonEncode(mockUser));
      await prefs.setString(_tokenKey, mockToken);

      _currentUser = mockUser;
      _authToken = mockToken;

      return {
        'success': true,
        'user': mockUser,
        'token': mockToken,
      };
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  // Sign out
  Future<void> signOut() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_userKey);
    await prefs.remove(_tokenKey);
    
    _currentUser = null;
    _authToken = null;
  }

  // Get ID token (for API calls)
  Future<String?> getIdToken() async {
    return _authToken;
  }

  // Refresh token (mock implementation)
  Future<String?> refreshToken() async {
    if (_currentUser != null) {
      final newToken = 'refreshed_token_${DateTime.now().millisecondsSinceEpoch}';
      
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_tokenKey, newToken);
      
      _authToken = newToken;
      return newToken;
    }
    return null;
  }

  // Update user profile
  Future<Map<String, dynamic>> updateProfile({
    String? displayName,
    String? photoURL,
  }) async {
    try {
      if (_currentUser == null) {
        throw Exception('No user signed in');
      }

      final updatedUser = Map<String, dynamic>.from(_currentUser!);
      
      if (displayName != null) {
        updatedUser['displayName'] = displayName;
      }
      
      if (photoURL != null) {
        updatedUser['photoURL'] = photoURL;
      }
      
      updatedUser['updatedAt'] = DateTime.now().toIso8601String();

      // Save to preferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userKey, jsonEncode(updatedUser));

      _currentUser = updatedUser;

      return {
        'success': true,
        'user': updatedUser,
      };
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  // Get user claims (for authorization)
  Map<String, dynamic> getUserClaims() {
    if (_currentUser == null) return {};
    
    return {
      'uid': _currentUser!['uid'],
      'email': _currentUser!['email'],
      'tenantId': _currentUser!['tenantId'] ?? 'demo',
      'role': 'user', // Default role
      'permissions': ['read', 'write'], // Default permissions
    };
  }

  // Check if user has permission
  bool hasPermission(String permission) {
    final claims = getUserClaims();
    final permissions = claims['permissions'] as List<dynamic>? ?? [];
    return permissions.contains(permission);
  }

  // Get tenant ID for multi-tenancy
  String getTenantId() {
    return _currentUser?['tenantId'] ?? 'demo';
  }

  // Mock Google Sign-In
  Future<Map<String, dynamic>> signInWithGoogle() async {
    try {
      // Simulate Google Sign-In flow
      await Future.delayed(const Duration(seconds: 1));
      
      // Create a mock Google user
      final mockUser = {
        'uid': 'google_user_${DateTime.now().millisecondsSinceEpoch}',
        'email': 'user@gmail.com',
        'displayName': 'Google User',
        'photoURL': 'https://via.placeholder.com/150',
        'isAnonymous': false,
        'provider': 'google',
        'tenantId': 'demo',
        'createdAt': DateTime.now().toIso8601String(),
      };

      // Generate a mock token
      final mockToken = 'google_token_${DateTime.now().millisecondsSinceEpoch}';

      // Save to preferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userKey, jsonEncode(mockUser));
      await prefs.setString(_tokenKey, mockToken);

      _currentUser = mockUser;
      _authToken = mockToken;

      return {
        'success': true,
        'user': mockUser,
        'token': mockToken,
      };
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  // Accept invitation to join organization (from AprioOne system)
  Future<Map<String, dynamic>> acceptInvitation(String invitationCode) async {
    try {
      // Validate invitation code format (AprioOne format)
      if (!invitationCode.startsWith('APRIO-') || invitationCode.length < 15) {
        throw Exception('Invalid invitation code format. Please check with your organization admin.');
      }

      // Mock API call to AprioOne system to validate invitation
      await Future.delayed(const Duration(seconds: 2));
      
      // Extract organization info from AprioOne invitation code (mock)
      final parts = invitationCode.split('-');
      if (parts.length < 3) {
        throw Exception('Invalid invitation code format');
      }
      
      final orgCode = parts[1];
      final inviteId = parts[2];
      
      // Mock organization data from AprioOne system
      final mockOrganization = {
        'id': 'aprio_org_$orgCode',
        'name': 'Acme Corporation',
        'webUrl': 'https://acme.com',
        'industry': 'Technology',
        'size': '201-1000 employees',
        'techContact': 'tech@acme.com',
        'businessContact': 'hr@acme.com',
        'adminPortalUrl': 'https://admin.acme.aprioone.com',
        'createdBy': 'aprioone_admin',
        'status': 'active',
        'features': ['chat', 'pulse', 'ingest', 'analytics'],
        'branding': {
          'primaryColor': '#1976D2',
          'logo': 'https://acme.com/logo.png',
          'theme': 'corporate'
        }
      };

      // Create user account bound to the organization
      final mockUser = {
        'uid': 'aprio_user_${DateTime.now().millisecondsSinceEpoch}',
        'email': 'user@acme.com', // Would be provided during invitation
        'displayName': 'Employee User',
        'isAnonymous': false,
        'organizationId': mockOrganization['id'],
        'organization': mockOrganization,
        'tenantId': mockOrganization['id'],
        'role': 'employee', // Role assigned by organization admin
        'department': 'Engineering', // From organization structure
        'permissions': ['read', 'write'], // Based on role
        'createdAt': DateTime.now().toIso8601String(),
        'invitedBy': 'org_admin@acme.com',
        'invitationCode': invitationCode,
        'inviteId': inviteId,
        'source': 'aprioone_invitation'
      };

      // Generate a mock token
      final mockToken = 'aprio_token_${DateTime.now().millisecondsSinceEpoch}';

      // Save to preferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userKey, jsonEncode(mockUser));
      await prefs.setString(_tokenKey, mockToken);

      _currentUser = mockUser;
      _authToken = mockToken;

      return {
        'success': true,
        'user': mockUser,
        'token': mockToken,
        'organization': mockOrganization,
        'message': 'Successfully joined ${mockOrganization['name']}!'
      };
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  // Create new organization
  Future<Map<String, dynamic>> createOrganization({
    required String name,
    required String industry,
    required String size,
    String? department,
    String? role,
  }) async {
    try {
      if (_currentUser == null) {
        throw Exception('No user signed in');
      }

      // Generate organization ID
      final orgId = 'org_${name.toLowerCase().replaceAll(' ', '_')}_${DateTime.now().millisecondsSinceEpoch}';
      
      // Create organization data
      final organization = {
        'id': orgId,
        'name': name,
        'industry': industry,
        'size': size,
        'department': department ?? 'General',
        'role': role ?? 'Admin',
        'createdAt': DateTime.now().toIso8601String(),
        'createdBy': _currentUser!['uid'],
        'permissions': ['read', 'write', 'admin'],
      };

      // Update user with organization
      final updatedUser = Map<String, dynamic>.from(_currentUser!);
      updatedUser['organizationId'] = orgId;
      updatedUser['organization'] = organization;
      updatedUser['tenantId'] = orgId;
      updatedUser['role'] = role ?? 'Admin';
      updatedUser['department'] = department ?? 'General';
      updatedUser['updatedAt'] = DateTime.now().toIso8601String();

      // Save to preferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userKey, jsonEncode(updatedUser));

      _currentUser = updatedUser;

      return {
        'success': true,
        'user': updatedUser,
        'organization': organization,
        'invitationCode': 'ORG-${orgId.toUpperCase()}-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}',
      };
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  // Generate invitation code for organization
  Future<String?> generateInvitationCode() async {
    if (_currentUser == null || _currentUser!['organizationId'] == null) {
      return null;
    }

    final orgId = _currentUser!['organizationId'];
    return 'ORG-${orgId.toString().toUpperCase()}-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}';
  }

  // Get organization info
  Map<String, dynamic>? getOrganization() {
    return _currentUser?['organization'];
  }

  // Check if user is organization admin
  bool isOrganizationAdmin() {
    final claims = getUserClaims();
    final permissions = claims['permissions'] as List<dynamic>? ?? [];
    return permissions.contains('admin');
  }

  // Update organization settings (admin only)
  Future<Map<String, dynamic>> updateOrganization({
    String? name,
    String? industry,
    String? size,
  }) async {
    try {
      if (_currentUser == null || !isOrganizationAdmin()) {
        throw Exception('Insufficient permissions');
      }

      final organization = Map<String, dynamic>.from(_currentUser!['organization'] ?? {});
      
      if (name != null) organization['name'] = name;
      if (industry != null) organization['industry'] = industry;
      if (size != null) organization['size'] = size;
      organization['updatedAt'] = DateTime.now().toIso8601String();

      // Update user data
      final updatedUser = Map<String, dynamic>.from(_currentUser!);
      updatedUser['organization'] = organization;
      updatedUser['updatedAt'] = DateTime.now().toIso8601String();

      // Save to preferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userKey, jsonEncode(updatedUser));

      _currentUser = updatedUser;

      return {
        'success': true,
        'organization': organization,
      };
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }
}
