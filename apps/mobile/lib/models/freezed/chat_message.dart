import 'package:freezed_annotation/freezed_annotation.dart';

part 'chat_message.freezed.dart';
part 'chat_message.g.dart';

/// Immutable ChatMessage model with freezed
/// 
/// Benefits:
/// - Automatic copyWith() method for creating modified copies
/// - Built-in equality (==) and hashCode
/// - Automatic toString() for debugging
/// - Type-safe JSON serialization
@freezed
class ChatMessage with _$ChatMessage {
  const factory ChatMessage({
    required String id,
    required String text,
    required bool isUser,
    required DateTime timestamp,
    @Default([]) List<String> sources,
    double? confidence,
  }) = _ChatMessage;

  /// Creates a ChatMessage from JSON
  factory ChatMessage.fromJson(Map<String, dynamic> json) =>
      _$ChatMessageFromJson(json);
}

/// Example usage:
/// ```dart
/// // Create immutable message
/// final message = ChatMessage(
///   id: '123',
///   text: 'Hello',
///   isUser: true,
///   timestamp: DateTime.now(),
/// );
/// 
/// // Create a copy with modifications (original unchanged)
/// final updated = message.copyWith(text: 'Hello World');
/// 
/// // Automatic equality
/// print(message == updated); // false
/// 
/// // Type-safe JSON
/// final json = message.toJson();
/// final decoded = ChatMessage.fromJson(json);
