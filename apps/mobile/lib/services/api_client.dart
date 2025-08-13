import 'dart:convert';
import 'package:http/http.dart' as http;
import 'auth.dart';

class ApiClient {
  final String base;
  final AuthService auth;
  ApiClient(this.base, this.auth);

  Future<http.Response> post(String path, Map<String, dynamic> body) async {
    final token = await auth.getIdToken();
    final headers = {
      'Content-Type':'application/json',
      if (token != null) 'Authorization':'Bearer $token'
    };
    return http.post(Uri.parse('$base$path'), headers: headers, body: jsonEncode(body));
  }
}
