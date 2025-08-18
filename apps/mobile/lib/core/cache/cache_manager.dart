import 'dart:convert';
import 'package:injectable/injectable.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'dart:async';

/// Cache entry model
class CacheEntry<T> {
  final String key;
  final T data;
  final DateTime createdAt;
  final Duration? ttl;
  
  CacheEntry({
    required this.key,
    required this.data,
    DateTime? createdAt,
    this.ttl,
  }) : createdAt = createdAt ?? DateTime.now();
  
  /// Check if cache entry is expired
  bool get isExpired {
    if (ttl == null) return false;
    return DateTime.now().difference(createdAt) > ttl!;
  }
  
  /// Check if cache entry is valid
  bool get isValid => !isExpired;
  
  /// Convert to JSON
  Map<String, dynamic> toJson() => {
    'key': key,
    'data': data is String ? data : jsonEncode(data),
    'createdAt': createdAt.toIso8601String(),
    'ttl': ttl?.inSeconds,
  };
  
  /// Create from JSON
  factory CacheEntry.fromJson(Map<String, dynamic> json) {
    return CacheEntry<T>(
      key: json['key'] as String,
      data: json['data'] as T,
      createdAt: DateTime.parse(json['createdAt'] as String),
      ttl: json['ttl'] != null 
        ? Duration(seconds: json['ttl'] as int)
        : null,
    );
  }
}

/// Cache manager with multiple storage strategies
@singleton
class CacheManager {
  final SharedPreferences _prefs;
  Database? _database;
  final Map<String, CacheEntry> _memoryCache = {};
  Timer? _cleanupTimer;
  
  // Cache configuration
  static const int maxMemoryCacheSize = 100;
  static const Duration defaultTTL = Duration(hours: 1);
  static const Duration cleanupInterval = Duration(minutes: 5);
  
  CacheManager(this._prefs) {
    _initDatabase();
    _startCleanupTimer();
  }
  
  /// Initialize SQLite database for persistent cache
  Future<void> _initDatabase() async {
    final databasesPath = await getDatabasesPath();
    final path = join(databasesPath, 'cache.db');
    
    _database = await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) {
        return db.execute(
          '''
          CREATE TABLE cache(
            key TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            ttl_seconds INTEGER,
            size INTEGER
          )
          ''',
        );
      },
    );
  }
  
  /// Start periodic cleanup of expired cache entries
  void _startCleanupTimer() {
    _cleanupTimer = Timer.periodic(cleanupInterval, (_) {
      cleanupExpired();
    });
  }
  
  // Memory Cache Operations
  
  /// Get from memory cache
  T? getFromMemory<T>(String key) {
    final entry = _memoryCache[key];
    if (entry != null && entry.isValid) {
      return entry.data as T?;
    }
    _memoryCache.remove(key);
    return null;
  }
  
  /// Save to memory cache
  void saveToMemory<T>(
    String key,
    T data, {
    Duration? ttl,
  }) {
    // Implement LRU eviction if cache is full
    if (_memoryCache.length >= maxMemoryCacheSize) {
      _evictOldestMemoryEntry();
    }
    
    _memoryCache[key] = CacheEntry<T>(
      key: key,
      data: data,
      ttl: ttl ?? defaultTTL,
    );
  }
  
  /// Evict oldest memory cache entry
  void _evictOldestMemoryEntry() {
    if (_memoryCache.isEmpty) return;
    
    String? oldestKey;
    DateTime? oldestTime;
    
    for (final entry in _memoryCache.entries) {
      final createdAt = (entry.value as CacheEntry).createdAt;
      if (oldestTime == null || createdAt.isBefore(oldestTime)) {
        oldestTime = createdAt;
        oldestKey = entry.key;
      }
    }
    
    if (oldestKey != null) {
      _memoryCache.remove(oldestKey);
    }
  }
  
  // SharedPreferences Cache Operations
  
  /// Get from SharedPreferences cache
  T? getFromPrefs<T>(String key) {
    final cacheKey = 'cache_$key';
    final metaKey = 'cache_meta_$key';
    
    final data = _prefs.getString(cacheKey);
    final metaJson = _prefs.getString(metaKey);
    
    if (data == null || metaJson == null) return null;
    
    final meta = jsonDecode(metaJson) as Map<String, dynamic>;
    final createdAt = DateTime.parse(meta['createdAt'] as String);
    final ttlSeconds = meta['ttl'] as int?;
    
    if (ttlSeconds != null) {
      final ttl = Duration(seconds: ttlSeconds);
      if (DateTime.now().difference(createdAt) > ttl) {
        // Cache expired
        _prefs.remove(cacheKey);
        _prefs.remove(metaKey);
        return null;
      }
    }
    
    try {
      if (T == String) {
        return data as T;
      } else {
        return jsonDecode(data) as T;
      }
    } catch (e) {
      return null;
    }
  }
  
  /// Save to SharedPreferences cache
  Future<bool> saveToPrefs<T>(
    String key,
    T data, {
    Duration? ttl,
  }) async {
    final cacheKey = 'cache_$key';
    final metaKey = 'cache_meta_$key';
    
    final dataString = data is String ? data : jsonEncode(data);
    final meta = {
      'createdAt': DateTime.now().toIso8601String(),
      'ttl': (ttl ?? defaultTTL).inSeconds,
    };
    
    final saved = await _prefs.setString(cacheKey, dataString);
    final metaSaved = await _prefs.setString(metaKey, jsonEncode(meta));
    
    return saved && metaSaved;
  }
  
  // Database Cache Operations
  
  /// Get from database cache
  Future<T?> getFromDatabase<T>(String key) async {
    if (_database == null) return null;
    
    final List<Map<String, dynamic>> maps = await _database!.query(
      'cache',
      where: 'key = ?',
      whereArgs: [key],
    );
    
    if (maps.isEmpty) return null;
    
    final row = maps.first;
    final createdAt = DateTime.fromMillisecondsSinceEpoch(
      row['created_at'] as int,
    );
    final ttlSeconds = row['ttl_seconds'] as int?;
    
    if (ttlSeconds != null) {
      final ttl = Duration(seconds: ttlSeconds);
      if (DateTime.now().difference(createdAt) > ttl) {
        // Cache expired
        await _database!.delete(
          'cache',
          where: 'key = ?',
          whereArgs: [key],
        );
        return null;
      }
    }
    
    final data = row['data'] as String;
    
    try {
      if (T == String) {
        return data as T;
      } else {
        return jsonDecode(data) as T;
      }
    } catch (e) {
      return null;
    }
  }
  
  /// Save to database cache
  Future<bool> saveToDatabase<T>(
    String key,
    T data, {
    Duration? ttl,
  }) async {
    if (_database == null) return false;
    
    final dataString = data is String ? data : jsonEncode(data);
    
    try {
      await _database!.insert(
        'cache',
        {
          'key': key,
          'data': dataString,
          'created_at': DateTime.now().millisecondsSinceEpoch,
          'ttl_seconds': (ttl ?? defaultTTL).inSeconds,
          'size': dataString.length,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
      return true;
    } catch (e) {
      return false;
    }
  }
  
  // Unified Cache Operations
  
  /// Get from cache (checks all levels)
  Future<T?> get<T>(
    String key, {
    CacheLevel level = CacheLevel.all,
  }) async {
    // Check memory cache first (fastest)
    if (level == CacheLevel.all || level == CacheLevel.memory) {
      final memoryData = getFromMemory<T>(key);
      if (memoryData != null) return memoryData;
    }
    
    // Check SharedPreferences cache (medium speed)
    if (level == CacheLevel.all || level == CacheLevel.prefs) {
      final prefsData = getFromPrefs<T>(key);
      if (prefsData != null) {
        // Promote to memory cache for faster access
        saveToMemory(key, prefsData);
        return prefsData;
      }
    }
    
    // Check database cache (slowest but most persistent)
    if (level == CacheLevel.all || level == CacheLevel.database) {
      final dbData = await getFromDatabase<T>(key);
      if (dbData != null) {
        // Promote to memory cache for faster access
        saveToMemory(key, dbData);
        return dbData;
      }
    }
    
    return null;
  }
  
  /// Save to cache
  Future<bool> save<T>(
    String key,
    T data, {
    Duration? ttl,
    CacheLevel level = CacheLevel.all,
  }) async {
    bool success = true;
    
    // Save to memory cache
    if (level == CacheLevel.all || level == CacheLevel.memory) {
      saveToMemory(key, data, ttl: ttl);
    }
    
    // Save to SharedPreferences cache
    if (level == CacheLevel.all || level == CacheLevel.prefs) {
      success = success && await saveToPrefs(key, data, ttl: ttl);
    }
    
    // Save to database cache
    if (level == CacheLevel.all || level == CacheLevel.database) {
      success = success && await saveToDatabase(key, data, ttl: ttl);
    }
    
    return success;
  }
  
  /// Delete from cache
  Future<bool> delete(String key) async {
    // Remove from memory cache
    _memoryCache.remove(key);
    
    // Remove from SharedPreferences
    final cacheKey = 'cache_$key';
    final metaKey = 'cache_meta_$key';
    await _prefs.remove(cacheKey);
    await _prefs.remove(metaKey);
    
    // Remove from database
    if (_database != null) {
      await _database!.delete(
        'cache',
        where: 'key = ?',
        whereArgs: [key],
      );
    }
    
    return true;
  }
  
  /// Clear all cache
  Future<void> clearAll() async {
    // Clear memory cache
    _memoryCache.clear();
    
    // Clear SharedPreferences cache
    final keys = _prefs.getKeys();
    for (final key in keys) {
      if (key.startsWith('cache_')) {
        await _prefs.remove(key);
      }
    }
    
    // Clear database cache
    if (_database != null) {
      await _database!.delete('cache');
    }
  }
  
  /// Clean up expired cache entries
  Future<void> cleanupExpired() async {
    // Cleanup memory cache
    _memoryCache.removeWhere((key, entry) => entry.isExpired);
    
    // Cleanup SharedPreferences cache
    final keys = _prefs.getKeys();
    for (final key in keys) {
      if (key.startsWith('cache_') && !key.contains('meta')) {
        final cacheKey = key.substring(6); // Remove 'cache_' prefix
        final data = getFromPrefs<dynamic>(cacheKey);
        // If null, it means it's expired and already removed
      }
    }
    
    // Cleanup database cache
    if (_database != null) {
      final now = DateTime.now().millisecondsSinceEpoch;
      await _database!.rawDelete(
        'DELETE FROM cache WHERE created_at + (ttl_seconds * 1000) < ?',
        [now],
      );
    }
  }
  
  /// Get cache statistics
  Future<CacheStats> getStats() async {
    final memoryCacheSize = _memoryCache.length;
    
    int prefsCacheSize = 0;
    final keys = _prefs.getKeys();
    for (final key in keys) {
      if (key.startsWith('cache_') && !key.contains('meta')) {
        prefsCacheSize++;
      }
    }
    
    int dbCacheSize = 0;
    int dbCacheSizeBytes = 0;
    if (_database != null) {
      final result = await _database!.rawQuery(
        'SELECT COUNT(*) as count, SUM(size) as total_size FROM cache',
      );
      dbCacheSize = result.first['count'] as int? ?? 0;
      dbCacheSizeBytes = result.first['total_size'] as int? ?? 0;
    }
    
    return CacheStats(
      memoryCacheEntries: memoryCacheSize,
      prefsCacheEntries: prefsCacheSize,
      databaseCacheEntries: dbCacheSize,
      databaseCacheSizeBytes: dbCacheSizeBytes,
    );
  }
  
  /// Dispose resources
  void dispose() {
    _cleanupTimer?.cancel();
    _database?.close();
    _memoryCache.clear();
  }
}

/// Cache levels
enum CacheLevel {
  memory,    // In-memory cache only
  prefs,     // SharedPreferences cache only
  database,  // SQLite database cache only
  all,       // All cache levels
}

/// Cache statistics
class CacheStats {
  final int memoryCacheEntries;
  final int prefsCacheEntries;
  final int databaseCacheEntries;
  final int databaseCacheSizeBytes;
  
  const CacheStats({
    required this.memoryCacheEntries,
    required this.prefsCacheEntries,
    required this.databaseCacheEntries,
    required this.databaseCacheSizeBytes,
  });
  
  int get totalEntries => 
    memoryCacheEntries + prefsCacheEntries + databaseCacheEntries;
  
  String get formattedSize {
    final kb = databaseCacheSizeBytes / 1024;
    if (kb < 1024) {
      return '${kb.toStringAsFixed(2)} KB';
    }
    final mb = kb / 1024;
    return '${mb.toStringAsFixed(2)} MB';
  }
}

/// Mixin for widgets that need caching
mixin CacheMixin<T extends StatefulWidget> on State<T> {
  CacheManager? _cacheManager;
  
  CacheManager get cacheManager {
    _cacheManager ??= GetIt.instance<CacheManager>();
    return _cacheManager!;
  }
  
  /// Cache an API response
  Future<void> cacheResponse(
    String key,
    dynamic data, {
    Duration? ttl,
  }) async {
    await cacheManager.save(key, data, ttl: ttl);
  }
  
  /// Get cached response
  Future<T?> getCachedResponse<T>(String key) async {
    return await cacheManager.get<T>(key);
  }
  
  /// Cache or fetch data
  Future<T> cacheOrFetch<T>({
    required String key,
    required Future<T> Function() fetcher,
    Duration? ttl,
  }) async {
    // Try to get from cache first
    final cached = await getCachedResponse<T>(key);
    if (cached != null) {
      return cached;
    }
    
    // Fetch fresh data
    final data = await fetcher();
    
    // Cache the result
    await cacheResponse(key, data, ttl: ttl);
    
    return data;
  }
}
