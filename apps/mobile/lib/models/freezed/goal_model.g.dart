// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'goal_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_GoalModel _$GoalModelFromJson(Map<String, dynamic> json) => _GoalModel(
      id: json['id'] as String,
      tenantId: json['tenantId'] as String,
      title: json['title'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      goalStatus:
          $enumDecodeNullable(_$GoalStatusEnumMap, json['goalStatus']) ??
              GoalStatus.draft,
      priority: $enumDecodeNullable(_$GoalPriorityEnumMap, json['priority']) ??
          GoalPriority.medium,
      status: json['status'] as String? ?? 'active',
      tags:
          (json['tags'] as List<dynamic>?)?.map((e) => e as String).toList() ??
              const [],
      description: json['description'] as String?,
      createdBy: json['createdBy'] as String?,
      dueDate: json['dueDate'] == null
          ? null
          : DateTime.parse(json['dueDate'] as String),
      completionDate: json['completionDate'] == null
          ? null
          : DateTime.parse(json['completionDate'] as String),
      progressPercentage: (json['progressPercentage'] as num?)?.toDouble(),
      teamId: json['teamId'] as String?,
      parentGoalId: json['parentGoalId'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$GoalModelToJson(_GoalModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'tenantId': instance.tenantId,
      'title': instance.title,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
      'goalStatus': _$GoalStatusEnumMap[instance.goalStatus]!,
      'priority': _$GoalPriorityEnumMap[instance.priority]!,
      'status': instance.status,
      'tags': instance.tags,
      'description': instance.description,
      'createdBy': instance.createdBy,
      'dueDate': instance.dueDate?.toIso8601String(),
      'completionDate': instance.completionDate?.toIso8601String(),
      'progressPercentage': instance.progressPercentage,
      'teamId': instance.teamId,
      'parentGoalId': instance.parentGoalId,
      'metadata': instance.metadata,
    };

const _$GoalStatusEnumMap = {
  GoalStatus.draft: 'draft',
  GoalStatus.active: 'active',
  GoalStatus.completed: 'completed',
  GoalStatus.archived: 'archived',
};

const _$GoalPriorityEnumMap = {
  GoalPriority.low: 'low',
  GoalPriority.medium: 'medium',
  GoalPriority.high: 'high',
  GoalPriority.critical: 'critical',
};
