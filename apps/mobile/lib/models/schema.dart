/// Living Twin - Consistent Schema Models for Flutter/Dart
/// 
/// These models ensure consistency with Neo4j, Firestore, and Pub/Sub schemas
library;

// =========================
// Storage Keys
// =========================
class StorageKeys {
  static const String tenantData = 'tenant_data';
  static const String userData = 'user_data';
  static const String teamData = 'team_data';
  static const String goalData = 'goal_data';
  static const String documentData = 'document_data';
  static const String chunkData = 'chunk_data';
  static const String offlineQueue = 'offline_queue';
  static const String authToken = 'auth_token';
  static const String lastSync = 'last_sync';
}

// =========================
// Enums
// =========================
enum EntityStatus { active, inactive, archived, suspended }

enum UserRole { admin, member, viewer }

enum GoalStatus { draft, active, completed, archived }

enum GoalPriority { low, medium, high, critical }

enum ProcessingStatus { pending, processing, completed, failed }

enum TenantStatus { active, suspended, trial }

enum SubscriptionTier { free, pro, enterprise }

enum Theme { light, dark, auto }

// =========================
// Base Entity Model
// =========================
abstract class BaseEntity {
  final String id;
  final String tenantId;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? createdBy;
  final String status;
  final Map<String, dynamic>? metadata;

  BaseEntity({
    required this.id,
    required this.tenantId,
    required this.createdAt,
    required this.updatedAt,
    required this.status, this.createdBy,
    this.metadata,
  });

  Map<String, dynamic> toJson();
  
  static DateTime parseDateTime(value) {
    if (value is DateTime) return value;
    if (value is String) return DateTime.parse(value);
    throw ArgumentError('Invalid datetime value: $value');
  }
}

// =========================
// Tenant Settings Model
// =========================
class TenantSettings {
  final String embeddingModel;
  final int maxChunkSize;
  final int chunkOverlap;
  final List<String> allowedFileTypes;
  final int maxFileSizeMb;
  final int retentionDays;

  TenantSettings({
    required this.embeddingModel,
    required this.maxChunkSize,
    required this.chunkOverlap,
    required this.allowedFileTypes,
    required this.maxFileSizeMb,
    required this.retentionDays,
  });

  factory TenantSettings.fromJson(Map<String, dynamic> json) {
    return TenantSettings(
      embeddingModel: json['embedding_model'] ?? 'sentence-transformers',
      maxChunkSize: json['max_chunk_size'] ?? 1000,
      chunkOverlap: json['chunk_overlap'] ?? 200,
      allowedFileTypes: List<String>.from(json['allowed_file_types'] ?? ['pdf', 'docx', 'txt']),
      maxFileSizeMb: json['max_file_size_mb'] ?? 100,
      retentionDays: json['retention_days'] ?? 365,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'embedding_model': embeddingModel,
      'max_chunk_size': maxChunkSize,
      'chunk_overlap': chunkOverlap,
      'allowed_file_types': allowedFileTypes,
      'max_file_size_mb': maxFileSizeMb,
      'retention_days': retentionDays,
    };
  }
}

// =========================
// Tenant Model
// =========================
class TenantModel {
  final String id;
  final String displayName;
  final String domain;
  final TenantSettings settings;
  final DateTime createdAt;
  final DateTime updatedAt;
  final TenantStatus status;
  final SubscriptionTier? subscriptionTier;
  final String? billingEmail;
  final Map<String, dynamic>? metadata;

  TenantModel({
    required this.id,
    required this.displayName,
    required this.domain,
    required this.settings,
    required this.createdAt,
    required this.updatedAt,
    required this.status,
    this.subscriptionTier,
    this.billingEmail,
    this.metadata,
  });

  factory TenantModel.fromJson(Map<String, dynamic> json) {
    return TenantModel(
      id: json['id'],
      displayName: json['display_name'],
      domain: json['domain'],
      settings: TenantSettings.fromJson(json['settings'] ?? {}),
      createdAt: BaseEntity.parseDateTime(json['created_at']),
      updatedAt: BaseEntity.parseDateTime(json['updated_at']),
      status: TenantStatus.values.firstWhere(
        (e) => e.name == json['status'],
        orElse: () => TenantStatus.active,
      ),
      subscriptionTier: json['subscription_tier'] != null
          ? SubscriptionTier.values.firstWhere(
              (e) => e.name == json['subscription_tier'],
              orElse: () => SubscriptionTier.free,
            )
          : null,
      billingEmail: json['billing_email'],
      metadata: json['metadata'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'display_name': displayName,
      'domain': domain,
      'settings': settings.toJson(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'status': status.name,
      'subscription_tier': subscriptionTier?.name,
      'billing_email': billingEmail,
      'metadata': metadata,
    };
  }
}

// =========================
// User Preferences Model
// =========================
class UserPreferences {
  final Theme theme;
  final bool notifications;
  final String language;

  UserPreferences({
    required this.theme,
    required this.notifications,
    required this.language,
  });

  factory UserPreferences.fromJson(Map<String, dynamic> json) {
    return UserPreferences(
      theme: Theme.values.firstWhere(
        (e) => e.name == json['theme'],
        orElse: () => Theme.auto,
      ),
      notifications: json['notifications'] ?? true,
      language: json['language'] ?? 'en',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'theme': theme.name,
      'notifications': notifications,
      'language': language,
    };
  }
}

// =========================
// User Model
// =========================
class UserModel extends BaseEntity {
  final String email;
  final String displayName;
  final UserRole role;
  final String firebaseUid;
  final DateTime? lastLogin;
  final String? avatarUrl;
  final UserPreferences? preferences;

  UserModel({
    required super.id,
    required super.tenantId,
    required super.createdAt,
    required super.updatedAt,
    required super.status, required this.email, required this.displayName, required this.role, required this.firebaseUid, super.createdBy,
    super.metadata,
    this.lastLogin,
    this.avatarUrl,
    this.preferences,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      tenantId: json['tenant_id'],
      createdAt: BaseEntity.parseDateTime(json['created_at']),
      updatedAt: BaseEntity.parseDateTime(json['updated_at']),
      createdBy: json['created_by'],
      status: json['status'],
      metadata: json['metadata'],
      email: json['email'],
      displayName: json['display_name'],
      role: UserRole.values.firstWhere(
        (e) => e.name == json['role'],
        orElse: () => UserRole.member,
      ),
      firebaseUid: json['firebase_uid'],
      lastLogin: json['last_login'] != null
          ? BaseEntity.parseDateTime(json['last_login'])
          : null,
      avatarUrl: json['avatar_url'],
      preferences: json['preferences'] != null
          ? UserPreferences.fromJson(json['preferences'])
          : null,
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'tenant_id': tenantId,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'created_by': createdBy,
      'status': status,
      'metadata': metadata,
      'email': email,
      'display_name': displayName,
      'role': role.name,
      'firebase_uid': firebaseUid,
      'last_login': lastLogin?.toIso8601String(),
      'avatar_url': avatarUrl,
      'preferences': preferences?.toJson(),
    };
  }
}

// =========================
// Team Settings Model
// =========================
class TeamSettings {
  final String visibility;
  final bool autoAssignGoals;

  TeamSettings({
    required this.visibility,
    required this.autoAssignGoals,
  });

  factory TeamSettings.fromJson(Map<String, dynamic> json) {
    return TeamSettings(
      visibility: json['visibility'] ?? 'public',
      autoAssignGoals: json['auto_assign_goals'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'visibility': visibility,
      'auto_assign_goals': autoAssignGoals,
    };
  }
}

// =========================
// Team Model
// =========================
class TeamModel extends BaseEntity {
  final String displayName;
  final String? description;
  final String? color;
  final int? memberCount;
  final TeamSettings? settings;

  TeamModel({
    required super.id,
    required super.tenantId,
    required super.createdAt,
    required super.updatedAt,
    required super.status, required this.displayName, super.createdBy,
    super.metadata,
    this.description,
    this.color,
    this.memberCount,
    this.settings,
  });

  factory TeamModel.fromJson(Map<String, dynamic> json) {
    return TeamModel(
      id: json['id'],
      tenantId: json['tenant_id'],
      createdAt: BaseEntity.parseDateTime(json['created_at']),
      updatedAt: BaseEntity.parseDateTime(json['updated_at']),
      createdBy: json['created_by'],
      status: json['status'],
      metadata: json['metadata'],
      displayName: json['display_name'],
      description: json['description'],
      color: json['color'],
      memberCount: json['member_count'],
      settings: json['settings'] != null
          ? TeamSettings.fromJson(json['settings'])
          : null,
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'tenant_id': tenantId,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'created_by': createdBy,
      'status': status,
      'metadata': metadata,
      'display_name': displayName,
      'description': description,
      'color': color,
      'member_count': memberCount,
      'settings': settings?.toJson(),
    };
  }
}

// =========================
// Goal Model
// =========================
class GoalModel extends BaseEntity {
  final String title;
  final String? description;
  final GoalStatus goalStatus;
  final GoalPriority priority;
  final DateTime? dueDate;
  final DateTime? completionDate;
  final double? progressPercentage;
  final List<String>? tags;
  final String? teamId;
  final String? parentGoalId;

  GoalModel({
    required super.id,
    required super.tenantId,
    required super.createdAt,
    required super.updatedAt,
    required super.status, required this.title, required this.goalStatus, required this.priority, super.createdBy,
    super.metadata,
    this.description,
    this.dueDate,
    this.completionDate,
    this.progressPercentage,
    this.tags,
    this.teamId,
    this.parentGoalId,
  });

  factory GoalModel.fromJson(Map<String, dynamic> json) {
    return GoalModel(
      id: json['id'],
      tenantId: json['tenant_id'],
      createdAt: BaseEntity.parseDateTime(json['created_at']),
      updatedAt: BaseEntity.parseDateTime(json['updated_at']),
      createdBy: json['created_by'],
      status: json['status'],
      metadata: json['metadata'],
      title: json['title'],
      description: json['description'],
      goalStatus: GoalStatus.values.firstWhere(
        (e) => e.name == json['status'],
        orElse: () => GoalStatus.draft,
      ),
      priority: GoalPriority.values.firstWhere(
        (e) => e.name == json['priority'],
        orElse: () => GoalPriority.medium,
      ),
      dueDate: json['due_date'] != null
          ? BaseEntity.parseDateTime(json['due_date'])
          : null,
      completionDate: json['completion_date'] != null
          ? BaseEntity.parseDateTime(json['completion_date'])
          : null,
      progressPercentage: json['progress_percentage']?.toDouble(),
      tags: json['tags'] != null ? List<String>.from(json['tags']) : null,
      teamId: json['team_id'],
      parentGoalId: json['parent_goal_id'],
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'tenant_id': tenantId,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'created_by': createdBy,
      'status': status,
      'metadata': metadata,
      'title': title,
      'description': description,
      'goal_status': goalStatus.name,
      'priority': priority.name,
      'due_date': dueDate?.toIso8601String(),
      'completion_date': completionDate?.toIso8601String(),
      'progress_percentage': progressPercentage,
      'tags': tags,
      'team_id': teamId,
      'parent_goal_id': parentGoalId,
    };
  }
}

// =========================
// Document Model
// =========================
class DocumentModel extends BaseEntity {
  final String title;
  final String fileName;
  final String fileType;
  final int fileSize;
  final String? gcsPath;
  final int? pageCount;
  final int? chunkCount;
  final ProcessingStatus processingStatus;
  final String? processingError;
  final List<String>? tags;
  final List<String>? relatedGoalIds;

  DocumentModel({
    required super.id,
    required super.tenantId,
    required super.createdAt,
    required super.updatedAt,
    required super.status, required this.title, required this.fileName, required this.fileType, required this.fileSize, required this.processingStatus, super.createdBy,
    super.metadata,
    this.gcsPath,
    this.pageCount,
    this.chunkCount,
    this.processingError,
    this.tags,
    this.relatedGoalIds,
  });

  factory DocumentModel.fromJson(Map<String, dynamic> json) {
    return DocumentModel(
      id: json['id'],
      tenantId: json['tenant_id'],
      createdAt: BaseEntity.parseDateTime(json['created_at']),
      updatedAt: BaseEntity.parseDateTime(json['updated_at']),
      createdBy: json['created_by'],
      status: json['status'],
      metadata: json['metadata'],
      title: json['title'],
      fileName: json['file_name'],
      fileType: json['file_type'],
      fileSize: json['file_size'],
      gcsPath: json['gcs_path'],
      pageCount: json['page_count'],
      chunkCount: json['chunk_count'],
      processingStatus: ProcessingStatus.values.firstWhere(
        (e) => e.name == json['processing_status'],
        orElse: () => ProcessingStatus.pending,
      ),
      processingError: json['processing_error'],
      tags: json['tags'] != null ? List<String>.from(json['tags']) : null,
      relatedGoalIds: json['related_goal_ids'] != null
          ? List<String>.from(json['related_goal_ids'])
          : null,
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'tenant_id': tenantId,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'created_by': createdBy,
      'status': status,
      'metadata': metadata,
      'title': title,
      'file_name': fileName,
      'file_type': fileType,
      'file_size': fileSize,
      'gcs_path': gcsPath,
      'page_count': pageCount,
      'chunk_count': chunkCount,
      'processing_status': processingStatus.name,
      'processing_error': processingError,
      'tags': tags,
      'related_goal_ids': relatedGoalIds,
    };
  }
}

// =========================
// Chunk Model
// =========================
class ChunkModel extends BaseEntity {
  final String documentId;
  final String content;
  final int position;
  final int? pageNumber;
  final int startChar;
  final int endChar;
  final int tokenCount;
  final double? similarityScore;

  ChunkModel({
    required super.id,
    required super.tenantId,
    required super.createdAt,
    required super.updatedAt,
    required super.status, required this.documentId, required this.content, required this.position, required this.startChar, required this.endChar, required this.tokenCount, super.createdBy,
    super.metadata,
    this.pageNumber,
    this.similarityScore,
  });

  factory ChunkModel.fromJson(Map<String, dynamic> json) {
    return ChunkModel(
      id: json['id'],
      tenantId: json['tenant_id'],
      createdAt: BaseEntity.parseDateTime(json['created_at']),
      updatedAt: BaseEntity.parseDateTime(json['updated_at']),
      createdBy: json['created_by'],
      status: json['status'],
      metadata: json['metadata'],
      documentId: json['document_id'],
      content: json['content'],
      position: json['position'],
      pageNumber: json['page_number'],
      startChar: json['start_char'],
      endChar: json['end_char'],
      tokenCount: json['token_count'],
      similarityScore: json['similarity_score']?.toDouble(),
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'tenant_id': tenantId,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'created_by': createdBy,
      'status': status,
      'metadata': metadata,
      'document_id': documentId,
      'content': content,
      'position': position,
      'page_number': pageNumber,
      'start_char': startChar,
      'end_char': endChar,
      'token_count': tokenCount,
      'similarity_score': similarityScore,
    };
  }
}

// =========================
// API Response Models
// =========================
class ApiResponse<T> {
  final bool success;
  final T? data;
  final String? error;
  final String? message;
  final DateTime timestamp;

  ApiResponse({
    required this.success,
    required this.timestamp, this.data,
    this.error,
    this.message,
  });

  factory ApiResponse.fromJson(
    Map<String, dynamic> json,
    T Function()? fromJsonT,
  ) {
    return ApiResponse<T>(
      success: json['success'] ?? false,
      data: json['data'] != null && fromJsonT != null
          ? fromJsonT(json['data'])
          : json['data'],
      error: json['error'],
      message: json['message'],
      timestamp: BaseEntity.parseDateTime(json['timestamp']),
    );
  }
}

class PaginationInfo {
  final int page;
  final int limit;
  final int total;
  final bool hasNext;
  final bool hasPrev;

  PaginationInfo({
    required this.page,
    required this.limit,
    required this.total,
    required this.hasNext,
    required this.hasPrev,
  });

  factory PaginationInfo.fromJson(Map<String, dynamic> json) {
    return PaginationInfo(
      page: json['page'],
      limit: json['limit'],
      total: json['total'],
      hasNext: json['has_next'],
      hasPrev: json['has_prev'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'page': page,
      'limit': limit,
      'total': total,
      'has_next': hasNext,
      'has_prev': hasPrev,
    };
  }
}

class PaginatedResponse<T> {
  final bool success;
  final List<T>? data;
  final String? error;
  final String? message;
  final DateTime timestamp;
  final PaginationInfo pagination;

  PaginatedResponse({
    required this.success,
    required this.timestamp, required this.pagination, this.data,
    this.error,
    this.message,
  });

  factory PaginatedResponse.fromJson(
    Map<String, dynamic> json,
    T Function() fromJsonT,
  ) {
    return PaginatedResponse<T>(
      success: json['success'] ?? false,
      data: json['data'] != null
          ? (json['data'] as List).map((item) => fromJsonT(item)).toList()
          : null,
      error: json['error'],
      message: json['message'],
      timestamp: BaseEntity.parseDateTime(json['timestamp']),
      pagination: PaginationInfo.fromJson(json['pagination']),
    );
  }
}

// =========================
// Search Models
// =========================
class SearchFilters {
  final List<String>? documentTypes;
  final DateRange? dateRange;
  final List<String>? goalIds;
  final List<String>? tags;

  SearchFilters({
    this.documentTypes,
    this.dateRange,
    this.goalIds,
    this.tags,
  });

  factory SearchFilters.fromJson(Map<String, dynamic> json) {
    return SearchFilters(
      documentTypes: json['document_types'] != null
          ? List<String>.from(json['document_types'])
          : null,
      dateRange: json['date_range'] != null
          ? DateRange.fromJson(json['date_range'])
          : null,
      goalIds: json['goal_ids'] != null
          ? List<String>.from(json['goal_ids'])
          : null,
      tags: json['tags'] != null ? List<String>.from(json['tags']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'document_types': documentTypes,
      'date_range': dateRange?.toJson(),
      'goal_ids': goalIds,
      'tags': tags,
    };
  }
}

class DateRange {
  final DateTime start;
  final DateTime end;

  DateRange({
    required this.start,
    required this.end,
  });

  factory DateRange.fromJson(Map<String, dynamic> json) {
    return DateRange(
      start: BaseEntity.parseDateTime(json['start']),
      end: BaseEntity.parseDateTime(json['end']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'start': start.toIso8601String(),
      'end': end.toIso8601String(),
    };
  }
}

class SearchRequest {
  final String query;
  final String tenantId;
  final SearchFilters? filters;
  final int? limit;
  final int? offset;

  SearchRequest({
    required this.query,
    required this.tenantId,
    this.filters,
    this.limit,
    this.offset,
  });

  factory SearchRequest.fromJson(Map<String, dynamic> json) {
    return SearchRequest(
      query: json['query'],
      tenantId: json['tenant_id'],
      filters: json['filters'] != null
          ? SearchFilters.fromJson(json['filters'])
          : null,
      limit: json['limit'],
      offset: json['offset'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'query': query,
      'tenant_id': tenantId,
      'filters': filters?.toJson(),
      'limit': limit,
      'offset': offset,
    };
  }
}

class SearchResult {
  final ChunkModel chunk;
  final DocumentModel document;
  final double similarityScore;
  final String? highlightedContent;

  SearchResult({
    required this.chunk,
    required this.document,
    required this.similarityScore,
    this.highlightedContent,
  });

  factory SearchResult.fromJson(Map<String, dynamic> json) {
    return SearchResult(
      chunk: ChunkModel.fromJson(json['chunk']),
      document: DocumentModel.fromJson(json['document']),
      similarityScore: json['similarity_score'].toDouble(),
      highlightedContent: json['highlighted_content'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'chunk': chunk.toJson(),
      'document': document.toJson(),
      'similarity_score': similarityScore,
      'highlighted_content': highlightedContent,
    };
  }
}

class SearchResponse {
  final bool success;
  final List<SearchResult>? data;
  final String? error;
  final String? message;
  final DateTime timestamp;
  final String query;
  final int totalResults;
  final int processingTimeMs;

  SearchResponse({
    required this.success,
    required this.timestamp, required this.query, required this.totalResults, required this.processingTimeMs, this.data,
    this.error,
    this.message,
  });

  factory SearchResponse.fromJson(Map<String, dynamic> json) {
    return SearchResponse(
      success: json['success'] ?? false,
      data: json['data'] != null
          ? (json['data'] as List)
              .map((item) => SearchResult.fromJson(item))
              .toList()
          : null,
      error: json['error'],
      message: json['message'],
      timestamp: BaseEntity.parseDateTime(json['timestamp']),
      query: json['query'],
      totalResults: json['total_results'],
      processingTimeMs: json['processing_time_ms'],
    );
  }
}

// =========================
// Pub/Sub Message Models
// =========================
class PubSubMessageMetadata {
  final String source;
  final String version;
  final String? userId;

  PubSubMessageMetadata({
    required this.source,
    required this.version,
    this.userId,
  });

  factory PubSubMessageMetadata.fromJson(Map<String, dynamic> json) {
    return PubSubMessageMetadata(
      source: json['source'],
      version: json['version'],
      userId: json['user_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'source': source,
      'version': version,
      'user_id': userId,
    };
  }
}

class PubSubMessage<T> {
  final String eventType;
  final String tenantId;
  final String? entityId;
  final DateTime timestamp;
  final String correlationId;
  final T data;
  final PubSubMessageMetadata metadata;

  PubSubMessage({
    required this.eventType,
    required this.tenantId,
    required this.timestamp, required this.correlationId, required this.data, required this.metadata, this.entityId,
  });

  factory PubSubMessage.fromJson(
    Map<String, dynamic> json,
    T Function() fromJsonT,
  ) {
    return PubSubMessage<T>(
      eventType: json['event_type'],
      tenantId: json['tenant_id'],
      entityId: json['entity_id'],
      timestamp: BaseEntity.parseDateTime(json['timestamp']),
      correlationId: json['correlation_id'],
      data: fromJsonT(json['data']),
      metadata: PubSubMessageMetadata.fromJson(json['metadata']),
    );
  }

  Map<String, dynamic> toJson(Map<String, dynamic> Function(T) toJsonT) {
    return {
      'event_type': eventType,
      'tenant_id': tenantId,
      'entity_id': entityId,
      'timestamp': timestamp.toIso8601String(),
      'correlation_id': correlationId,
      'data': toJsonT(data),
      'metadata': metadata.toJson(),
    };
  }
}

// =========================
// Form Models
// =========================
class CreateTenantForm {
  final String displayName;
  final String domain;
  final String billingEmail;
  final SubscriptionTier subscriptionTier;

  CreateTenantForm({
    required this.displayName,
    required this.domain,
    required this.billingEmail,
    required this.subscriptionTier,
  });

  Map<String, dynamic> toJson() {
    return {
      'display_name': displayName,
      'domain': domain,
      'billing_email': billingEmail,
      'subscription_tier': subscriptionTier.name,
    };
  }
}

class CreateUserForm {
  final String email;
  final String displayName;
  final UserRole role;
  final bool sendInvite;

  CreateUserForm({
    required this.email,
    required this.displayName,
    required this.role,
    required this.sendInvite,
  });

  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'display_name': displayName,
      'role': role.name,
      'send_invite': sendInvite,
    };
  }
}

class CreateGoalForm {
  final String title;
  final String? description;
  final GoalPriority priority;
  final DateTime? dueDate;
  final String? teamId;
  final String? parentGoalId;
  final List<String>? tags;

  CreateGoalForm({
    required this.title,
    required this.priority, this.description,
    this.dueDate,
    this.teamId,
    this.parentGoalId,
    this.tags,
  });

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'description': description,
      'priority': priority.name,
      'due_date': dueDate?.toIso8601String(),
      'team_id': teamId,
      'parent_goal_id': parentGoalId,
      'tags': tags,
    };
  }
}

// =========================
// Validation Patterns
// =========================
class ValidationPatterns {
  static final RegExp tenantId = RegExp(r'^tenant-[a-z0-9]{6,12}$');
  static final RegExp userId = RegExp(r'^user-[a-z0-9]{6,12}$');
  static final RegExp teamId = RegExp(r'^team-[a-z0-9]{6,12}$');
  static final RegExp goalId = RegExp(r'^goal-[a-z0-9-]{6,50}$');
  static final RegExp documentId = RegExp(r'^doc-[a-z0-9-]{6,50}$');
  static final RegExp chunkId = RegExp(r'^chunk-[a-z0-9-]{6,50}$');
  static final RegExp email = RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$');
  static final RegExp domain = RegExp(r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$');
}

class ValidationRules {
  static const int displayNameMinLength = 2;
  static const int displayNameMaxLength = 100;
  static const int descriptionMaxLength = 1000;
  static const int maxFileSizeMb = 100;
}

// =========================
// Utility Extensions
// =========================
extension EntityStatusExtension on EntityStatus {
  String get displayName {
    switch (this) {
      case EntityStatus.active:
        return 'Active';
      case EntityStatus.inactive:
        return 'Inactive';
      case EntityStatus.archived:
        return 'Archived';
      case EntityStatus.suspended:
        return 'Suspended';
    }
  }
}

extension UserRoleExtension on UserRole {
  String get displayName {
    switch (this) {
      case UserRole.admin:
        return 'Administrator';
      case UserRole.member:
        return 'Member';
      case UserRole.viewer:
        return 'Viewer';
    }
  }
}

extension GoalStatusExtension on GoalStatus {
  String get displayName {
    switch (this) {
      case GoalStatus.draft:
        return 'Draft';
      case GoalStatus.active:
        return 'Active';
      case GoalStatus.completed:
        return 'Completed';
      case GoalStatus.archived:
        return 'Archived';
    }
  }
}

extension GoalPriorityExtension on GoalPriority {
  String get displayName {
    switch (this) {
      case GoalPriority.low:
        return 'Low';
      case GoalPriority.medium:
        return 'Medium';
      case GoalPriority.high:
        return 'High';
      case GoalPriority.critical:
        return 'Critical';
    }
  }
}

extension ProcessingStatusExtension on ProcessingStatus {
  String get displayName {
    switch (this) {
      case ProcessingStatus.pending:
        return 'Pending';
      case ProcessingStatus.processing:
        return 'Processing';
      case ProcessingStatus.completed:
        return 'Completed';
      case ProcessingStatus.failed:
        return 'Failed';
    }
  }
}
