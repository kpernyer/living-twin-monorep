import 'package:intl/intl.dart';

/// Extension methods for DateTime to provide convenient formatting
extension DateTimeX on DateTime {
  /// Returns a human-readable time ago string
  String get timeAgo {
    final now = DateTime.now();
    final difference = now.difference(this);
    
    if (difference.inDays > 365) {
      final years = (difference.inDays / 365).floor();
      return years == 1 ? '1 year ago' : '$years years ago';
    } else if (difference.inDays > 30) {
      final months = (difference.inDays / 30).floor();
      return months == 1 ? '1 month ago' : '$months months ago';
    } else if (difference.inDays > 7) {
      final weeks = (difference.inDays / 7).floor();
      return weeks == 1 ? '1 week ago' : '$weeks weeks ago';
    } else if (difference.inDays > 0) {
      return difference.inDays == 1 ? 'Yesterday' : '${difference.inDays} days ago';
    } else if (difference.inHours > 0) {
      return difference.inHours == 1 ? '1 hour ago' : '${difference.inHours} hours ago';
    } else if (difference.inMinutes > 0) {
      return difference.inMinutes == 1 ? '1 minute ago' : '${difference.inMinutes} minutes ago';
    } else {
      return 'Just now';
    }
  }
  
  /// Returns a short time ago string (e.g., "2h", "3d")
  String get shortTimeAgo {
    final now = DateTime.now();
    final difference = now.difference(this);
    
    if (difference.inDays > 365) {
      return '${(difference.inDays / 365).floor()}y';
    } else if (difference.inDays > 30) {
      return '${(difference.inDays / 30).floor()}mo';
    } else if (difference.inDays > 7) {
      return '${(difference.inDays / 7).floor()}w';
    } else if (difference.inDays > 0) {
      return '${difference.inDays}d';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m';
    } else {
      return 'now';
    }
  }
  
  /// Checks if this date is today
  bool get isToday {
    final now = DateTime.now();
    return year == now.year && month == now.month && day == now.day;
  }
  
  /// Checks if this date is yesterday
  bool get isYesterday {
    final yesterday = DateTime.now().subtract(const Duration(days: 1));
    return year == yesterday.year && month == yesterday.month && day == yesterday.day;
  }
  
  /// Checks if this date is within the current week
  bool get isThisWeek {
    final now = DateTime.now();
    final startOfWeek = now.subtract(Duration(days: now.weekday - 1));
    final endOfWeek = startOfWeek.add(const Duration(days: 6));
    return isAfter(startOfWeek.subtract(const Duration(days: 1))) && 
           isBefore(endOfWeek.add(const Duration(days: 1)));
  }
  
  /// Returns formatted date string
  String get formatted {
    if (isToday) {
      return 'Today ${DateFormat.jm().format(this)}';
    } else if (isYesterday) {
      return 'Yesterday ${DateFormat.jm().format(this)}';
    } else if (isThisWeek) {
      return DateFormat('EEEE').format(this);
    } else if (year == DateTime.now().year) {
      return DateFormat('MMM d').format(this);
    } else {
      return DateFormat('MMM d, y').format(this);
    }
  }
  
  /// Returns date only (without time)
  DateTime get dateOnly {
    return DateTime(year, month, day);
  }
  
  /// Returns time only string
  String get timeOnly {
    return DateFormat.jm().format(this);
  }
  
  /// Returns full date and time string
  String get fullDateTime {
    return DateFormat('MMM d, y • h:mm a').format(this);
  }
  
  /// Returns ISO 8601 string
  String get iso8601 {
    return toIso8601String();
  }
  
  /// Checks if this date is in the past
  bool get isPast {
    return isBefore(DateTime.now());
  }
  
  /// Checks if this date is in the future
  bool get isFuture {
    return isAfter(DateTime.now());
  }
  
  /// Returns the start of the day (00:00:00)
  DateTime get startOfDay {
    return DateTime(year, month, day);
  }
  
  /// Returns the end of the day (23:59:59)
  DateTime get endOfDay {
    return DateTime(year, month, day, 23, 59, 59, 999);
  }
  
  /// Add business days (excluding weekends)
  DateTime addBusinessDays(int days) {
    var date = this;
    var daysToAdd = days;
    
    while (daysToAdd > 0) {
      date = date.add(const Duration(days: 1));
      if (date.weekday != DateTime.saturday && date.weekday != DateTime.sunday) {
        daysToAdd--;
      }
    }
    
    return date;
  }
}
