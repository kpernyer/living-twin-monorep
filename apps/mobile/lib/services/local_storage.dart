import 'dart:convert';

import 'package:path/path.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite/sqflite.dart';
import 'package:uuid/uuid.dart';

class LocalStorageService {
  static Database? _database;
  static const String _dbName = 'living_twin.db';
  static const int _dbVersion = 1;

  // Singleton pattern
  static final LocalStorageService _instance = LocalStorageService._internal();
  factory LocalStorageService() => _instance;
  LocalStorageService._internal();

  Future<Database> get database async {
    _database ??= await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final path = join(await getDatabasesPath(), _dbName);
    return openDatabase(
      path,
      version: _dbVersion,
      onCreate: _onCreate,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    // Chat messages table
    await db.execute('''
      CREATE TABLE chat_messages (
        id TEXT PRIMARY KEY,
        question TEXT NOT NULL,
        answer TEXT,
        confidence REAL,
        sources TEXT,
        timestamp INTEGER NOT NULL,
        is_synced INTEGER DEFAULT 0,
        tenant_id TEXT DEFAULT 'demo'
      )
    ''');

    // Pulse data table
    await db.execute('''
      CREATE TABLE pulse_data (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT,
        metadata TEXT,
        timestamp INTEGER NOT NULL,
        is_synced INTEGER DEFAULT 0,
        tenant_id TEXT DEFAULT 'demo'
      )
    ''');

    // Retry queue table
    await db.execute('''
      CREATE TABLE retry_queue (
        id TEXT PRIMARY KEY,
        endpoint TEXT NOT NULL,
        method TEXT NOT NULL,
        payload TEXT NOT NULL,
        retry_count INTEGER DEFAULT 0,
        max_retries INTEGER DEFAULT 3,
        created_at INTEGER NOT NULL,
        last_attempt INTEGER,
        tenant_id TEXT DEFAULT 'demo'
      )
    ''');

    // Documents table for offline access
    await db.execute('''
      CREATE TABLE documents (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT,
        type TEXT DEFAULT 'text',
        chunks INTEGER DEFAULT 0,
        timestamp INTEGER NOT NULL,
        is_synced INTEGER DEFAULT 0,
        tenant_id TEXT DEFAULT 'demo'
      )
    ''');
  }

  // Chat Messages
  Future<String> saveChatMessage({
    required String question,
    String? answer,
    double? confidence,
    List<String>? sources,
    String tenantId = 'demo',
  }) async {
    final db = await database;
    final id = const Uuid().v4();
    
    await db.insert('chat_messages', {
      'id': id,
      'question': question,
      'answer': answer,
      'confidence': confidence,
      'sources': sources != null ? jsonEncode(sources) : null,
      'timestamp': DateTime.now().millisecondsSinceEpoch,
      'is_synced': answer != null ? 1 : 0,
      'tenant_id': tenantId,
    });
    
    return id;
  }

  Future<void> updateChatMessage(String id, {
    String? answer,
    double? confidence,
    List<String>? sources,
    bool? isSynced,
  }) async {
    final db = await database;
    final updates = <String, dynamic>{};
    
    if (answer != null) updates['answer'] = answer;
    if (confidence != null) updates['confidence'] = confidence;
    if (sources != null) updates['sources'] = jsonEncode(sources);
    if (isSynced != null) updates['is_synced'] = isSynced ? 1 : 0;
    
    if (updates.isNotEmpty) {
      await db.update('chat_messages', updates, where: 'id = ?', whereArgs: [id]);
    }
  }

  Future<List<Map<String, dynamic>>> getChatMessages({
    String tenantId = 'demo',
    int limit = 50,
  }) async {
    final db = await database;
    final results = await db.query(
      'chat_messages',
      where: 'tenant_id = ?',
      whereArgs: [tenantId],
      orderBy: 'timestamp DESC',
      limit: limit,
    );
    
    return results.map((row) {
      final sources = row['sources'] as String?;
      return {
        ...row,
        'sources': sources != null ? List<String>.from(jsonDecode(sources)) : <String>[],
        'is_synced': row['is_synced'] == 1,
      };
    }).toList();
  }

  // Pulse Data
  Future<void> savePulseData({
    required String type,
    required String title,
    String? content,
    Map<String, dynamic>? metadata,
    String tenantId = 'demo',
  }) async {
    final db = await database;
    final id = const Uuid().v4();
    
    await db.insert('pulse_data', {
      'id': id,
      'type': type,
      'title': title,
      'content': content,
      'metadata': metadata != null ? jsonEncode(metadata) : null,
      'timestamp': DateTime.now().millisecondsSinceEpoch,
      'tenant_id': tenantId,
    });
  }

  Future<List<Map<String, dynamic>>> getPulseData({
    String? type,
    String tenantId = 'demo',
    int limit = 20,
  }) async {
    final db = await database;
    var where = 'tenant_id = ?';
    final whereArgs = <dynamic>[tenantId];
    
    if (type != null) {
      where += ' AND type = ?';
      whereArgs.add(type);
    }
    
    final results = await db.query(
      'pulse_data',
      where: where,
      whereArgs: whereArgs,
      orderBy: 'timestamp DESC',
      limit: limit,
    );
    
    return results.map((row) {
      final metadata = row['metadata'] as String?;
      return {
        ...row,
        'metadata': metadata != null ? jsonDecode(metadata) : <String, dynamic>{},
        'is_synced': row['is_synced'] == 1,
      };
    }).toList();
  }

  // Documents
  Future<void> saveDocument({
    required String title,
    String? content,
    String type = 'text',
    int chunks = 0,
    String tenantId = 'demo',
  }) async {
    final db = await database;
    final id = const Uuid().v4();
    
    await db.insert('documents', {
      'id': id,
      'title': title,
      'content': content,
      'type': type,
      'chunks': chunks,
      'timestamp': DateTime.now().millisecondsSinceEpoch,
      'tenant_id': tenantId,
    });
  }

  Future<List<Map<String, dynamic>>> getDocuments({
    String tenantId = 'demo',
    int limit = 20,
  }) async {
    final db = await database;
    final results = await db.query(
      'documents',
      where: 'tenant_id = ?',
      whereArgs: [tenantId],
      orderBy: 'timestamp DESC',
      limit: limit,
    );
    
    return results.map((row) => {
      ...row,
      'is_synced': row['is_synced'] == 1,
    }).toList();
  }

  // Retry Queue
  Future<void> addToRetryQueue({
    required String endpoint,
    required String method,
    required Map<String, dynamic> payload,
    int maxRetries = 3,
    String tenantId = 'demo',
  }) async {
    final db = await database;
    final id = const Uuid().v4();
    
    await db.insert('retry_queue', {
      'id': id,
      'endpoint': endpoint,
      'method': method,
      'payload': jsonEncode(payload),
      'max_retries': maxRetries,
      'created_at': DateTime.now().millisecondsSinceEpoch,
      'tenant_id': tenantId,
    });
  }

  Future<List<Map<String, dynamic>>> getRetryQueue({
    String tenantId = 'demo',
  }) async {
    final db = await database;
    final results = await db.query(
      'retry_queue',
      where: 'tenant_id = ? AND retry_count < max_retries',
      whereArgs: [tenantId],
      orderBy: 'created_at ASC',
    );
    
    return results.map((row) => {
      ...row,
      'payload': jsonDecode(row['payload']! as String),
    }).toList();
  }

  Future<void> updateRetryItem(String id, {
    int? retryCount,
    int? lastAttempt,
  }) async {
    final db = await database;
    final updates = <String, dynamic>{};
    
    if (retryCount != null) updates['retry_count'] = retryCount;
    if (lastAttempt != null) updates['last_attempt'] = lastAttempt;
    
    if (updates.isNotEmpty) {
      await db.update('retry_queue', updates, where: 'id = ?', whereArgs: [id]);
    }
  }

  Future<void> removeFromRetryQueue(String id) async {
    final db = await database;
    await db.delete('retry_queue', where: 'id = ?', whereArgs: [id]);
  }

  // Preferences
  Future<void> setPreference(String key, value) async {
    final prefs = await SharedPreferences.getInstance();
    if (value is String) {
      await prefs.setString(key, value);
    } else if (value is int) {
      await prefs.setInt(key, value);
    } else if (value is double) {
      await prefs.setDouble(key, value);
    } else if (value is bool) {
      await prefs.setBool(key, value);
    } else {
      await prefs.setString(key, jsonEncode(value));
    }
  }

  Future<T?> getPreference<T>(String key) async {
    final prefs = await SharedPreferences.getInstance();
    final value = prefs.get(key);
    
    if (value == null) return null;
    
    if (T == String && value is String) return value as T;
    if (T == int && value is int) return value as T;
    if (T == double && value is double) return value as T;
    if (T == bool && value is bool) return value as T;
    
    // Try to decode JSON for complex types
    if (value is String) {
      try {
        return jsonDecode(value) as T;
      } catch (e) {
        return null;
      }
    }
    
    return null;
  }

  // Cleanup
  Future<void> clearOldData({int daysToKeep = 30}) async {
    final db = await database;
    final cutoff = DateTime.now().subtract(Duration(days: daysToKeep)).millisecondsSinceEpoch;
    
    await db.delete('chat_messages', where: 'timestamp < ? AND is_synced = 1', whereArgs: [cutoff]);
    await db.delete('pulse_data', where: 'timestamp < ? AND is_synced = 1', whereArgs: [cutoff]);
    await db.delete('retry_queue', where: 'retry_count >= max_retries AND created_at < ?', whereArgs: [cutoff]);
  }
}
