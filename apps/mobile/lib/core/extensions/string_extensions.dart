/// Extension methods for String to provide validation and formatting utilities
extension StringX on String {
  /// Validates if the string is a valid email address
  bool get isValidEmail {
    return RegExp(
      r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    ).hasMatch(this);
  }
  
  /// Validates if the string is a strong password
  bool get isStrongPassword {
    // At least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
    if (length < 8) return false;
    
    final hasUpperCase = contains(RegExp(r'[A-Z]'));
    final hasLowerCase = contains(RegExp(r'[a-z]'));
    final hasDigit = contains(RegExp(r'[0-9]'));
    final hasSpecialChar = contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]'));
    
    return hasUpperCase && hasLowerCase && hasDigit && hasSpecialChar;
  }
  
  /// Checks if password is of medium strength
  bool get isMediumPassword {
    if (length < 6) return false;
    
    int criteriaCount = 0;
    if (contains(RegExp(r'[A-Z]'))) criteriaCount++;
    if (contains(RegExp(r'[a-z]'))) criteriaCount++;
    if (contains(RegExp(r'[0-9]'))) criteriaCount++;
    if (contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]'))) criteriaCount++;
    
    return criteriaCount >= 2;
  }
  
  /// Returns password strength level
  PasswordStrength get passwordStrength {
    if (isStrongPassword) return PasswordStrength.strong;
    if (isMediumPassword) return PasswordStrength.medium;
    if (length >= 4) return PasswordStrength.weak;
    return PasswordStrength.veryWeak;
  }
  
  /// Capitalizes the first letter of the string
  String get capitalized {
    if (isEmpty) return this;
    return '${this[0].toUpperCase()}${substring(1)}';
  }
  
  /// Capitalizes first letter of each word
  String get titleCase {
    if (isEmpty) return this;
    return split(' ').map((word) => word.capitalized).join(' ');
  }
  
  /// Removes all whitespace from the string
  String get removeAllWhitespace {
    return replaceAll(RegExp(r'\s+'), '');
  }
  
  /// Checks if string is null or empty
  bool get isNullOrEmpty {
    return isEmpty;
  }
  
  /// Checks if string is not null and not empty
  bool get isNotNullOrEmpty {
    return isNotEmpty;
  }
  
  /// Validates if the string is a valid phone number
  bool get isValidPhone {
    // Simple validation for international format
    return RegExp(r'^\+?[\d\s\-\(\)]+$').hasMatch(this) && 
           removeAllWhitespace.length >= 10;
  }
  
  /// Validates if the string is a valid URL
  bool get isValidUrl {
    return Uri.tryParse(this) != null && 
           (startsWith('http://') || startsWith('https://'));
  }
  
  /// Truncates string to specified length with ellipsis
  String truncate(int maxLength, {String ellipsis = '...'}) {
    if (length <= maxLength) return this;
    return '${substring(0, maxLength - ellipsis.length)}$ellipsis';
  }
  
  /// Returns initials from a name
  String get initials {
    if (isEmpty) return '';
    
    final words = trim().split(RegExp(r'\s+'));
    if (words.isEmpty) return '';
    
    if (words.length == 1) {
      return words.first.isNotEmpty ? words.first[0].toUpperCase() : '';
    }
    
    final first = words.first.isNotEmpty ? words.first[0].toUpperCase() : '';
    final last = words.last.isNotEmpty ? words.last[0].toUpperCase() : '';
    
    return '$first$last';
  }
  
  /// Converts string to a slug (URL-friendly format)
  String get toSlug {
    return toLowerCase()
        .replaceAll(RegExp(r'[^\w\s-]'), '')
        .replaceAll(RegExp(r'[\s_-]+'), '-')
        .replaceAll(RegExp(r'^-+|-+$'), '');
  }
  
  /// Masks sensitive information (e.g., email, phone)
  String get masked {
    if (isValidEmail) {
      final parts = split('@');
      if (parts.length != 2) return this;
      
      final username = parts[0];
      final domain = parts[1];
      
      if (username.length <= 2) {
        return '**@$domain';
      }
      
      return '${username.substring(0, 2)}${'*' * (username.length - 2)}@$domain';
    }
    
    if (isValidPhone) {
      final digits = removeAllWhitespace;
      if (digits.length <= 4) return '*' * digits.length;
      
      return '${digits.substring(0, 2)}${'*' * (digits.length - 4)}${digits.substring(digits.length - 2)}';
    }
    
    // Default masking for other strings
    if (length <= 4) return '*' * length;
    return '${substring(0, 2)}${'*' * (length - 4)}${substring(length - 2)}';
  }
  
  /// Converts string to int or returns null
  int? get toIntOrNull {
    return int.tryParse(this);
  }
  
  /// Converts string to double or returns null
  double? get toDoubleOrNull {
    return double.tryParse(this);
  }
  
  /// Checks if string contains only digits
  bool get isNumeric {
    return RegExp(r'^\d+$').hasMatch(this);
  }
  
  /// Checks if string contains only alphabets
  bool get isAlpha {
    return RegExp(r'^[a-zA-Z]+$').hasMatch(this);
  }
  
  /// Checks if string contains only alphanumeric characters
  bool get isAlphanumeric {
    return RegExp(r'^[a-zA-Z0-9]+$').hasMatch(this);
  }
  
  /// Returns the string reversed
  String get reversed {
    return split('').reversed.join();
  }
  
  /// Removes duplicate characters
  String get removeDuplicates {
    return split('').toSet().join();
  }
  
  /// Converts camelCase to snake_case
  String get toSnakeCase {
    return replaceAllMapped(
      RegExp(r'[A-Z]'),
      (match) => '_${match.group(0)!.toLowerCase()}',
    ).replaceFirst(RegExp(r'^_'), '');
  }
  
  /// Converts snake_case to camelCase
  String get toCamelCase {
    final words = split('_');
    if (words.isEmpty) return this;
    
    return words.first.toLowerCase() + 
           words.skip(1).map((word) => word.capitalized).join();
  }
}

/// Password strength levels
enum PasswordStrength {
  veryWeak,
  weak,
  medium,
  strong,
}

/// Extension for password strength enum
extension PasswordStrengthX on PasswordStrength {
  /// Returns a descriptive message for the strength level
  String get message {
    switch (this) {
      case PasswordStrength.veryWeak:
        return 'Very weak password';
      case PasswordStrength.weak:
        return 'Weak password';
      case PasswordStrength.medium:
        return 'Medium strength password';
      case PasswordStrength.strong:
        return 'Strong password';
    }
  }
  
  /// Returns a color code for UI representation
  int get colorValue {
    switch (this) {
      case PasswordStrength.veryWeak:
        return 0xFFD32F2F; // Red
      case PasswordStrength.weak:
        return 0xFFF57C00; // Orange
      case PasswordStrength.medium:
        return 0xFFFBC02D; // Yellow
      case PasswordStrength.strong:
        return 0xFF388E3C; // Green
    }
  }
}
