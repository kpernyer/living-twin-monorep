import 'package:freezed_annotation/freezed_annotation.dart';

part 'organization.freezed.dart';
part 'organization.g.dart';

/// Organization model with json_serializable
@freezed
class Organization with _$Organization {
  const factory Organization({
    required String id,
    required String name,
    String? webUrl,
    String? industry,
    String? size,
    String? techContact,
    String? businessContact,
    String? adminPortalUrl,
    @Default('active') String status,
    @Default([]) List<String> features,
    BrandingConfig? branding,
    @Default([]) List<String> emailDomains,
    @Default(true) bool autoBindNewUsers,
    String? department,
    String? role,
    @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
    DateTime? createdAt,
    @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
    DateTime? updatedAt,
    String? createdBy,
    Map<String, dynamic>? metadata,
  }) = _Organization;

  factory Organization.fromJson(Map<String, dynamic> json) =>
      _$OrganizationFromJson(json);
}

/// Branding configuration for organization
@freezed
class BrandingConfig with _$BrandingConfig {
  const factory BrandingConfig({
    String? primaryColor,
    String? secondaryColor,
    String? logo,
    String? favicon,
    @Default('modern') String theme,
    Map<String, dynamic>? customStyles,
  }) = _BrandingConfig;

  factory BrandingConfig.fromJson(Map<String, dynamic> json) =>
      _$BrandingConfigFromJson(json);
}

/// Organization member model
@freezed
class OrganizationMember with _$OrganizationMember {
  const factory OrganizationMember({
    required String userId,
    required String organizationId,
    required String email,
    String? displayName,
    @Default('member') String role,
    String? department,
    @Default([]) List<String> permissions,
    @Default(true) bool isActive,
    @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
    DateTime? joinedAt,
    @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
    DateTime? lastActiveAt,
    String? invitedBy,
    Map<String, dynamic>? metadata,
  }) = _OrganizationMember;

  factory OrganizationMember.fromJson(Map<String, dynamic> json) =>
      _$OrganizationMemberFromJson(json);
}

/// Organization invitation model
@freezed
class OrganizationInvitation with _$OrganizationInvitation {
  const factory OrganizationInvitation({
    required String id,
    required String organizationId,
    required String code,
    String? email,
    @Default('employee') String role,
    String? department,
    @Default([]) List<String> permissions,
    @Default('pending') String status,
    @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
    DateTime? createdAt,
    @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
    DateTime? expiresAt,
    @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
    DateTime? acceptedAt,
    String? createdBy,
    String? acceptedBy,
    Map<String, dynamic>? metadata,
  }) = _OrganizationInvitation;

  factory OrganizationInvitation.fromJson(Map<String, dynamic> json) =>
      _$OrganizationInvitationFromJson(json);
}

/// Helper functions for DateTime serialization
DateTime? _dateTimeFromJson(json) {
  if (json == null) return null;
  if (json is String) return DateTime.parse(json);
  if (json is int) return DateTime.fromMillisecondsSinceEpoch(json);
  throw ArgumentError('Cannot convert $json to DateTime');
}

String? _dateTimeToJson(DateTime? dateTime) {
  return dateTime?.toIso8601String();
}

/// Organization roles enum
enum OrganizationRole {
  owner,
  admin,
  manager,
  employee,
  member,
  guest,
}

/// Extension for organization role
extension OrganizationRoleX on OrganizationRole {
  String get displayName {
    switch (this) {
      case OrganizationRole.owner:
        return 'Owner';
      case OrganizationRole.admin:
        return 'Administrator';
      case OrganizationRole.manager:
        return 'Manager';
      case OrganizationRole.employee:
        return 'Employee';
      case OrganizationRole.member:
        return 'Member';
      case OrganizationRole.guest:
        return 'Guest';
    }
  }
  
  List<String> get defaultPermissions {
    switch (this) {
      case OrganizationRole.owner:
        return ['read', 'write', 'delete', 'admin', 'billing', 'invite'];
      case OrganizationRole.admin:
        return ['read', 'write', 'delete', 'admin', 'invite'];
      case OrganizationRole.manager:
        return ['read', 'write', 'invite'];
      case OrganizationRole.employee:
        return ['read', 'write'];
      case OrganizationRole.member:
        return ['read'];
      case OrganizationRole.guest:
        return ['read'];
    }
  }
  
  bool get canInviteMembers {
    return this == OrganizationRole.owner || 
           this == OrganizationRole.admin || 
           this == OrganizationRole.manager;
  }
  
  bool get canManageOrganization {
    return this == OrganizationRole.owner || 
           this == OrganizationRole.admin;
  }
}
