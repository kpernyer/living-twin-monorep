import 'dart:convert';
import 'package:http/http.dart' as http;
import 'auth.dart';

class ApiClientEnhanced {
  final String baseUrl;
  final AuthService authService;
  
  ApiClientEnhanced({
    required this.baseUrl,
    required this.authService,
  });

  Future<Map<String, String>> _getHeaders() async {
    final token = await authService.getIdToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  /// Make a conversational query with memory
  Future<Map<String, dynamic>> conversationalQuery({
    required String question,
    String? conversationId,
    int k = 5,
    int memoryWindow = 10,
  }) async {
    try {
      final headers = await _getHeaders();
      final body = {
        'question': question,
        'k': k,
        'memoryWindow': memoryWindow,
        if (conversationId != null) 'conversationId': conversationId,
      };

      final response = await http.post(
        Uri.parse('$baseUrl/query/conversation/query'),
        headers: headers,
        body: jsonEncode(body),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'success': true,
          'answer': data['answer'] ?? '',
          'conversationId': data['conversationId'] ?? '',
          'sources': data['sources'] ?? [],
          'confidence': data['confidence'] ?? 0.0,
        };
      } else {
        return {
          'success': false,
          'error': 'Server error: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Get list of conversations
  Future<Map<String, dynamic>> getConversations() async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/query/conversations'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'success': true,
          'conversations': data['conversations'] ?? [],
        };
      } else {
        return {
          'success': false,
          'error': 'Server error: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Get full conversation history
  Future<Map<String, dynamic>> getConversation(String conversationId) async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/query/conversations/$conversationId'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'success': true,
          'conversation': data,
        };
      } else {
        return {
          'success': false,
          'error': 'Server error: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Delete a conversation
  Future<Map<String, dynamic>> deleteConversation(String conversationId) async {
    try {
      final headers = await _getHeaders();
      final response = await http.delete(
        Uri.parse('$baseUrl/query/conversations/$conversationId'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return {'success': true};
      } else {
        return {
          'success': false,
          'error': 'Server error: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Regular query (non-conversational)
  Future<Map<String, dynamic>> query({
    required String question,
    int k = 5,
  }) async {
    try {
      final headers = await _getHeaders();
      final body = {
        'question': question,
        'k': k,
      };

      final response = await http.post(
        Uri.parse('$baseUrl/query'),
        headers: headers,
        body: jsonEncode(body),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'success': true,
          'answer': data['answer'] ?? '',
          'sources': data['sources'] ?? [],
          'confidence': data['confidence'] ?? 0.0,
        };
      } else {
        return {
          'success': false,
          'error': 'Server error: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Ingest documents
  Future<Map<String, dynamic>> ingestDocument({
    required String content,
    required String title,
    String? source,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final headers = await _getHeaders();
      final body = {
        'content': content,
        'title': title,
        if (source != null) 'source': source,
        if (metadata != null) 'metadata': metadata,
      };

      final response = await http.post(
        Uri.parse('$baseUrl/ingest'),
        headers: headers,
        body: jsonEncode(body),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'success': true,
          'message': data['message'] ?? 'Document ingested successfully',
        };
      } else {
        return {
          'success': false,
          'error': 'Server error: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Health check
  Future<Map<String, dynamic>> healthCheck() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/healthz'),
      );

      if (response.statusCode == 200) {
        return {'success': true, 'status': 'healthy'};
      } else {
        return {
          'success': false,
          'error': 'Health check failed: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }
}
