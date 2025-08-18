import 'package:flutter/material.dart';
import '../../services/communication_service.dart';
import '../../services/api_client_enhanced.dart';
import '../../services/auth.dart';
import '../../services/local_storage.dart';
import '../../config/app_config.dart';

class CommunicationScreen extends StatefulWidget {
  const CommunicationScreen({Key? key}) : super(key: key);

  @override
  State<CommunicationScreen> createState() => _CommunicationScreenState();
}

class _CommunicationScreenState extends State<CommunicationScreen> {
  late CommunicationService _communicationService;
  bool _isInitialized = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _initializeCommunicationService();
  }

  Future<void> _initializeCommunicationService() async {
    try {
      _communicationService = CommunicationService(
        ApiClientEnhanced(
          baseUrl: AppConfig.apiUrl,
          authService: AuthService(),
        ),
        AuthService(),
        LocalStorageService(),
      );
      
      await _communicationService.initialize();
      
      setState(() {
        _isInitialized = true;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
      });
    }
  }

  @override
  void dispose() {
    if (_isInitialized) {
      _communicationService.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Communications'),
          backgroundColor: Colors.blue[700],
          foregroundColor: Colors.white,
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.error_outline,
                size: 64,
                color: Colors.red[400],
              ),
              const SizedBox(height: 16),
              Text(
                'Failed to initialize communications',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              Text(
                _error!,
                style: Theme.of(context).textTheme.bodyMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    _error = null;
                  });
                  _initializeCommunicationService();
                },
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    if (!_isInitialized) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Communications'),
          backgroundColor: Colors.blue[700],
          foregroundColor: Colors.white,
        ),
        body: const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('Initializing communication system...'),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Communications'),
        backgroundColor: Colors.blue[700],
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {});
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Status indicator
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            color: _communicationService.isActive ? Colors.green[100] : Colors.red[100],
            child: Row(
              children: [
                Icon(
                  _communicationService.isActive ? Icons.wifi : Icons.wifi_off,
                  color: _communicationService.isActive ? Colors.green[700] : Colors.red[700],
                ),
                const SizedBox(width: 8),
                Text(
                  _communicationService.isActive ? 'Connected' : 'Disconnected',
                  style: TextStyle(
                    color: _communicationService.isActive ? Colors.green[700] : Colors.red[700],
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Text(
                  '${_communicationService.activeCommunications.length} active',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
          
          // Communication list
          Expanded(
            child: _buildCommunicationList(),
          ),
        ],
      ),
    );
  }

  Widget _buildCommunicationList() {
    return StreamBuilder<Communication>(
      stream: _communicationService.communicationStream,
      builder: (context, snapshot) {
        final communications = _communicationService.activeCommunications;
        
        if (communications.isEmpty) {
          return const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.inbox, size: 64, color: Colors.grey),
                SizedBox(height: 16),
                Text('No communications yet'),
                SizedBox(height: 8),
                Text('Communications will appear here when received'),
              ],
            ),
          );
        }

        return ListView.builder(
          itemCount: communications.length,
          itemBuilder: (context, index) {
            final comm = communications[index];
            return _buildCommunicationCard(comm);
          },
        );
      },
    );
  }

  Widget _buildCommunicationCard(Communication comm) {
    final hasResponded = _communicationService.hasResponded(comm.id);
    
    return Card(
      margin: const EdgeInsets.all(8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getTypeColor(comm.type),
          child: Icon(
            _getTypeIcon(comm.type),
            color: Colors.white,
          ),
        ),
        title: Text(
          comm.subject,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('From: ${comm.senderName}'),
            Text(comm.content, maxLines: 2, overflow: TextOverflow.ellipsis),
            const SizedBox(height: 4),
            Row(
              children: [
                Icon(Icons.schedule, size: 12, color: Colors.grey[600]),
                const SizedBox(width: 4),
                Text(
                  _formatTimestamp(comm.timestamp),
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
                const Spacer(),
                if (comm.priorityLevel >= 4)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.red[100],
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      'HIGH PRIORITY',
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.red[700],
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
              ],
            ),
          ],
        ),
        trailing: hasResponded
            ? Icon(Icons.check_circle, color: Colors.green[600])
            : Icon(Icons.radio_button_unchecked, color: Colors.grey[400]),
        onTap: () => _showCommunicationDetails(comm),
      ),
    );
  }

  Color _getTypeColor(CommunicationType type) {
    switch (type) {
      case CommunicationType.urgent:
        return Colors.red;
      case CommunicationType.directOrder:
        return Colors.orange;
      case CommunicationType.nudge:
        return Colors.blue;
      case CommunicationType.recommendation:
        return Colors.green;
      case CommunicationType.announcement:
        return Colors.purple;
      case CommunicationType.policy:
        return Colors.brown;
      case CommunicationType.consultation:
        return Colors.teal;
    }
  }

  IconData _getTypeIcon(CommunicationType type) {
    switch (type) {
      case CommunicationType.urgent:
        return Icons.warning;
      case CommunicationType.directOrder:
        return Icons.gavel;
      case CommunicationType.nudge:
        return Icons.notifications;
      case CommunicationType.recommendation:
        return Icons.lightbulb;
      case CommunicationType.announcement:
        return Icons.campaign;
      case CommunicationType.policy:
        return Icons.policy;
      case CommunicationType.consultation:
        return Icons.forum;
    }
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final diff = now.difference(timestamp);
    
    if (diff.inMinutes < 1) {
      return 'Just now';
    } else if (diff.inHours < 1) {
      return '${diff.inMinutes}m ago';
    } else if (diff.inDays < 1) {
      return '${diff.inHours}h ago';
    } else {
      return '${diff.inDays}d ago';
    }
  }

  void _showCommunicationDetails(Communication comm) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(comm.subject),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('From: ${comm.senderName}'),
              const SizedBox(height: 8),
              Text('Type: ${comm.type.toString().split('.').last}'),
              const SizedBox(height: 8),
              Text('Priority: ${comm.priorityLevel}/5'),
              const SizedBox(height: 8),
              if (comm.deadline != null)
                Text('Deadline: ${comm.deadline!.toLocal()}'),
              const SizedBox(height: 16),
              const Text('Content:', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 4),
              Text(comm.content),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
          if (!_communicationService.hasResponded(comm.id))
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                _showResponseDialog(comm);
              },
              child: const Text('Respond'),
            ),
        ],
      ),
    );
  }

  void _showResponseDialog(Communication comm) {
    ActionStatus selectedStatus = ActionStatus.pending;
    final messageController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: Text('Respond to: ${comm.subject}'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              DropdownButtonFormField<ActionStatus>(
                value: selectedStatus,
                decoration: const InputDecoration(labelText: 'Status'),
                items: ActionStatus.values.map((status) {
                  return DropdownMenuItem(
                    value: status,
                    child: Text(status.toString().split('.').last),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    selectedStatus = value!;
                  });
                },
              ),
              const SizedBox(height: 16),
              TextField(
                controller: messageController,
                decoration: const InputDecoration(
                  labelText: 'Response Message (optional)',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                try {
                  final response = CommunicationResponse(
                    communicationId: comm.id,
                    status: selectedStatus,
                    message: messageController.text.isNotEmpty ? messageController.text : null,
                  );
                  
                  await _communicationService.respondToCommunication(response);
                  
                  if (context.mounted) {
                    Navigator.of(context).pop();
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Response sent successfully')),
                    );
                  }
                } catch (e) {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Failed to send response: $e')),
                    );
                  }
                }
              },
              child: const Text('Send'),
            ),
          ],
        ),
      ),
    );
  }
}
