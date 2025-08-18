// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'organization.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_Organization _$OrganizationFromJson(Map<String, dynamic> json) =>
    _Organization(
      id: json['id'] as String,
      name: json['name'] as String,
      webUrl: json['webUrl'] as String?,
      industry: json['industry'] as String?,
      size: json['size'] as String?,
      techContact: json['techContact'] as String?,
      businessContact: json['businessContact'] as String?,
      adminPortalUrl: json['adminPortalUrl'] as String?,
      status: json['status'] as String? ?? 'active',
      features: (json['features'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      branding: json['branding'] == null
          ? null
          : BrandingConfig.fromJson(json['branding'] as Map<String, dynamic>),
      emailDomains: (json['emailDomains'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      autoBindNewUsers: json['autoBindNewUsers'] as bool? ?? true,
      department: json['department'] as String?,
      role: json['role'] as String?,
      createdAt: _dateTimeFromJson(json['createdAt']),
      updatedAt: _dateTimeFromJson(json['updatedAt']),
      createdBy: json['createdBy'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$OrganizationToJson(_Organization instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'webUrl': instance.webUrl,
      'industry': instance.industry,
      'size': instance.size,
      'techContact': instance.techContact,
      'businessContact': instance.businessContact,
      'adminPortalUrl': instance.adminPortalUrl,
      'status': instance.status,
      'features': instance.features,
      'branding': instance.branding,
      'emailDomains': instance.emailDomains,
      'autoBindNewUsers': instance.autoBindNewUsers,
      'department': instance.department,
      'role': instance.role,
      'createdAt': _dateTimeToJson(instance.createdAt),
      'updatedAt': _dateTimeToJson(instance.updatedAt),
      'createdBy': instance.createdBy,
      'metadata': instance.metadata,
    };

_BrandingConfig _$BrandingConfigFromJson(Map<String, dynamic> json) =>
    _BrandingConfig(
      primaryColor: json['primaryColor'] as String?,
      secondaryColor: json['secondaryColor'] as String?,
      logo: json['logo'] as String?,
      favicon: json['favicon'] as String?,
      theme: json['theme'] as String? ?? 'modern',
      customStyles: json['customStyles'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$BrandingConfigToJson(_BrandingConfig instance) =>
    <String, dynamic>{
      'primaryColor': instance.primaryColor,
      'secondaryColor': instance.secondaryColor,
      'logo': instance.logo,
      'favicon': instance.favicon,
      'theme': instance.theme,
      'customStyles': instance.customStyles,
    };

_OrganizationMember _$OrganizationMemberFromJson(Map<String, dynamic> json) =>
    _OrganizationMember(
      userId: json['userId'] as String,
      organizationId: json['organizationId'] as String,
      email: json['email'] as String,
      displayName: json['displayName'] as String?,
      role: json['role'] as String? ?? 'member',
      department: json['department'] as String?,
      permissions: (json['permissions'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      isActive: json['isActive'] as bool? ?? true,
      joinedAt: _dateTimeFromJson(json['joinedAt']),
      lastActiveAt: _dateTimeFromJson(json['lastActiveAt']),
      invitedBy: json['invitedBy'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$OrganizationMemberToJson(_OrganizationMember instance) =>
    <String, dynamic>{
      'userId': instance.userId,
      'organizationId': instance.organizationId,
      'email': instance.email,
      'displayName': instance.displayName,
      'role': instance.role,
      'department': instance.department,
      'permissions': instance.permissions,
      'isActive': instance.isActive,
      'joinedAt': _dateTimeToJson(instance.joinedAt),
      'lastActiveAt': _dateTimeToJson(instance.lastActiveAt),
      'invitedBy': instance.invitedBy,
      'metadata': instance.metadata,
    };

_OrganizationInvitation _$OrganizationInvitationFromJson(
        Map<String, dynamic> json) =>
    _OrganizationInvitation(
      id: json['id'] as String,
      organizationId: json['organizationId'] as String,
      code: json['code'] as String,
      email: json['email'] as String?,
      role: json['role'] as String? ?? 'employee',
      department: json['department'] as String?,
      permissions: (json['permissions'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      status: json['status'] as String? ?? 'pending',
      createdAt: _dateTimeFromJson(json['createdAt']),
      expiresAt: _dateTimeFromJson(json['expiresAt']),
      acceptedAt: _dateTimeFromJson(json['acceptedAt']),
      createdBy: json['createdBy'] as String?,
      acceptedBy: json['acceptedBy'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$OrganizationInvitationToJson(
        _OrganizationInvitation instance) =>
    <String, dynamic>{
      'id': instance.id,
      'organizationId': instance.organizationId,
      'code': instance.code,
      'email': instance.email,
      'role': instance.role,
      'department': instance.department,
      'permissions': instance.permissions,
      'status': instance.status,
      'createdAt': _dateTimeToJson(instance.createdAt),
      'expiresAt': _dateTimeToJson(instance.expiresAt),
      'acceptedAt': _dateTimeToJson(instance.acceptedAt),
      'createdBy': instance.createdBy,
      'acceptedBy': instance.acceptedBy,
      'metadata': instance.metadata,
    };
