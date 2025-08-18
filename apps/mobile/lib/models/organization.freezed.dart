// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'organization.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$Organization {
  String get id;
  String get name;
  String? get webUrl;
  String? get industry;
  String? get size;
  String? get techContact;
  String? get businessContact;
  String? get adminPortalUrl;
  String get status;
  List<String> get features;
  BrandingConfig? get branding;
  List<String> get emailDomains;
  bool get autoBindNewUsers;
  String? get department;
  String? get role;
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
  DateTime? get createdAt;
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
  DateTime? get updatedAt;
  String? get createdBy;
  Map<String, dynamic>? get metadata;

  /// Create a copy of Organization
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $OrganizationCopyWith<Organization> get copyWith =>
      _$OrganizationCopyWithImpl<Organization>(
          this as Organization, _$identity);

  /// Serializes this Organization to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is Organization &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.webUrl, webUrl) || other.webUrl == webUrl) &&
            (identical(other.industry, industry) ||
                other.industry == industry) &&
            (identical(other.size, size) || other.size == size) &&
            (identical(other.techContact, techContact) ||
                other.techContact == techContact) &&
            (identical(other.businessContact, businessContact) ||
                other.businessContact == businessContact) &&
            (identical(other.adminPortalUrl, adminPortalUrl) ||
                other.adminPortalUrl == adminPortalUrl) &&
            (identical(other.status, status) || other.status == status) &&
            const DeepCollectionEquality().equals(other.features, features) &&
            (identical(other.branding, branding) ||
                other.branding == branding) &&
            const DeepCollectionEquality()
                .equals(other.emailDomains, emailDomains) &&
            (identical(other.autoBindNewUsers, autoBindNewUsers) ||
                other.autoBindNewUsers == autoBindNewUsers) &&
            (identical(other.department, department) ||
                other.department == department) &&
            (identical(other.role, role) || other.role == role) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt) &&
            (identical(other.createdBy, createdBy) ||
                other.createdBy == createdBy) &&
            const DeepCollectionEquality().equals(other.metadata, metadata));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hashAll([
        runtimeType,
        id,
        name,
        webUrl,
        industry,
        size,
        techContact,
        businessContact,
        adminPortalUrl,
        status,
        const DeepCollectionEquality().hash(features),
        branding,
        const DeepCollectionEquality().hash(emailDomains),
        autoBindNewUsers,
        department,
        role,
        createdAt,
        updatedAt,
        createdBy,
        const DeepCollectionEquality().hash(metadata)
      ]);

  @override
  String toString() {
    return 'Organization(id: $id, name: $name, webUrl: $webUrl, industry: $industry, size: $size, techContact: $techContact, businessContact: $businessContact, adminPortalUrl: $adminPortalUrl, status: $status, features: $features, branding: $branding, emailDomains: $emailDomains, autoBindNewUsers: $autoBindNewUsers, department: $department, role: $role, createdAt: $createdAt, updatedAt: $updatedAt, createdBy: $createdBy, metadata: $metadata)';
  }
}

/// @nodoc
abstract mixin class $OrganizationCopyWith<$Res> {
  factory $OrganizationCopyWith(
          Organization value, $Res Function(Organization) _then) =
      _$OrganizationCopyWithImpl;
  @useResult
  $Res call(
      {String id,
      String name,
      String? webUrl,
      String? industry,
      String? size,
      String? techContact,
      String? businessContact,
      String? adminPortalUrl,
      String status,
      List<String> features,
      BrandingConfig? branding,
      List<String> emailDomains,
      bool autoBindNewUsers,
      String? department,
      String? role,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      DateTime? createdAt,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      DateTime? updatedAt,
      String? createdBy,
      Map<String, dynamic>? metadata});

  $BrandingConfigCopyWith<$Res>? get branding;
}

/// @nodoc
class _$OrganizationCopyWithImpl<$Res> implements $OrganizationCopyWith<$Res> {
  _$OrganizationCopyWithImpl(this._self, this._then);

  final Organization _self;
  final $Res Function(Organization) _then;

  /// Create a copy of Organization
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? webUrl = freezed,
    Object? industry = freezed,
    Object? size = freezed,
    Object? techContact = freezed,
    Object? businessContact = freezed,
    Object? adminPortalUrl = freezed,
    Object? status = null,
    Object? features = null,
    Object? branding = freezed,
    Object? emailDomains = null,
    Object? autoBindNewUsers = null,
    Object? department = freezed,
    Object? role = freezed,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
    Object? createdBy = freezed,
    Object? metadata = freezed,
  }) {
    return _then(_self.copyWith(
      id: null == id
          ? _self.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _self.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      webUrl: freezed == webUrl
          ? _self.webUrl
          : webUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      industry: freezed == industry
          ? _self.industry
          : industry // ignore: cast_nullable_to_non_nullable
              as String?,
      size: freezed == size
          ? _self.size
          : size // ignore: cast_nullable_to_non_nullable
              as String?,
      techContact: freezed == techContact
          ? _self.techContact
          : techContact // ignore: cast_nullable_to_non_nullable
              as String?,
      businessContact: freezed == businessContact
          ? _self.businessContact
          : businessContact // ignore: cast_nullable_to_non_nullable
              as String?,
      adminPortalUrl: freezed == adminPortalUrl
          ? _self.adminPortalUrl
          : adminPortalUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      status: null == status
          ? _self.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      features: null == features
          ? _self.features
          : features // ignore: cast_nullable_to_non_nullable
              as List<String>,
      branding: freezed == branding
          ? _self.branding
          : branding // ignore: cast_nullable_to_non_nullable
              as BrandingConfig?,
      emailDomains: null == emailDomains
          ? _self.emailDomains
          : emailDomains // ignore: cast_nullable_to_non_nullable
              as List<String>,
      autoBindNewUsers: null == autoBindNewUsers
          ? _self.autoBindNewUsers
          : autoBindNewUsers // ignore: cast_nullable_to_non_nullable
              as bool,
      department: freezed == department
          ? _self.department
          : department // ignore: cast_nullable_to_non_nullable
              as String?,
      role: freezed == role
          ? _self.role
          : role // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: freezed == createdAt
          ? _self.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      updatedAt: freezed == updatedAt
          ? _self.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdBy: freezed == createdBy
          ? _self.createdBy
          : createdBy // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: freezed == metadata
          ? _self.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }

  /// Create a copy of Organization
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $BrandingConfigCopyWith<$Res>? get branding {
    if (_self.branding == null) {
      return null;
    }

    return $BrandingConfigCopyWith<$Res>(_self.branding!, (value) {
      return _then(_self.copyWith(branding: value));
    });
  }
}

/// Adds pattern-matching-related methods to [Organization].
extension OrganizationPatterns on Organization {
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
    TResult Function(_Organization value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _Organization() when $default != null:
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
    TResult Function(_Organization value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _Organization():
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
    TResult? Function(_Organization value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _Organization() when $default != null:
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
            String name,
            String? webUrl,
            String? industry,
            String? size,
            String? techContact,
            String? businessContact,
            String? adminPortalUrl,
            String status,
            List<String> features,
            BrandingConfig? branding,
            List<String> emailDomains,
            bool autoBindNewUsers,
            String? department,
            String? role,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? createdAt,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? updatedAt,
            String? createdBy,
            Map<String, dynamic>? metadata)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _Organization() when $default != null:
        return $default(
            _that.id,
            _that.name,
            _that.webUrl,
            _that.industry,
            _that.size,
            _that.techContact,
            _that.businessContact,
            _that.adminPortalUrl,
            _that.status,
            _that.features,
            _that.branding,
            _that.emailDomains,
            _that.autoBindNewUsers,
            _that.department,
            _that.role,
            _that.createdAt,
            _that.updatedAt,
            _that.createdBy,
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
            String name,
            String? webUrl,
            String? industry,
            String? size,
            String? techContact,
            String? businessContact,
            String? adminPortalUrl,
            String status,
            List<String> features,
            BrandingConfig? branding,
            List<String> emailDomains,
            bool autoBindNewUsers,
            String? department,
            String? role,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? createdAt,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? updatedAt,
            String? createdBy,
            Map<String, dynamic>? metadata)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _Organization():
        return $default(
            _that.id,
            _that.name,
            _that.webUrl,
            _that.industry,
            _that.size,
            _that.techContact,
            _that.businessContact,
            _that.adminPortalUrl,
            _that.status,
            _that.features,
            _that.branding,
            _that.emailDomains,
            _that.autoBindNewUsers,
            _that.department,
            _that.role,
            _that.createdAt,
            _that.updatedAt,
            _that.createdBy,
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
            String name,
            String? webUrl,
            String? industry,
            String? size,
            String? techContact,
            String? businessContact,
            String? adminPortalUrl,
            String status,
            List<String> features,
            BrandingConfig? branding,
            List<String> emailDomains,
            bool autoBindNewUsers,
            String? department,
            String? role,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? createdAt,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? updatedAt,
            String? createdBy,
            Map<String, dynamic>? metadata)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _Organization() when $default != null:
        return $default(
            _that.id,
            _that.name,
            _that.webUrl,
            _that.industry,
            _that.size,
            _that.techContact,
            _that.businessContact,
            _that.adminPortalUrl,
            _that.status,
            _that.features,
            _that.branding,
            _that.emailDomains,
            _that.autoBindNewUsers,
            _that.department,
            _that.role,
            _that.createdAt,
            _that.updatedAt,
            _that.createdBy,
            _that.metadata);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _Organization implements Organization {
  const _Organization(
      {required this.id,
      required this.name,
      this.webUrl,
      this.industry,
      this.size,
      this.techContact,
      this.businessContact,
      this.adminPortalUrl,
      this.status = 'active',
      final List<String> features = const [],
      this.branding,
      final List<String> emailDomains = const [],
      this.autoBindNewUsers = true,
      this.department,
      this.role,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      this.createdAt,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      this.updatedAt,
      this.createdBy,
      final Map<String, dynamic>? metadata})
      : _features = features,
        _emailDomains = emailDomains,
        _metadata = metadata;
  factory _Organization.fromJson(Map<String, dynamic> json) =>
      _$OrganizationFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  final String? webUrl;
  @override
  final String? industry;
  @override
  final String? size;
  @override
  final String? techContact;
  @override
  final String? businessContact;
  @override
  final String? adminPortalUrl;
  @override
  @JsonKey()
  final String status;
  final List<String> _features;
  @override
  @JsonKey()
  List<String> get features {
    if (_features is EqualUnmodifiableListView) return _features;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_features);
  }

  @override
  final BrandingConfig? branding;
  final List<String> _emailDomains;
  @override
  @JsonKey()
  List<String> get emailDomains {
    if (_emailDomains is EqualUnmodifiableListView) return _emailDomains;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_emailDomains);
  }

  @override
  @JsonKey()
  final bool autoBindNewUsers;
  @override
  final String? department;
  @override
  final String? role;
  @override
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
  final DateTime? createdAt;
  @override
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
  final DateTime? updatedAt;
  @override
  final String? createdBy;
  final Map<String, dynamic>? _metadata;
  @override
  Map<String, dynamic>? get metadata {
    final value = _metadata;
    if (value == null) return null;
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  /// Create a copy of Organization
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$OrganizationCopyWith<_Organization> get copyWith =>
      __$OrganizationCopyWithImpl<_Organization>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$OrganizationToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _Organization &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.webUrl, webUrl) || other.webUrl == webUrl) &&
            (identical(other.industry, industry) ||
                other.industry == industry) &&
            (identical(other.size, size) || other.size == size) &&
            (identical(other.techContact, techContact) ||
                other.techContact == techContact) &&
            (identical(other.businessContact, businessContact) ||
                other.businessContact == businessContact) &&
            (identical(other.adminPortalUrl, adminPortalUrl) ||
                other.adminPortalUrl == adminPortalUrl) &&
            (identical(other.status, status) || other.status == status) &&
            const DeepCollectionEquality().equals(other._features, _features) &&
            (identical(other.branding, branding) ||
                other.branding == branding) &&
            const DeepCollectionEquality()
                .equals(other._emailDomains, _emailDomains) &&
            (identical(other.autoBindNewUsers, autoBindNewUsers) ||
                other.autoBindNewUsers == autoBindNewUsers) &&
            (identical(other.department, department) ||
                other.department == department) &&
            (identical(other.role, role) || other.role == role) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt) &&
            (identical(other.createdBy, createdBy) ||
                other.createdBy == createdBy) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hashAll([
        runtimeType,
        id,
        name,
        webUrl,
        industry,
        size,
        techContact,
        businessContact,
        adminPortalUrl,
        status,
        const DeepCollectionEquality().hash(_features),
        branding,
        const DeepCollectionEquality().hash(_emailDomains),
        autoBindNewUsers,
        department,
        role,
        createdAt,
        updatedAt,
        createdBy,
        const DeepCollectionEquality().hash(_metadata)
      ]);

  @override
  String toString() {
    return 'Organization(id: $id, name: $name, webUrl: $webUrl, industry: $industry, size: $size, techContact: $techContact, businessContact: $businessContact, adminPortalUrl: $adminPortalUrl, status: $status, features: $features, branding: $branding, emailDomains: $emailDomains, autoBindNewUsers: $autoBindNewUsers, department: $department, role: $role, createdAt: $createdAt, updatedAt: $updatedAt, createdBy: $createdBy, metadata: $metadata)';
  }
}

/// @nodoc
abstract mixin class _$OrganizationCopyWith<$Res>
    implements $OrganizationCopyWith<$Res> {
  factory _$OrganizationCopyWith(
          _Organization value, $Res Function(_Organization) _then) =
      __$OrganizationCopyWithImpl;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      String? webUrl,
      String? industry,
      String? size,
      String? techContact,
      String? businessContact,
      String? adminPortalUrl,
      String status,
      List<String> features,
      BrandingConfig? branding,
      List<String> emailDomains,
      bool autoBindNewUsers,
      String? department,
      String? role,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      DateTime? createdAt,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      DateTime? updatedAt,
      String? createdBy,
      Map<String, dynamic>? metadata});

  @override
  $BrandingConfigCopyWith<$Res>? get branding;
}

/// @nodoc
class __$OrganizationCopyWithImpl<$Res>
    implements _$OrganizationCopyWith<$Res> {
  __$OrganizationCopyWithImpl(this._self, this._then);

  final _Organization _self;
  final $Res Function(_Organization) _then;

  /// Create a copy of Organization
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? webUrl = freezed,
    Object? industry = freezed,
    Object? size = freezed,
    Object? techContact = freezed,
    Object? businessContact = freezed,
    Object? adminPortalUrl = freezed,
    Object? status = null,
    Object? features = null,
    Object? branding = freezed,
    Object? emailDomains = null,
    Object? autoBindNewUsers = null,
    Object? department = freezed,
    Object? role = freezed,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
    Object? createdBy = freezed,
    Object? metadata = freezed,
  }) {
    return _then(_Organization(
      id: null == id
          ? _self.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _self.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      webUrl: freezed == webUrl
          ? _self.webUrl
          : webUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      industry: freezed == industry
          ? _self.industry
          : industry // ignore: cast_nullable_to_non_nullable
              as String?,
      size: freezed == size
          ? _self.size
          : size // ignore: cast_nullable_to_non_nullable
              as String?,
      techContact: freezed == techContact
          ? _self.techContact
          : techContact // ignore: cast_nullable_to_non_nullable
              as String?,
      businessContact: freezed == businessContact
          ? _self.businessContact
          : businessContact // ignore: cast_nullable_to_non_nullable
              as String?,
      adminPortalUrl: freezed == adminPortalUrl
          ? _self.adminPortalUrl
          : adminPortalUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      status: null == status
          ? _self.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      features: null == features
          ? _self._features
          : features // ignore: cast_nullable_to_non_nullable
              as List<String>,
      branding: freezed == branding
          ? _self.branding
          : branding // ignore: cast_nullable_to_non_nullable
              as BrandingConfig?,
      emailDomains: null == emailDomains
          ? _self._emailDomains
          : emailDomains // ignore: cast_nullable_to_non_nullable
              as List<String>,
      autoBindNewUsers: null == autoBindNewUsers
          ? _self.autoBindNewUsers
          : autoBindNewUsers // ignore: cast_nullable_to_non_nullable
              as bool,
      department: freezed == department
          ? _self.department
          : department // ignore: cast_nullable_to_non_nullable
              as String?,
      role: freezed == role
          ? _self.role
          : role // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: freezed == createdAt
          ? _self.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      updatedAt: freezed == updatedAt
          ? _self.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdBy: freezed == createdBy
          ? _self.createdBy
          : createdBy // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: freezed == metadata
          ? _self._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }

  /// Create a copy of Organization
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $BrandingConfigCopyWith<$Res>? get branding {
    if (_self.branding == null) {
      return null;
    }

    return $BrandingConfigCopyWith<$Res>(_self.branding!, (value) {
      return _then(_self.copyWith(branding: value));
    });
  }
}

/// @nodoc
mixin _$BrandingConfig {
  String? get primaryColor;
  String? get secondaryColor;
  String? get logo;
  String? get favicon;
  String get theme;
  Map<String, dynamic>? get customStyles;

  /// Create a copy of BrandingConfig
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $BrandingConfigCopyWith<BrandingConfig> get copyWith =>
      _$BrandingConfigCopyWithImpl<BrandingConfig>(
          this as BrandingConfig, _$identity);

  /// Serializes this BrandingConfig to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is BrandingConfig &&
            (identical(other.primaryColor, primaryColor) ||
                other.primaryColor == primaryColor) &&
            (identical(other.secondaryColor, secondaryColor) ||
                other.secondaryColor == secondaryColor) &&
            (identical(other.logo, logo) || other.logo == logo) &&
            (identical(other.favicon, favicon) || other.favicon == favicon) &&
            (identical(other.theme, theme) || other.theme == theme) &&
            const DeepCollectionEquality()
                .equals(other.customStyles, customStyles));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, primaryColor, secondaryColor,
      logo, favicon, theme, const DeepCollectionEquality().hash(customStyles));

  @override
  String toString() {
    return 'BrandingConfig(primaryColor: $primaryColor, secondaryColor: $secondaryColor, logo: $logo, favicon: $favicon, theme: $theme, customStyles: $customStyles)';
  }
}

/// @nodoc
abstract mixin class $BrandingConfigCopyWith<$Res> {
  factory $BrandingConfigCopyWith(
          BrandingConfig value, $Res Function(BrandingConfig) _then) =
      _$BrandingConfigCopyWithImpl;
  @useResult
  $Res call(
      {String? primaryColor,
      String? secondaryColor,
      String? logo,
      String? favicon,
      String theme,
      Map<String, dynamic>? customStyles});
}

/// @nodoc
class _$BrandingConfigCopyWithImpl<$Res>
    implements $BrandingConfigCopyWith<$Res> {
  _$BrandingConfigCopyWithImpl(this._self, this._then);

  final BrandingConfig _self;
  final $Res Function(BrandingConfig) _then;

  /// Create a copy of BrandingConfig
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? primaryColor = freezed,
    Object? secondaryColor = freezed,
    Object? logo = freezed,
    Object? favicon = freezed,
    Object? theme = null,
    Object? customStyles = freezed,
  }) {
    return _then(_self.copyWith(
      primaryColor: freezed == primaryColor
          ? _self.primaryColor
          : primaryColor // ignore: cast_nullable_to_non_nullable
              as String?,
      secondaryColor: freezed == secondaryColor
          ? _self.secondaryColor
          : secondaryColor // ignore: cast_nullable_to_non_nullable
              as String?,
      logo: freezed == logo
          ? _self.logo
          : logo // ignore: cast_nullable_to_non_nullable
              as String?,
      favicon: freezed == favicon
          ? _self.favicon
          : favicon // ignore: cast_nullable_to_non_nullable
              as String?,
      theme: null == theme
          ? _self.theme
          : theme // ignore: cast_nullable_to_non_nullable
              as String,
      customStyles: freezed == customStyles
          ? _self.customStyles
          : customStyles // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// Adds pattern-matching-related methods to [BrandingConfig].
extension BrandingConfigPatterns on BrandingConfig {
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
    TResult Function(_BrandingConfig value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _BrandingConfig() when $default != null:
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
    TResult Function(_BrandingConfig value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _BrandingConfig():
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
    TResult? Function(_BrandingConfig value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _BrandingConfig() when $default != null:
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
    TResult Function(String? primaryColor, String? secondaryColor, String? logo,
            String? favicon, String theme, Map<String, dynamic>? customStyles)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _BrandingConfig() when $default != null:
        return $default(_that.primaryColor, _that.secondaryColor, _that.logo,
            _that.favicon, _that.theme, _that.customStyles);
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
    TResult Function(String? primaryColor, String? secondaryColor, String? logo,
            String? favicon, String theme, Map<String, dynamic>? customStyles)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _BrandingConfig():
        return $default(_that.primaryColor, _that.secondaryColor, _that.logo,
            _that.favicon, _that.theme, _that.customStyles);
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
            String? primaryColor,
            String? secondaryColor,
            String? logo,
            String? favicon,
            String theme,
            Map<String, dynamic>? customStyles)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _BrandingConfig() when $default != null:
        return $default(_that.primaryColor, _that.secondaryColor, _that.logo,
            _that.favicon, _that.theme, _that.customStyles);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _BrandingConfig implements BrandingConfig {
  const _BrandingConfig(
      {this.primaryColor,
      this.secondaryColor,
      this.logo,
      this.favicon,
      this.theme = 'modern',
      final Map<String, dynamic>? customStyles})
      : _customStyles = customStyles;
  factory _BrandingConfig.fromJson(Map<String, dynamic> json) =>
      _$BrandingConfigFromJson(json);

  @override
  final String? primaryColor;
  @override
  final String? secondaryColor;
  @override
  final String? logo;
  @override
  final String? favicon;
  @override
  @JsonKey()
  final String theme;
  final Map<String, dynamic>? _customStyles;
  @override
  Map<String, dynamic>? get customStyles {
    final value = _customStyles;
    if (value == null) return null;
    if (_customStyles is EqualUnmodifiableMapView) return _customStyles;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  /// Create a copy of BrandingConfig
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$BrandingConfigCopyWith<_BrandingConfig> get copyWith =>
      __$BrandingConfigCopyWithImpl<_BrandingConfig>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$BrandingConfigToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _BrandingConfig &&
            (identical(other.primaryColor, primaryColor) ||
                other.primaryColor == primaryColor) &&
            (identical(other.secondaryColor, secondaryColor) ||
                other.secondaryColor == secondaryColor) &&
            (identical(other.logo, logo) || other.logo == logo) &&
            (identical(other.favicon, favicon) || other.favicon == favicon) &&
            (identical(other.theme, theme) || other.theme == theme) &&
            const DeepCollectionEquality()
                .equals(other._customStyles, _customStyles));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, primaryColor, secondaryColor,
      logo, favicon, theme, const DeepCollectionEquality().hash(_customStyles));

  @override
  String toString() {
    return 'BrandingConfig(primaryColor: $primaryColor, secondaryColor: $secondaryColor, logo: $logo, favicon: $favicon, theme: $theme, customStyles: $customStyles)';
  }
}

/// @nodoc
abstract mixin class _$BrandingConfigCopyWith<$Res>
    implements $BrandingConfigCopyWith<$Res> {
  factory _$BrandingConfigCopyWith(
          _BrandingConfig value, $Res Function(_BrandingConfig) _then) =
      __$BrandingConfigCopyWithImpl;
  @override
  @useResult
  $Res call(
      {String? primaryColor,
      String? secondaryColor,
      String? logo,
      String? favicon,
      String theme,
      Map<String, dynamic>? customStyles});
}

/// @nodoc
class __$BrandingConfigCopyWithImpl<$Res>
    implements _$BrandingConfigCopyWith<$Res> {
  __$BrandingConfigCopyWithImpl(this._self, this._then);

  final _BrandingConfig _self;
  final $Res Function(_BrandingConfig) _then;

  /// Create a copy of BrandingConfig
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? primaryColor = freezed,
    Object? secondaryColor = freezed,
    Object? logo = freezed,
    Object? favicon = freezed,
    Object? theme = null,
    Object? customStyles = freezed,
  }) {
    return _then(_BrandingConfig(
      primaryColor: freezed == primaryColor
          ? _self.primaryColor
          : primaryColor // ignore: cast_nullable_to_non_nullable
              as String?,
      secondaryColor: freezed == secondaryColor
          ? _self.secondaryColor
          : secondaryColor // ignore: cast_nullable_to_non_nullable
              as String?,
      logo: freezed == logo
          ? _self.logo
          : logo // ignore: cast_nullable_to_non_nullable
              as String?,
      favicon: freezed == favicon
          ? _self.favicon
          : favicon // ignore: cast_nullable_to_non_nullable
              as String?,
      theme: null == theme
          ? _self.theme
          : theme // ignore: cast_nullable_to_non_nullable
              as String,
      customStyles: freezed == customStyles
          ? _self._customStyles
          : customStyles // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
mixin _$OrganizationMember {
  String get userId;
  String get organizationId;
  String get email;
  String? get displayName;
  String get role;
  String? get department;
  List<String> get permissions;
  bool get isActive;
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
  DateTime? get joinedAt;
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
  DateTime? get lastActiveAt;
  String? get invitedBy;
  Map<String, dynamic>? get metadata;

  /// Create a copy of OrganizationMember
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $OrganizationMemberCopyWith<OrganizationMember> get copyWith =>
      _$OrganizationMemberCopyWithImpl<OrganizationMember>(
          this as OrganizationMember, _$identity);

  /// Serializes this OrganizationMember to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is OrganizationMember &&
            (identical(other.userId, userId) || other.userId == userId) &&
            (identical(other.organizationId, organizationId) ||
                other.organizationId == organizationId) &&
            (identical(other.email, email) || other.email == email) &&
            (identical(other.displayName, displayName) ||
                other.displayName == displayName) &&
            (identical(other.role, role) || other.role == role) &&
            (identical(other.department, department) ||
                other.department == department) &&
            const DeepCollectionEquality()
                .equals(other.permissions, permissions) &&
            (identical(other.isActive, isActive) ||
                other.isActive == isActive) &&
            (identical(other.joinedAt, joinedAt) ||
                other.joinedAt == joinedAt) &&
            (identical(other.lastActiveAt, lastActiveAt) ||
                other.lastActiveAt == lastActiveAt) &&
            (identical(other.invitedBy, invitedBy) ||
                other.invitedBy == invitedBy) &&
            const DeepCollectionEquality().equals(other.metadata, metadata));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      userId,
      organizationId,
      email,
      displayName,
      role,
      department,
      const DeepCollectionEquality().hash(permissions),
      isActive,
      joinedAt,
      lastActiveAt,
      invitedBy,
      const DeepCollectionEquality().hash(metadata));

  @override
  String toString() {
    return 'OrganizationMember(userId: $userId, organizationId: $organizationId, email: $email, displayName: $displayName, role: $role, department: $department, permissions: $permissions, isActive: $isActive, joinedAt: $joinedAt, lastActiveAt: $lastActiveAt, invitedBy: $invitedBy, metadata: $metadata)';
  }
}

/// @nodoc
abstract mixin class $OrganizationMemberCopyWith<$Res> {
  factory $OrganizationMemberCopyWith(
          OrganizationMember value, $Res Function(OrganizationMember) _then) =
      _$OrganizationMemberCopyWithImpl;
  @useResult
  $Res call(
      {String userId,
      String organizationId,
      String email,
      String? displayName,
      String role,
      String? department,
      List<String> permissions,
      bool isActive,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      DateTime? joinedAt,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      DateTime? lastActiveAt,
      String? invitedBy,
      Map<String, dynamic>? metadata});
}

/// @nodoc
class _$OrganizationMemberCopyWithImpl<$Res>
    implements $OrganizationMemberCopyWith<$Res> {
  _$OrganizationMemberCopyWithImpl(this._self, this._then);

  final OrganizationMember _self;
  final $Res Function(OrganizationMember) _then;

  /// Create a copy of OrganizationMember
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? userId = null,
    Object? organizationId = null,
    Object? email = null,
    Object? displayName = freezed,
    Object? role = null,
    Object? department = freezed,
    Object? permissions = null,
    Object? isActive = null,
    Object? joinedAt = freezed,
    Object? lastActiveAt = freezed,
    Object? invitedBy = freezed,
    Object? metadata = freezed,
  }) {
    return _then(_self.copyWith(
      userId: null == userId
          ? _self.userId
          : userId // ignore: cast_nullable_to_non_nullable
              as String,
      organizationId: null == organizationId
          ? _self.organizationId
          : organizationId // ignore: cast_nullable_to_non_nullable
              as String,
      email: null == email
          ? _self.email
          : email // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: freezed == displayName
          ? _self.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String?,
      role: null == role
          ? _self.role
          : role // ignore: cast_nullable_to_non_nullable
              as String,
      department: freezed == department
          ? _self.department
          : department // ignore: cast_nullable_to_non_nullable
              as String?,
      permissions: null == permissions
          ? _self.permissions
          : permissions // ignore: cast_nullable_to_non_nullable
              as List<String>,
      isActive: null == isActive
          ? _self.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
      joinedAt: freezed == joinedAt
          ? _self.joinedAt
          : joinedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      lastActiveAt: freezed == lastActiveAt
          ? _self.lastActiveAt
          : lastActiveAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      invitedBy: freezed == invitedBy
          ? _self.invitedBy
          : invitedBy // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: freezed == metadata
          ? _self.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// Adds pattern-matching-related methods to [OrganizationMember].
extension OrganizationMemberPatterns on OrganizationMember {
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
    TResult Function(_OrganizationMember value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _OrganizationMember() when $default != null:
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
    TResult Function(_OrganizationMember value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _OrganizationMember():
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
    TResult? Function(_OrganizationMember value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _OrganizationMember() when $default != null:
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
            String userId,
            String organizationId,
            String email,
            String? displayName,
            String role,
            String? department,
            List<String> permissions,
            bool isActive,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? joinedAt,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? lastActiveAt,
            String? invitedBy,
            Map<String, dynamic>? metadata)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _OrganizationMember() when $default != null:
        return $default(
            _that.userId,
            _that.organizationId,
            _that.email,
            _that.displayName,
            _that.role,
            _that.department,
            _that.permissions,
            _that.isActive,
            _that.joinedAt,
            _that.lastActiveAt,
            _that.invitedBy,
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
            String userId,
            String organizationId,
            String email,
            String? displayName,
            String role,
            String? department,
            List<String> permissions,
            bool isActive,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? joinedAt,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? lastActiveAt,
            String? invitedBy,
            Map<String, dynamic>? metadata)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _OrganizationMember():
        return $default(
            _that.userId,
            _that.organizationId,
            _that.email,
            _that.displayName,
            _that.role,
            _that.department,
            _that.permissions,
            _that.isActive,
            _that.joinedAt,
            _that.lastActiveAt,
            _that.invitedBy,
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
            String userId,
            String organizationId,
            String email,
            String? displayName,
            String role,
            String? department,
            List<String> permissions,
            bool isActive,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? joinedAt,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? lastActiveAt,
            String? invitedBy,
            Map<String, dynamic>? metadata)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _OrganizationMember() when $default != null:
        return $default(
            _that.userId,
            _that.organizationId,
            _that.email,
            _that.displayName,
            _that.role,
            _that.department,
            _that.permissions,
            _that.isActive,
            _that.joinedAt,
            _that.lastActiveAt,
            _that.invitedBy,
            _that.metadata);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _OrganizationMember implements OrganizationMember {
  const _OrganizationMember(
      {required this.userId,
      required this.organizationId,
      required this.email,
      this.displayName,
      this.role = 'member',
      this.department,
      final List<String> permissions = const [],
      this.isActive = true,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      this.joinedAt,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      this.lastActiveAt,
      this.invitedBy,
      final Map<String, dynamic>? metadata})
      : _permissions = permissions,
        _metadata = metadata;
  factory _OrganizationMember.fromJson(Map<String, dynamic> json) =>
      _$OrganizationMemberFromJson(json);

  @override
  final String userId;
  @override
  final String organizationId;
  @override
  final String email;
  @override
  final String? displayName;
  @override
  @JsonKey()
  final String role;
  @override
  final String? department;
  final List<String> _permissions;
  @override
  @JsonKey()
  List<String> get permissions {
    if (_permissions is EqualUnmodifiableListView) return _permissions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_permissions);
  }

  @override
  @JsonKey()
  final bool isActive;
  @override
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
  final DateTime? joinedAt;
  @override
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
  final DateTime? lastActiveAt;
  @override
  final String? invitedBy;
  final Map<String, dynamic>? _metadata;
  @override
  Map<String, dynamic>? get metadata {
    final value = _metadata;
    if (value == null) return null;
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  /// Create a copy of OrganizationMember
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$OrganizationMemberCopyWith<_OrganizationMember> get copyWith =>
      __$OrganizationMemberCopyWithImpl<_OrganizationMember>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$OrganizationMemberToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _OrganizationMember &&
            (identical(other.userId, userId) || other.userId == userId) &&
            (identical(other.organizationId, organizationId) ||
                other.organizationId == organizationId) &&
            (identical(other.email, email) || other.email == email) &&
            (identical(other.displayName, displayName) ||
                other.displayName == displayName) &&
            (identical(other.role, role) || other.role == role) &&
            (identical(other.department, department) ||
                other.department == department) &&
            const DeepCollectionEquality()
                .equals(other._permissions, _permissions) &&
            (identical(other.isActive, isActive) ||
                other.isActive == isActive) &&
            (identical(other.joinedAt, joinedAt) ||
                other.joinedAt == joinedAt) &&
            (identical(other.lastActiveAt, lastActiveAt) ||
                other.lastActiveAt == lastActiveAt) &&
            (identical(other.invitedBy, invitedBy) ||
                other.invitedBy == invitedBy) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      userId,
      organizationId,
      email,
      displayName,
      role,
      department,
      const DeepCollectionEquality().hash(_permissions),
      isActive,
      joinedAt,
      lastActiveAt,
      invitedBy,
      const DeepCollectionEquality().hash(_metadata));

  @override
  String toString() {
    return 'OrganizationMember(userId: $userId, organizationId: $organizationId, email: $email, displayName: $displayName, role: $role, department: $department, permissions: $permissions, isActive: $isActive, joinedAt: $joinedAt, lastActiveAt: $lastActiveAt, invitedBy: $invitedBy, metadata: $metadata)';
  }
}

/// @nodoc
abstract mixin class _$OrganizationMemberCopyWith<$Res>
    implements $OrganizationMemberCopyWith<$Res> {
  factory _$OrganizationMemberCopyWith(
          _OrganizationMember value, $Res Function(_OrganizationMember) _then) =
      __$OrganizationMemberCopyWithImpl;
  @override
  @useResult
  $Res call(
      {String userId,
      String organizationId,
      String email,
      String? displayName,
      String role,
      String? department,
      List<String> permissions,
      bool isActive,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      DateTime? joinedAt,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      DateTime? lastActiveAt,
      String? invitedBy,
      Map<String, dynamic>? metadata});
}

/// @nodoc
class __$OrganizationMemberCopyWithImpl<$Res>
    implements _$OrganizationMemberCopyWith<$Res> {
  __$OrganizationMemberCopyWithImpl(this._self, this._then);

  final _OrganizationMember _self;
  final $Res Function(_OrganizationMember) _then;

  /// Create a copy of OrganizationMember
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? userId = null,
    Object? organizationId = null,
    Object? email = null,
    Object? displayName = freezed,
    Object? role = null,
    Object? department = freezed,
    Object? permissions = null,
    Object? isActive = null,
    Object? joinedAt = freezed,
    Object? lastActiveAt = freezed,
    Object? invitedBy = freezed,
    Object? metadata = freezed,
  }) {
    return _then(_OrganizationMember(
      userId: null == userId
          ? _self.userId
          : userId // ignore: cast_nullable_to_non_nullable
              as String,
      organizationId: null == organizationId
          ? _self.organizationId
          : organizationId // ignore: cast_nullable_to_non_nullable
              as String,
      email: null == email
          ? _self.email
          : email // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: freezed == displayName
          ? _self.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String?,
      role: null == role
          ? _self.role
          : role // ignore: cast_nullable_to_non_nullable
              as String,
      department: freezed == department
          ? _self.department
          : department // ignore: cast_nullable_to_non_nullable
              as String?,
      permissions: null == permissions
          ? _self._permissions
          : permissions // ignore: cast_nullable_to_non_nullable
              as List<String>,
      isActive: null == isActive
          ? _self.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
      joinedAt: freezed == joinedAt
          ? _self.joinedAt
          : joinedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      lastActiveAt: freezed == lastActiveAt
          ? _self.lastActiveAt
          : lastActiveAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      invitedBy: freezed == invitedBy
          ? _self.invitedBy
          : invitedBy // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: freezed == metadata
          ? _self._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
mixin _$OrganizationInvitation {
  String get id;
  String get organizationId;
  String get code;
  String? get email;
  String get role;
  String? get department;
  List<String> get permissions;
  String get status;
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
  DateTime? get createdAt;
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
  DateTime? get expiresAt;
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
  DateTime? get acceptedAt;
  String? get createdBy;
  String? get acceptedBy;
  Map<String, dynamic>? get metadata;

  /// Create a copy of OrganizationInvitation
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $OrganizationInvitationCopyWith<OrganizationInvitation> get copyWith =>
      _$OrganizationInvitationCopyWithImpl<OrganizationInvitation>(
          this as OrganizationInvitation, _$identity);

  /// Serializes this OrganizationInvitation to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is OrganizationInvitation &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.organizationId, organizationId) ||
                other.organizationId == organizationId) &&
            (identical(other.code, code) || other.code == code) &&
            (identical(other.email, email) || other.email == email) &&
            (identical(other.role, role) || other.role == role) &&
            (identical(other.department, department) ||
                other.department == department) &&
            const DeepCollectionEquality()
                .equals(other.permissions, permissions) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.expiresAt, expiresAt) ||
                other.expiresAt == expiresAt) &&
            (identical(other.acceptedAt, acceptedAt) ||
                other.acceptedAt == acceptedAt) &&
            (identical(other.createdBy, createdBy) ||
                other.createdBy == createdBy) &&
            (identical(other.acceptedBy, acceptedBy) ||
                other.acceptedBy == acceptedBy) &&
            const DeepCollectionEquality().equals(other.metadata, metadata));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      organizationId,
      code,
      email,
      role,
      department,
      const DeepCollectionEquality().hash(permissions),
      status,
      createdAt,
      expiresAt,
      acceptedAt,
      createdBy,
      acceptedBy,
      const DeepCollectionEquality().hash(metadata));

  @override
  String toString() {
    return 'OrganizationInvitation(id: $id, organizationId: $organizationId, code: $code, email: $email, role: $role, department: $department, permissions: $permissions, status: $status, createdAt: $createdAt, expiresAt: $expiresAt, acceptedAt: $acceptedAt, createdBy: $createdBy, acceptedBy: $acceptedBy, metadata: $metadata)';
  }
}

/// @nodoc
abstract mixin class $OrganizationInvitationCopyWith<$Res> {
  factory $OrganizationInvitationCopyWith(OrganizationInvitation value,
          $Res Function(OrganizationInvitation) _then) =
      _$OrganizationInvitationCopyWithImpl;
  @useResult
  $Res call(
      {String id,
      String organizationId,
      String code,
      String? email,
      String role,
      String? department,
      List<String> permissions,
      String status,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      DateTime? createdAt,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      DateTime? expiresAt,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      DateTime? acceptedAt,
      String? createdBy,
      String? acceptedBy,
      Map<String, dynamic>? metadata});
}

/// @nodoc
class _$OrganizationInvitationCopyWithImpl<$Res>
    implements $OrganizationInvitationCopyWith<$Res> {
  _$OrganizationInvitationCopyWithImpl(this._self, this._then);

  final OrganizationInvitation _self;
  final $Res Function(OrganizationInvitation) _then;

  /// Create a copy of OrganizationInvitation
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? organizationId = null,
    Object? code = null,
    Object? email = freezed,
    Object? role = null,
    Object? department = freezed,
    Object? permissions = null,
    Object? status = null,
    Object? createdAt = freezed,
    Object? expiresAt = freezed,
    Object? acceptedAt = freezed,
    Object? createdBy = freezed,
    Object? acceptedBy = freezed,
    Object? metadata = freezed,
  }) {
    return _then(_self.copyWith(
      id: null == id
          ? _self.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      organizationId: null == organizationId
          ? _self.organizationId
          : organizationId // ignore: cast_nullable_to_non_nullable
              as String,
      code: null == code
          ? _self.code
          : code // ignore: cast_nullable_to_non_nullable
              as String,
      email: freezed == email
          ? _self.email
          : email // ignore: cast_nullable_to_non_nullable
              as String?,
      role: null == role
          ? _self.role
          : role // ignore: cast_nullable_to_non_nullable
              as String,
      department: freezed == department
          ? _self.department
          : department // ignore: cast_nullable_to_non_nullable
              as String?,
      permissions: null == permissions
          ? _self.permissions
          : permissions // ignore: cast_nullable_to_non_nullable
              as List<String>,
      status: null == status
          ? _self.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: freezed == createdAt
          ? _self.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      expiresAt: freezed == expiresAt
          ? _self.expiresAt
          : expiresAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      acceptedAt: freezed == acceptedAt
          ? _self.acceptedAt
          : acceptedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdBy: freezed == createdBy
          ? _self.createdBy
          : createdBy // ignore: cast_nullable_to_non_nullable
              as String?,
      acceptedBy: freezed == acceptedBy
          ? _self.acceptedBy
          : acceptedBy // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: freezed == metadata
          ? _self.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// Adds pattern-matching-related methods to [OrganizationInvitation].
extension OrganizationInvitationPatterns on OrganizationInvitation {
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
    TResult Function(_OrganizationInvitation value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _OrganizationInvitation() when $default != null:
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
    TResult Function(_OrganizationInvitation value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _OrganizationInvitation():
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
    TResult? Function(_OrganizationInvitation value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _OrganizationInvitation() when $default != null:
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
            String organizationId,
            String code,
            String? email,
            String role,
            String? department,
            List<String> permissions,
            String status,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? createdAt,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? expiresAt,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? acceptedAt,
            String? createdBy,
            String? acceptedBy,
            Map<String, dynamic>? metadata)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _OrganizationInvitation() when $default != null:
        return $default(
            _that.id,
            _that.organizationId,
            _that.code,
            _that.email,
            _that.role,
            _that.department,
            _that.permissions,
            _that.status,
            _that.createdAt,
            _that.expiresAt,
            _that.acceptedAt,
            _that.createdBy,
            _that.acceptedBy,
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
            String organizationId,
            String code,
            String? email,
            String role,
            String? department,
            List<String> permissions,
            String status,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? createdAt,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? expiresAt,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? acceptedAt,
            String? createdBy,
            String? acceptedBy,
            Map<String, dynamic>? metadata)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _OrganizationInvitation():
        return $default(
            _that.id,
            _that.organizationId,
            _that.code,
            _that.email,
            _that.role,
            _that.department,
            _that.permissions,
            _that.status,
            _that.createdAt,
            _that.expiresAt,
            _that.acceptedAt,
            _that.createdBy,
            _that.acceptedBy,
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
            String organizationId,
            String code,
            String? email,
            String role,
            String? department,
            List<String> permissions,
            String status,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? createdAt,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? expiresAt,
            @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
            DateTime? acceptedAt,
            String? createdBy,
            String? acceptedBy,
            Map<String, dynamic>? metadata)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _OrganizationInvitation() when $default != null:
        return $default(
            _that.id,
            _that.organizationId,
            _that.code,
            _that.email,
            _that.role,
            _that.department,
            _that.permissions,
            _that.status,
            _that.createdAt,
            _that.expiresAt,
            _that.acceptedAt,
            _that.createdBy,
            _that.acceptedBy,
            _that.metadata);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _OrganizationInvitation implements OrganizationInvitation {
  const _OrganizationInvitation(
      {required this.id,
      required this.organizationId,
      required this.code,
      this.email,
      this.role = 'employee',
      this.department,
      final List<String> permissions = const [],
      this.status = 'pending',
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      this.createdAt,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      this.expiresAt,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      this.acceptedAt,
      this.createdBy,
      this.acceptedBy,
      final Map<String, dynamic>? metadata})
      : _permissions = permissions,
        _metadata = metadata;
  factory _OrganizationInvitation.fromJson(Map<String, dynamic> json) =>
      _$OrganizationInvitationFromJson(json);

  @override
  final String id;
  @override
  final String organizationId;
  @override
  final String code;
  @override
  final String? email;
  @override
  @JsonKey()
  final String role;
  @override
  final String? department;
  final List<String> _permissions;
  @override
  @JsonKey()
  List<String> get permissions {
    if (_permissions is EqualUnmodifiableListView) return _permissions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_permissions);
  }

  @override
  @JsonKey()
  final String status;
  @override
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
  final DateTime? createdAt;
  @override
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
  final DateTime? expiresAt;
  @override
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
  final DateTime? acceptedAt;
  @override
  final String? createdBy;
  @override
  final String? acceptedBy;
  final Map<String, dynamic>? _metadata;
  @override
  Map<String, dynamic>? get metadata {
    final value = _metadata;
    if (value == null) return null;
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  /// Create a copy of OrganizationInvitation
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$OrganizationInvitationCopyWith<_OrganizationInvitation> get copyWith =>
      __$OrganizationInvitationCopyWithImpl<_OrganizationInvitation>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$OrganizationInvitationToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _OrganizationInvitation &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.organizationId, organizationId) ||
                other.organizationId == organizationId) &&
            (identical(other.code, code) || other.code == code) &&
            (identical(other.email, email) || other.email == email) &&
            (identical(other.role, role) || other.role == role) &&
            (identical(other.department, department) ||
                other.department == department) &&
            const DeepCollectionEquality()
                .equals(other._permissions, _permissions) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.expiresAt, expiresAt) ||
                other.expiresAt == expiresAt) &&
            (identical(other.acceptedAt, acceptedAt) ||
                other.acceptedAt == acceptedAt) &&
            (identical(other.createdBy, createdBy) ||
                other.createdBy == createdBy) &&
            (identical(other.acceptedBy, acceptedBy) ||
                other.acceptedBy == acceptedBy) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      organizationId,
      code,
      email,
      role,
      department,
      const DeepCollectionEquality().hash(_permissions),
      status,
      createdAt,
      expiresAt,
      acceptedAt,
      createdBy,
      acceptedBy,
      const DeepCollectionEquality().hash(_metadata));

  @override
  String toString() {
    return 'OrganizationInvitation(id: $id, organizationId: $organizationId, code: $code, email: $email, role: $role, department: $department, permissions: $permissions, status: $status, createdAt: $createdAt, expiresAt: $expiresAt, acceptedAt: $acceptedAt, createdBy: $createdBy, acceptedBy: $acceptedBy, metadata: $metadata)';
  }
}

/// @nodoc
abstract mixin class _$OrganizationInvitationCopyWith<$Res>
    implements $OrganizationInvitationCopyWith<$Res> {
  factory _$OrganizationInvitationCopyWith(_OrganizationInvitation value,
          $Res Function(_OrganizationInvitation) _then) =
      __$OrganizationInvitationCopyWithImpl;
  @override
  @useResult
  $Res call(
      {String id,
      String organizationId,
      String code,
      String? email,
      String role,
      String? department,
      List<String> permissions,
      String status,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      DateTime? createdAt,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      DateTime? expiresAt,
      @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
      DateTime? acceptedAt,
      String? createdBy,
      String? acceptedBy,
      Map<String, dynamic>? metadata});
}

/// @nodoc
class __$OrganizationInvitationCopyWithImpl<$Res>
    implements _$OrganizationInvitationCopyWith<$Res> {
  __$OrganizationInvitationCopyWithImpl(this._self, this._then);

  final _OrganizationInvitation _self;
  final $Res Function(_OrganizationInvitation) _then;

  /// Create a copy of OrganizationInvitation
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? id = null,
    Object? organizationId = null,
    Object? code = null,
    Object? email = freezed,
    Object? role = null,
    Object? department = freezed,
    Object? permissions = null,
    Object? status = null,
    Object? createdAt = freezed,
    Object? expiresAt = freezed,
    Object? acceptedAt = freezed,
    Object? createdBy = freezed,
    Object? acceptedBy = freezed,
    Object? metadata = freezed,
  }) {
    return _then(_OrganizationInvitation(
      id: null == id
          ? _self.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      organizationId: null == organizationId
          ? _self.organizationId
          : organizationId // ignore: cast_nullable_to_non_nullable
              as String,
      code: null == code
          ? _self.code
          : code // ignore: cast_nullable_to_non_nullable
              as String,
      email: freezed == email
          ? _self.email
          : email // ignore: cast_nullable_to_non_nullable
              as String?,
      role: null == role
          ? _self.role
          : role // ignore: cast_nullable_to_non_nullable
              as String,
      department: freezed == department
          ? _self.department
          : department // ignore: cast_nullable_to_non_nullable
              as String?,
      permissions: null == permissions
          ? _self._permissions
          : permissions // ignore: cast_nullable_to_non_nullable
              as List<String>,
      status: null == status
          ? _self.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: freezed == createdAt
          ? _self.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      expiresAt: freezed == expiresAt
          ? _self.expiresAt
          : expiresAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      acceptedAt: freezed == acceptedAt
          ? _self.acceptedAt
          : acceptedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdBy: freezed == createdBy
          ? _self.createdBy
          : createdBy // ignore: cast_nullable_to_non_nullable
              as String?,
      acceptedBy: freezed == acceptedBy
          ? _self.acceptedBy
          : acceptedBy // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: freezed == metadata
          ? _self._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

// dart format on
