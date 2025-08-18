// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_UserPreferences _$UserPreferencesFromJson(Map<String, dynamic> json) =>
    _UserPreferences(
      theme: json['theme'] as String? ?? 'auto',
      notifications: json['notifications'] as bool? ?? true,
      language: json['language'] as String? ?? 'en',
    );

Map<String, dynamic> _$UserPreferencesToJson(_UserPreferences instance) =>
    <String, dynamic>{
      'theme': instance.theme,
      'notifications': instance.notifications,
      'language': instance.language,
    };

_UserModel _$UserModelFromJson(Map<String, dynamic> json) => _UserModel(
      id: json['id'] as String,
      tenantId: json['tenantId'] as String,
      email: json['email'] as String,
      displayName: json['displayName'] as String,
      role: json['role'] as String,
      firebaseUid: json['firebaseUid'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      status: json['status'] as String? ?? 'active',
      createdBy: json['createdBy'] as String?,
      avatarUrl: json['avatarUrl'] as String?,
      lastLogin: json['lastLogin'] == null
          ? null
          : DateTime.parse(json['lastLogin'] as String),
      preferences: json['preferences'] == null
          ? null
          : UserPreferences.fromJson(
              json['preferences'] as Map<String, dynamic>),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$UserModelToJson(_UserModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'tenantId': instance.tenantId,
      'email': instance.email,
      'displayName': instance.displayName,
      'role': instance.role,
      'firebaseUid': instance.firebaseUid,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
      'status': instance.status,
      'createdBy': instance.createdBy,
      'avatarUrl': instance.avatarUrl,
      'lastLogin': instance.lastLogin?.toIso8601String(),
      'preferences': instance.preferences,
      'metadata': instance.metadata,
    };
