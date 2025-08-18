/// Sealed class for type-safe authentication results
/// Replaces Map<String, dynamic> returns from auth methods
sealed class AuthResult {
  const AuthResult();
}

/// Successful authentication result
class AuthSuccess extends AuthResult {
  final String uid;
  final String email;
  final String? displayName;
  final String token;
  final String? organizationId;
  final Map<String, dynamic>? organization;
  final bool isAnonymous;
  
  const AuthSuccess({
    required this.uid,
    required this.email,
    this.displayName,
    required this.token,
    this.organizationId,
    this.organization,
    required this.isAnonymous,
  });
}

/// Failed authentication result
class AuthFailure extends AuthResult {
  final String message;
  final AuthErrorType type;
  final String? code;
  
  const AuthFailure({
    required this.message,
    required this.type,
    this.code,
  });
}

/// Types of authentication errors
enum AuthErrorType {
  invalidCredentials,
  userNotFound,
  userDisabled,
  emailAlreadyInUse,
  weakPassword,
  invalidEmail,
  networkError,
  serverError,
  timeout,
  cancelled,
  unknown,
}
