import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'api_client_enhanced.dart';
import 'auth.dart';
import 'local_storage.dart';

/// Communication types from the simulation system
enum CommunicationType {
  nudge,
  recommendation,
  directOrder,
  urgent,
  announcement,
  policy,
  consultation
}

/// Delivery status tracking
enum DeliveryStatus {
  sent,
  delivered,
  read,
  acknowledged,
  actionTaken,
  failed
}

/// Action status for communications
enum ActionStatus {
  pending,
  inProgress,
  completed,
  blocked,
  delegated,
  ignored
}

/// Communication model
class Communication {
  final String id;
  final String senderId;
  final String senderName;
  final List<String> recipientIds;
  final String subject;
  final String content;
  final CommunicationType type;
  final int priorityLevel;
  final DateTime timestamp;
  final DateTime? deadline;
  final bool organizationWide;
  final Map<String, dynamic> metadata;

  Communication({
    required this.id,
    required this.senderId,
    required this.senderName,
    required this.recipientIds,
    required this.subject,
    required this.content,
    required this.type,
    required this.priorityLevel,
    required this.timestamp,
    this.deadline,
    this.organizationWide = false,
    this.metadata = const {},
  });

  factory Communication.fromJson(Map<String, dynamic> json) {
    return Communication(
      id: json['communication_id'] ?? json['id'],
      senderId: json['sender_id'],
      senderName: json['sender_name'] ?? 'Unknown',
      recipientIds: List<String>.from(json['recipients'] ?? []),
      subject: json['subject'],
      content: json['content'],
      type: CommunicationType.values.firstWhere(
        (e) => e.toString().split('.').last == json['communication_type'],
        orElse: () => CommunicationType.nudge,
      ),
      priorityLevel: json['priority_level'] ?? 3,
      timestamp: DateTime.parse(json['timestamp']),
      deadline: json['deadline'] != null ? DateTime.parse(json['deadline']) : null,
      organizationWide: json['organization_wide'] ?? false,
      metadata: json['metadata'] ?? {},
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'sender_id': senderId,
      'sender_name': senderName,
      'recipients': recipientIds,
      'subject': subject,
      'content': content,
      'communication_type': type.toString().split('.').last,
      'priority_level': priorityLevel,
      'timestamp': timestamp.toIso8601String(),
      'deadline': deadline?.toIso8601String(),
      'organization_wide': organizationWide,
      'metadata': metadata,
    };
  }
}

/// Communication response model
class CommunicationResponse {
  final String communicationId;
  final ActionStatus status;
  final String? message;
  final Map<String, dynamic> details;

  CommunicationResponse({
    required this.communicationId,
    required this.status,
    this.message,
    this.details = const {},
  });

  Map<String, dynamic> toJson() {
    return {
      'communication_id': communicationId,
      'action_status': status.toString().split('.').last,
      'message': message,
      'details': details,
    };
  }
}

/// Real-time communication service for Flutter app
class CommunicationService extends ChangeNotifier {
  final ApiClientEnhanced _apiClient;
  final AuthService _authService;
  final LocalStorageService _localStorage;

  // Stream controllers for real-time updates
  final StreamController<Communication> _communicationController = 
      StreamController<Communication>.broadcast();
  final StreamController<Map<String, dynamic>> _presenceController = 
      StreamController<Map<String, dynamic>>.broadcast();
  final StreamController<Map<String, dynamic>> _pulseController = 
      StreamController<Map<String, dynamic>>.broadcast();

  // State management
  final List<Communication> _activeCommunications = [];
  final Map<String, CommunicationResponse> _responses = {};
  bool _isActive = false;
  String? _organizationId;
  String? _userId;

  // Polling timer for real-time updates
  Timer? _pollingTimer;

  CommunicationService(this._apiClient, this._authService, this._localStorage);

  // Getters
  Stream<Communication> get communicationStream => _communicationController.stream;
  Stream<Map<String, dynamic>> get presenceStream => _presenceController.stream;
  Stream<Map<String, dynamic>> get pulseStream => _pulseController.stream;
  List<Communication> get activeCommunications => List.unmodifiable(_activeCommunications);
  bool get isActive => _isActive;

  /// Initialize the communication service
  Future<void> initialize() async {
    try {
      final user = _authService.currentUser;
      _userId = user?['uid'];
      _organizationId = user?['organizationId'] ?? user?['tenantId'];

      if (_userId == null || _organizationId == null) {
        throw Exception('User not authenticated or organization not set');
      }

      // Mark user as active
      await _updatePresence(true);

      // Start polling for updates
      _startPolling();

      _isActive = true;
      notifyListeners();

      debugPrint('CommunicationService initialized for user: $_userId');
    } catch (e) {
      debugPrint('Failed to initialize CommunicationService: $e');
      rethrow;
    }
  }

  /// Start polling for real-time updates
  void _startPolling() {
    _pollingTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      _pollForUpdates();
    });
  }

  /// Poll for communication updates
  Future<void> _pollForUpdates() async {
    try {
      // Poll for new communications
      final response = await _apiClient.get('/communication/poll');
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        // Process new communications
        if (data['communications'] != null) {
          for (var commData in data['communications']) {
            final communication = Communication.fromJson(commData);
            _addCommunication(communication);
          }
        }

        // Process pulse updates
        if (data['pulse_updates'] != null) {
          for (var pulseData in data['pulse_updates']) {
            _pulseController.add(pulseData);
          }
        }

        // Process presence updates
        if (data['presence_updates'] != null) {
          for (var presenceData in data['presence_updates']) {
            _presenceController.add(presenceData);
          }
        }
      }
    } catch (e) {
      debugPrint('Error polling for updates: $e');
    }
  }

  /// Add communication to active list
  void _addCommunication(Communication communication) {
    // Avoid duplicates
    if (!_activeCommunications.any((c) => c.id == communication.id)) {
      _activeCommunications.insert(0, communication);
      _communicationController.add(communication);
      notifyListeners();
      
      // Auto-mark as delivered after a short delay
      Timer(const Duration(seconds: 2), () {
        _sendDeliveryConfirmation(communication.id, DeliveryStatus.delivered);
      });
    }
  }

  /// Send delivery confirmation
  Future<void> _sendDeliveryConfirmation(String communicationId, DeliveryStatus status) async {
    try {
      await _apiClient.post('/communication/delivery-confirmation', body: {
        'communication_id': communicationId,
        'status': status.toString().split('.').last,
        'timestamp': DateTime.now().toIso8601String(),
      });
    } catch (e) {
      debugPrint('Failed to send delivery confirmation: $e');
    }
  }

  /// Mark communication as read
  Future<void> markAsRead(String communicationId) async {
    try {
      await _apiClient.post('/communication/read-receipt', body: {
        'communication_id': communicationId,
        'timestamp': DateTime.now().toIso8601String(),
      });
      
      // Update local state
      final index = _activeCommunications.indexWhere((c) => c.id == communicationId);
      if (index != -1) {
        // Could add read status to Communication model if needed
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Failed to mark communication as read: $e');
    }
  }

  /// Respond to communication
  Future<void> respondToCommunication(CommunicationResponse response) async {
    try {
      await _apiClient.post('/communication/respond', body: response.toJson());
      
      // Store response locally
      _responses[response.communicationId] = response;
      notifyListeners();
      
      debugPrint('Response sent for communication: ${response.communicationId}');
    } catch (e) {
      debugPrint('Failed to send response: $e');
      rethrow;
    }
  }

  /// Send a new communication (for managers/executives)
  Future<void> sendCommunication({
    required List<String> recipientIds,
    required String subject,
    required String content,
    required CommunicationType type,
    int priorityLevel = 3,
    DateTime? deadline,
    bool organizationWide = false,
  }) async {
    try {
      await _apiClient.post('/communication/send', body: {
        'recipient_ids': recipientIds,
        'subject': subject,
        'content': content,
        'communication_type': type.toString().split('.').last,
        'priority_level': priorityLevel,
        'deadline': deadline?.toIso8601String(),
        'organization_wide': organizationWide,
      });
      
      debugPrint('Communication sent successfully');
    } catch (e) {
      debugPrint('Failed to send communication: $e');
      rethrow;
    }
  }

  /// Update user presence
  Future<void> _updatePresence(bool isActive) async {
    try {
      await _apiClient.post('/user/presence', body: {
        'is_active': isActive,
        'timestamp': DateTime.now().toIso8601String(),
      });
    } catch (e) {
      debugPrint('Failed to update presence: $e');
    }
  }

  /// Get communication dashboard (for executives)
  Future<Map<String, dynamic>> getCommunicationDashboard(String communicationId) async {
    try {
      final response = await _apiClient.get('/communication/dashboard/$communicationId');
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get dashboard: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Failed to get communication dashboard: $e');
      rethrow;
    }
  }

  /// Get organizational metrics
  Future<Map<String, dynamic>> getOrganizationalMetrics() async {
    try {
      final response = await _apiClient.get('/organization/metrics');
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get metrics: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Failed to get organizational metrics: $e');
      rethrow;
    }
  }

  /// Get user's response to a communication
  CommunicationResponse? getResponse(String communicationId) {
    return _responses[communicationId];
  }

  /// Check if user has responded to a communication
  bool hasResponded(String communicationId) {
    return _responses.containsKey(communicationId);
  }

  /// Get communications by type
  List<Communication> getCommunicationsByType(CommunicationType type) {
    return _activeCommunications.where((c) => c.type == type).toList();
  }

  /// Get high priority communications
  List<Communication> getHighPriorityCommunications() {
    return _activeCommunications.where((c) => c.priorityLevel >= 4).toList();
  }

  /// Get organization-wide communications
  List<Communication> getOrganizationWideCommunications() {
    return _activeCommunications.where((c) => c.organizationWide).toList();
  }

  /// Dispose resources
  @override
  void dispose() {
    _pollingTimer?.cancel();
    _communicationController.close();
    _presenceController.close();
    _pulseController.close();
    
    // Mark user as inactive
    if (_isActive) {
      _updatePresence(false);
    }
    
    super.dispose();
  }

  /// Pause the service (when app goes to background)
  Future<void> pause() async {
    _pollingTimer?.cancel();
    await _updatePresence(false);
    _isActive = false;
    notifyListeners();
  }

  /// Resume the service (when app comes to foreground)
  Future<void> resume() async {
    await _updatePresence(true);
    _startPolling();
    _isActive = true;
    notifyListeners();
  }
}
