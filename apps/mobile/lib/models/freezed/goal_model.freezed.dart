// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'goal_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$GoalModel {
  String get id;
  String get tenantId;
  String get title;
  DateTime get createdAt;
  DateTime get updatedAt;
  GoalStatus get goalStatus;
  GoalPriority get priority;
  String get status;
  List<String> get tags;
  String? get description;
  String? get createdBy;
  DateTime? get dueDate;
  DateTime? get completionDate;
  double? get progressPercentage;
  String? get teamId;
  String? get parentGoalId;
  Map<String, dynamic>? get metadata;

  /// Create a copy of GoalModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $GoalModelCopyWith<GoalModel> get copyWith =>
      _$GoalModelCopyWithImpl<GoalModel>(this as GoalModel, _$identity);

  /// Serializes this GoalModel to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is GoalModel &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.tenantId, tenantId) ||
                other.tenantId == tenantId) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt) &&
            (identical(other.goalStatus, goalStatus) ||
                other.goalStatus == goalStatus) &&
            (identical(other.priority, priority) ||
                other.priority == priority) &&
            (identical(other.status, status) || other.status == status) &&
            const DeepCollectionEquality().equals(other.tags, tags) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.createdBy, createdBy) ||
                other.createdBy == createdBy) &&
            (identical(other.dueDate, dueDate) || other.dueDate == dueDate) &&
            (identical(other.completionDate, completionDate) ||
                other.completionDate == completionDate) &&
            (identical(other.progressPercentage, progressPercentage) ||
                other.progressPercentage == progressPercentage) &&
            (identical(other.teamId, teamId) || other.teamId == teamId) &&
            (identical(other.parentGoalId, parentGoalId) ||
                other.parentGoalId == parentGoalId) &&
            const DeepCollectionEquality().equals(other.metadata, metadata));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      tenantId,
      title,
      createdAt,
      updatedAt,
      goalStatus,
      priority,
      status,
      const DeepCollectionEquality().hash(tags),
      description,
      createdBy,
      dueDate,
      completionDate,
      progressPercentage,
      teamId,
      parentGoalId,
      const DeepCollectionEquality().hash(metadata));

  @override
  String toString() {
    return 'GoalModel(id: $id, tenantId: $tenantId, title: $title, createdAt: $createdAt, updatedAt: $updatedAt, goalStatus: $goalStatus, priority: $priority, status: $status, tags: $tags, description: $description, createdBy: $createdBy, dueDate: $dueDate, completionDate: $completionDate, progressPercentage: $progressPercentage, teamId: $teamId, parentGoalId: $parentGoalId, metadata: $metadata)';
  }
}

/// @nodoc
abstract mixin class $GoalModelCopyWith<$Res> {
  factory $GoalModelCopyWith(GoalModel value, $Res Function(GoalModel) _then) =
      _$GoalModelCopyWithImpl;
  @useResult
  $Res call(
      {String id,
      String tenantId,
      String title,
      DateTime createdAt,
      DateTime updatedAt,
      GoalStatus goalStatus,
      GoalPriority priority,
      String status,
      List<String> tags,
      String? description,
      String? createdBy,
      DateTime? dueDate,
      DateTime? completionDate,
      double? progressPercentage,
      String? teamId,
      String? parentGoalId,
      Map<String, dynamic>? metadata});
}

/// @nodoc
class _$GoalModelCopyWithImpl<$Res> implements $GoalModelCopyWith<$Res> {
  _$GoalModelCopyWithImpl(this._self, this._then);

  final GoalModel _self;
  final $Res Function(GoalModel) _then;

  /// Create a copy of GoalModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? tenantId = null,
    Object? title = null,
    Object? createdAt = null,
    Object? updatedAt = null,
    Object? goalStatus = null,
    Object? priority = null,
    Object? status = null,
    Object? tags = null,
    Object? description = freezed,
    Object? createdBy = freezed,
    Object? dueDate = freezed,
    Object? completionDate = freezed,
    Object? progressPercentage = freezed,
    Object? teamId = freezed,
    Object? parentGoalId = freezed,
    Object? metadata = freezed,
  }) {
    return _then(_self.copyWith(
      id: null == id
          ? _self.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      tenantId: null == tenantId
          ? _self.tenantId
          : tenantId // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _self.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _self.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      updatedAt: null == updatedAt
          ? _self.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      goalStatus: null == goalStatus
          ? _self.goalStatus
          : goalStatus // ignore: cast_nullable_to_non_nullable
              as GoalStatus,
      priority: null == priority
          ? _self.priority
          : priority // ignore: cast_nullable_to_non_nullable
              as GoalPriority,
      status: null == status
          ? _self.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      tags: null == tags
          ? _self.tags
          : tags // ignore: cast_nullable_to_non_nullable
              as List<String>,
      description: freezed == description
          ? _self.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      createdBy: freezed == createdBy
          ? _self.createdBy
          : createdBy // ignore: cast_nullable_to_non_nullable
              as String?,
      dueDate: freezed == dueDate
          ? _self.dueDate
          : dueDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      completionDate: freezed == completionDate
          ? _self.completionDate
          : completionDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      progressPercentage: freezed == progressPercentage
          ? _self.progressPercentage
          : progressPercentage // ignore: cast_nullable_to_non_nullable
              as double?,
      teamId: freezed == teamId
          ? _self.teamId
          : teamId // ignore: cast_nullable_to_non_nullable
              as String?,
      parentGoalId: freezed == parentGoalId
          ? _self.parentGoalId
          : parentGoalId // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: freezed == metadata
          ? _self.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// Adds pattern-matching-related methods to [GoalModel].
extension GoalModelPatterns on GoalModel {
  /// A variant of `map` that fallback to returning `orElse`.
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case final Subclass value:
  ///     return ...;
  ///   case _:
  ///     return orElse();
  /// }
  /// ```

  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>(
    TResult Function(_GoalModel value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _GoalModel() when $default != null:
        return $default(_that);
      case _:
        return orElse();
    }
  }

  /// A `switch`-like method, using callbacks.
  ///
  /// Callbacks receives the raw object, upcasted.
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case final Subclass value:
  ///     return ...;
  ///   case final Subclass2 value:
  ///     return ...;
  /// }
  /// ```

  @optionalTypeArgs
  TResult map<TResult extends Object?>(
    TResult Function(_GoalModel value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _GoalModel():
        return $default(_that);
      case _:
        throw StateError('Unexpected subclass');
    }
  }

  /// A variant of `map` that fallback to returning `null`.
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case final Subclass value:
  ///     return ...;
  ///   case _:
  ///     return null;
  /// }
  /// ```

  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>(
    TResult? Function(_GoalModel value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _GoalModel() when $default != null:
        return $default(_that);
      case _:
        return null;
    }
  }

  /// A variant of `when` that fallback to an `orElse` callback.
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case Subclass(:final field):
  ///     return ...;
  ///   case _:
  ///     return orElse();
  /// }
  /// ```

  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>(
    TResult Function(
            String id,
            String tenantId,
            String title,
            DateTime createdAt,
            DateTime updatedAt,
            GoalStatus goalStatus,
            GoalPriority priority,
            String status,
            List<String> tags,
            String? description,
            String? createdBy,
            DateTime? dueDate,
            DateTime? completionDate,
            double? progressPercentage,
            String? teamId,
            String? parentGoalId,
            Map<String, dynamic>? metadata)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _GoalModel() when $default != null:
        return $default(
            _that.id,
            _that.tenantId,
            _that.title,
            _that.createdAt,
            _that.updatedAt,
            _that.goalStatus,
            _that.priority,
            _that.status,
            _that.tags,
            _that.description,
            _that.createdBy,
            _that.dueDate,
            _that.completionDate,
            _that.progressPercentage,
            _that.teamId,
            _that.parentGoalId,
            _that.metadata);
      case _:
        return orElse();
    }
  }

  /// A `switch`-like method, using callbacks.
  ///
  /// As opposed to `map`, this offers destructuring.
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case Subclass(:final field):
  ///     return ...;
  ///   case Subclass2(:final field2):
  ///     return ...;
  /// }
  /// ```

  @optionalTypeArgs
  TResult when<TResult extends Object?>(
    TResult Function(
            String id,
            String tenantId,
            String title,
            DateTime createdAt,
            DateTime updatedAt,
            GoalStatus goalStatus,
            GoalPriority priority,
            String status,
            List<String> tags,
            String? description,
            String? createdBy,
            DateTime? dueDate,
            DateTime? completionDate,
            double? progressPercentage,
            String? teamId,
            String? parentGoalId,
            Map<String, dynamic>? metadata)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _GoalModel():
        return $default(
            _that.id,
            _that.tenantId,
            _that.title,
            _that.createdAt,
            _that.updatedAt,
            _that.goalStatus,
            _that.priority,
            _that.status,
            _that.tags,
            _that.description,
            _that.createdBy,
            _that.dueDate,
            _that.completionDate,
            _that.progressPercentage,
            _that.teamId,
            _that.parentGoalId,
            _that.metadata);
      case _:
        throw StateError('Unexpected subclass');
    }
  }

  /// A variant of `when` that fallback to returning `null`
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case Subclass(:final field):
  ///     return ...;
  ///   case _:
  ///     return null;
  /// }
  /// ```

  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>(
    TResult? Function(
            String id,
            String tenantId,
            String title,
            DateTime createdAt,
            DateTime updatedAt,
            GoalStatus goalStatus,
            GoalPriority priority,
            String status,
            List<String> tags,
            String? description,
            String? createdBy,
            DateTime? dueDate,
            DateTime? completionDate,
            double? progressPercentage,
            String? teamId,
            String? parentGoalId,
            Map<String, dynamic>? metadata)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _GoalModel() when $default != null:
        return $default(
            _that.id,
            _that.tenantId,
            _that.title,
            _that.createdAt,
            _that.updatedAt,
            _that.goalStatus,
            _that.priority,
            _that.status,
            _that.tags,
            _that.description,
            _that.createdBy,
            _that.dueDate,
            _that.completionDate,
            _that.progressPercentage,
            _that.teamId,
            _that.parentGoalId,
            _that.metadata);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _GoalModel implements GoalModel {
  const _GoalModel(
      {required this.id,
      required this.tenantId,
      required this.title,
      required this.createdAt,
      required this.updatedAt,
      this.goalStatus = GoalStatus.draft,
      this.priority = GoalPriority.medium,
      this.status = 'active',
      final List<String> tags = const [],
      this.description,
      this.createdBy,
      this.dueDate,
      this.completionDate,
      this.progressPercentage,
      this.teamId,
      this.parentGoalId,
      final Map<String, dynamic>? metadata})
      : _tags = tags,
        _metadata = metadata;
  factory _GoalModel.fromJson(Map<String, dynamic> json) =>
      _$GoalModelFromJson(json);

  @override
  final String id;
  @override
  final String tenantId;
  @override
  final String title;
  @override
  final DateTime createdAt;
  @override
  final DateTime updatedAt;
  @override
  @JsonKey()
  final GoalStatus goalStatus;
  @override
  @JsonKey()
  final GoalPriority priority;
  @override
  @JsonKey()
  final String status;
  final List<String> _tags;
  @override
  @JsonKey()
  List<String> get tags {
    if (_tags is EqualUnmodifiableListView) return _tags;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_tags);
  }

  @override
  final String? description;
  @override
  final String? createdBy;
  @override
  final DateTime? dueDate;
  @override
  final DateTime? completionDate;
  @override
  final double? progressPercentage;
  @override
  final String? teamId;
  @override
  final String? parentGoalId;
  final Map<String, dynamic>? _metadata;
  @override
  Map<String, dynamic>? get metadata {
    final value = _metadata;
    if (value == null) return null;
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  /// Create a copy of GoalModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$GoalModelCopyWith<_GoalModel> get copyWith =>
      __$GoalModelCopyWithImpl<_GoalModel>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$GoalModelToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _GoalModel &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.tenantId, tenantId) ||
                other.tenantId == tenantId) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt) &&
            (identical(other.goalStatus, goalStatus) ||
                other.goalStatus == goalStatus) &&
            (identical(other.priority, priority) ||
                other.priority == priority) &&
            (identical(other.status, status) || other.status == status) &&
            const DeepCollectionEquality().equals(other._tags, _tags) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.createdBy, createdBy) ||
                other.createdBy == createdBy) &&
            (identical(other.dueDate, dueDate) || other.dueDate == dueDate) &&
            (identical(other.completionDate, completionDate) ||
                other.completionDate == completionDate) &&
            (identical(other.progressPercentage, progressPercentage) ||
                other.progressPercentage == progressPercentage) &&
            (identical(other.teamId, teamId) || other.teamId == teamId) &&
            (identical(other.parentGoalId, parentGoalId) ||
                other.parentGoalId == parentGoalId) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      tenantId,
      title,
      createdAt,
      updatedAt,
      goalStatus,
      priority,
      status,
      const DeepCollectionEquality().hash(_tags),
      description,
      createdBy,
      dueDate,
      completionDate,
      progressPercentage,
      teamId,
      parentGoalId,
      const DeepCollectionEquality().hash(_metadata));

  @override
  String toString() {
    return 'GoalModel(id: $id, tenantId: $tenantId, title: $title, createdAt: $createdAt, updatedAt: $updatedAt, goalStatus: $goalStatus, priority: $priority, status: $status, tags: $tags, description: $description, createdBy: $createdBy, dueDate: $dueDate, completionDate: $completionDate, progressPercentage: $progressPercentage, teamId: $teamId, parentGoalId: $parentGoalId, metadata: $metadata)';
  }
}

/// @nodoc
abstract mixin class _$GoalModelCopyWith<$Res>
    implements $GoalModelCopyWith<$Res> {
  factory _$GoalModelCopyWith(
          _GoalModel value, $Res Function(_GoalModel) _then) =
      __$GoalModelCopyWithImpl;
  @override
  @useResult
  $Res call(
      {String id,
      String tenantId,
      String title,
      DateTime createdAt,
      DateTime updatedAt,
      GoalStatus goalStatus,
      GoalPriority priority,
      String status,
      List<String> tags,
      String? description,
      String? createdBy,
      DateTime? dueDate,
      DateTime? completionDate,
      double? progressPercentage,
      String? teamId,
      String? parentGoalId,
      Map<String, dynamic>? metadata});
}

/// @nodoc
class __$GoalModelCopyWithImpl<$Res> implements _$GoalModelCopyWith<$Res> {
  __$GoalModelCopyWithImpl(this._self, this._then);

  final _GoalModel _self;
  final $Res Function(_GoalModel) _then;

  /// Create a copy of GoalModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? id = null,
    Object? tenantId = null,
    Object? title = null,
    Object? createdAt = null,
    Object? updatedAt = null,
    Object? goalStatus = null,
    Object? priority = null,
    Object? status = null,
    Object? tags = null,
    Object? description = freezed,
    Object? createdBy = freezed,
    Object? dueDate = freezed,
    Object? completionDate = freezed,
    Object? progressPercentage = freezed,
    Object? teamId = freezed,
    Object? parentGoalId = freezed,
    Object? metadata = freezed,
  }) {
    return _then(_GoalModel(
      id: null == id
          ? _self.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      tenantId: null == tenantId
          ? _self.tenantId
          : tenantId // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _self.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _self.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      updatedAt: null == updatedAt
          ? _self.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      goalStatus: null == goalStatus
          ? _self.goalStatus
          : goalStatus // ignore: cast_nullable_to_non_nullable
              as GoalStatus,
      priority: null == priority
          ? _self.priority
          : priority // ignore: cast_nullable_to_non_nullable
              as GoalPriority,
      status: null == status
          ? _self.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      tags: null == tags
          ? _self._tags
          : tags // ignore: cast_nullable_to_non_nullable
              as List<String>,
      description: freezed == description
          ? _self.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      createdBy: freezed == createdBy
          ? _self.createdBy
          : createdBy // ignore: cast_nullable_to_non_nullable
              as String?,
      dueDate: freezed == dueDate
          ? _self.dueDate
          : dueDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      completionDate: freezed == completionDate
          ? _self.completionDate
          : completionDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      progressPercentage: freezed == progressPercentage
          ? _self.progressPercentage
          : progressPercentage // ignore: cast_nullable_to_non_nullable
              as double?,
      teamId: freezed == teamId
          ? _self.teamId
          : teamId // ignore: cast_nullable_to_non_nullable
              as String?,
      parentGoalId: freezed == parentGoalId
          ? _self.parentGoalId
          : parentGoalId // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: freezed == metadata
          ? _self._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
mixin _$GoalsState {
  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is GoalsState);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  String toString() {
    return 'GoalsState()';
  }
}

/// @nodoc
class $GoalsStateCopyWith<$Res> {
  $GoalsStateCopyWith(GoalsState _, $Res Function(GoalsState) __);
}

/// Adds pattern-matching-related methods to [GoalsState].
extension GoalsStatePatterns on GoalsState {
  /// A variant of `map` that fallback to returning `orElse`.
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case final Subclass value:
  ///     return ...;
  ///   case _:
  ///     return orElse();
  /// }
  /// ```

  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(_Initial value)? initial,
    TResult Function(_Loading value)? loading,
    TResult Function(_Loaded value)? loaded,
    TResult Function(_Error value)? error,
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _Initial() when initial != null:
        return initial(_that);
      case _Loading() when loading != null:
        return loading(_that);
      case _Loaded() when loaded != null:
        return loaded(_that);
      case _Error() when error != null:
        return error(_that);
      case _:
        return orElse();
    }
  }

  /// A `switch`-like method, using callbacks.
  ///
  /// Callbacks receives the raw object, upcasted.
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case final Subclass value:
  ///     return ...;
  ///   case final Subclass2 value:
  ///     return ...;
  /// }
  /// ```

  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(_Initial value) initial,
    required TResult Function(_Loading value) loading,
    required TResult Function(_Loaded value) loaded,
    required TResult Function(_Error value) error,
  }) {
    final _that = this;
    switch (_that) {
      case _Initial():
        return initial(_that);
      case _Loading():
        return loading(_that);
      case _Loaded():
        return loaded(_that);
      case _Error():
        return error(_that);
      case _:
        throw StateError('Unexpected subclass');
    }
  }

  /// A variant of `map` that fallback to returning `null`.
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case final Subclass value:
  ///     return ...;
  ///   case _:
  ///     return null;
  /// }
  /// ```

  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(_Initial value)? initial,
    TResult? Function(_Loading value)? loading,
    TResult? Function(_Loaded value)? loaded,
    TResult? Function(_Error value)? error,
  }) {
    final _that = this;
    switch (_that) {
      case _Initial() when initial != null:
        return initial(_that);
      case _Loading() when loading != null:
        return loading(_that);
      case _Loaded() when loaded != null:
        return loaded(_that);
      case _Error() when error != null:
        return error(_that);
      case _:
        return null;
    }
  }

  /// A variant of `when` that fallback to an `orElse` callback.
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case Subclass(:final field):
  ///     return ...;
  ///   case _:
  ///     return orElse();
  /// }
  /// ```

  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? initial,
    TResult Function()? loading,
    TResult Function(List<GoalModel> goals, GoalModel? selectedGoal)? loaded,
    TResult Function(String message)? error,
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _Initial() when initial != null:
        return initial();
      case _Loading() when loading != null:
        return loading();
      case _Loaded() when loaded != null:
        return loaded(_that.goals, _that.selectedGoal);
      case _Error() when error != null:
        return error(_that.message);
      case _:
        return orElse();
    }
  }

  /// A `switch`-like method, using callbacks.
  ///
  /// As opposed to `map`, this offers destructuring.
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case Subclass(:final field):
  ///     return ...;
  ///   case Subclass2(:final field2):
  ///     return ...;
  /// }
  /// ```

  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() initial,
    required TResult Function() loading,
    required TResult Function(List<GoalModel> goals, GoalModel? selectedGoal)
        loaded,
    required TResult Function(String message) error,
  }) {
    final _that = this;
    switch (_that) {
      case _Initial():
        return initial();
      case _Loading():
        return loading();
      case _Loaded():
        return loaded(_that.goals, _that.selectedGoal);
      case _Error():
        return error(_that.message);
      case _:
        throw StateError('Unexpected subclass');
    }
  }

  /// A variant of `when` that fallback to returning `null`
  ///
  /// It is equivalent to doing:
  /// ```dart
  /// switch (sealedClass) {
  ///   case Subclass(:final field):
  ///     return ...;
  ///   case _:
  ///     return null;
  /// }
  /// ```

  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? initial,
    TResult? Function()? loading,
    TResult? Function(List<GoalModel> goals, GoalModel? selectedGoal)? loaded,
    TResult? Function(String message)? error,
  }) {
    final _that = this;
    switch (_that) {
      case _Initial() when initial != null:
        return initial();
      case _Loading() when loading != null:
        return loading();
      case _Loaded() when loaded != null:
        return loaded(_that.goals, _that.selectedGoal);
      case _Error() when error != null:
        return error(_that.message);
      case _:
        return null;
    }
  }
}

/// @nodoc

class _Initial implements GoalsState {
  const _Initial();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is _Initial);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  String toString() {
    return 'GoalsState.initial()';
  }
}

/// @nodoc

class _Loading implements GoalsState {
  const _Loading();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is _Loading);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  String toString() {
    return 'GoalsState.loading()';
  }
}

/// @nodoc

class _Loaded implements GoalsState {
  const _Loaded({required final List<GoalModel> goals, this.selectedGoal})
      : _goals = goals;

  final List<GoalModel> _goals;
  List<GoalModel> get goals {
    if (_goals is EqualUnmodifiableListView) return _goals;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_goals);
  }

  final GoalModel? selectedGoal;

  /// Create a copy of GoalsState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$LoadedCopyWith<_Loaded> get copyWith =>
      __$LoadedCopyWithImpl<_Loaded>(this, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _Loaded &&
            const DeepCollectionEquality().equals(other._goals, _goals) &&
            (identical(other.selectedGoal, selectedGoal) ||
                other.selectedGoal == selectedGoal));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType, const DeepCollectionEquality().hash(_goals), selectedGoal);

  @override
  String toString() {
    return 'GoalsState.loaded(goals: $goals, selectedGoal: $selectedGoal)';
  }
}

/// @nodoc
abstract mixin class _$LoadedCopyWith<$Res>
    implements $GoalsStateCopyWith<$Res> {
  factory _$LoadedCopyWith(_Loaded value, $Res Function(_Loaded) _then) =
      __$LoadedCopyWithImpl;
  @useResult
  $Res call({List<GoalModel> goals, GoalModel? selectedGoal});

  $GoalModelCopyWith<$Res>? get selectedGoal;
}

/// @nodoc
class __$LoadedCopyWithImpl<$Res> implements _$LoadedCopyWith<$Res> {
  __$LoadedCopyWithImpl(this._self, this._then);

  final _Loaded _self;
  final $Res Function(_Loaded) _then;

  /// Create a copy of GoalsState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  $Res call({
    Object? goals = null,
    Object? selectedGoal = freezed,
  }) {
    return _then(_Loaded(
      goals: null == goals
          ? _self._goals
          : goals // ignore: cast_nullable_to_non_nullable
              as List<GoalModel>,
      selectedGoal: freezed == selectedGoal
          ? _self.selectedGoal
          : selectedGoal // ignore: cast_nullable_to_non_nullable
              as GoalModel?,
    ));
  }

  /// Create a copy of GoalsState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $GoalModelCopyWith<$Res>? get selectedGoal {
    if (_self.selectedGoal == null) {
      return null;
    }

    return $GoalModelCopyWith<$Res>(_self.selectedGoal!, (value) {
      return _then(_self.copyWith(selectedGoal: value));
    });
  }
}

/// @nodoc

class _Error implements GoalsState {
  const _Error(this.message);

  final String message;

  /// Create a copy of GoalsState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$ErrorCopyWith<_Error> get copyWith =>
      __$ErrorCopyWithImpl<_Error>(this, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _Error &&
            (identical(other.message, message) || other.message == message));
  }

  @override
  int get hashCode => Object.hash(runtimeType, message);

  @override
  String toString() {
    return 'GoalsState.error(message: $message)';
  }
}

/// @nodoc
abstract mixin class _$ErrorCopyWith<$Res>
    implements $GoalsStateCopyWith<$Res> {
  factory _$ErrorCopyWith(_Error value, $Res Function(_Error) _then) =
      __$ErrorCopyWithImpl;
  @useResult
  $Res call({String message});
}

/// @nodoc
class __$ErrorCopyWithImpl<$Res> implements _$ErrorCopyWith<$Res> {
  __$ErrorCopyWithImpl(this._self, this._then);

  final _Error _self;
  final $Res Function(_Error) _then;

  /// Create a copy of GoalsState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  $Res call({
    Object? message = null,
  }) {
    return _then(_Error(
      null == message
          ? _self.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

// dart format on
