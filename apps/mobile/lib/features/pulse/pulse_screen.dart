import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../config/app_config.dart';
import '../../services/api_client_enhanced.dart';
import '../../services/auth.dart';
import '../../services/local_storage.dart';

class PulseScreen extends StatefulWidget {
  const PulseScreen({super.key});

  @override
  State<PulseScreen> createState() => _PulseScreenState();
}

class _PulseScreenState extends State<PulseScreen> {
  late final ApiClientEnhanced _apiClient;
  final LocalStorageService _storage = LocalStorageService();
  
  @override
  void initState() {
    super.initState();
    _apiClient = ApiClientEnhanced(
      baseUrl: AppConfig.apiUrl,
      authService: AuthService(),
    );
    _loadPulseData();
  }
  
  Map<String, dynamic> _stats = {};
  List<Map<String, dynamic>> _recentMessages = [];
  List<Map<String, dynamic>> _recentDocuments = [];
  bool _isLoading = true;
  bool _isOnline = true;

  Future<void> _loadPulseData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // Check connectivity
      final connectivityResult = await Connectivity().checkConnectivity();
      _isOnline = connectivityResult != ConnectivityResult.none;
      
      // Load recent messages from local storage
      final messages = await _storage.getChatMessages(limit: 10);
      final answeredMessages = messages.where((m) => m['answer'] != null).toList();
      
      // Mock data for now (since these methods don't exist in ApiClientEnhanced)
      final mockOfflineStats = {
        'totalMessages': answeredMessages.length,
        'totalDocuments': 5,
        'unsyncedMessages': 0,
        'unsyncedDocuments': 0,
        'pendingRetries': 0,
      };
      
      final mockDocuments = [
        {'title': 'Sample Document 1', 'created_at': DateTime.now().subtract(const Duration(days: 1))},
        {'title': 'Sample Document 2', 'created_at': DateTime.now().subtract(const Duration(days: 2))},
      ];
      
      // Calculate stats
      final totalQueries = mockOfflineStats['totalMessages'] ?? 0;
      final totalDocuments = mockOfflineStats['totalDocuments'] ?? 0;
      final avgConfidence = _calculateAverageConfidence(answeredMessages);
      
      setState(() {
        _stats = {
          'totalQueries': totalQueries,
          'totalDocuments': totalDocuments,
          'avgConfidence': avgConfidence,
          'unsyncedMessages': mockOfflineStats['unsyncedMessages'] ?? 0,
          'unsyncedDocuments': mockOfflineStats['unsyncedDocuments'] ?? 0,
          'pendingRetries': mockOfflineStats['pendingRetries'] ?? 0,
        };
        _recentMessages = answeredMessages;
        _recentDocuments = mockDocuments;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading pulse data: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  double _calculateAverageConfidence(List<Map<String, dynamic>> messages) {
    if (messages.isEmpty) return 0;
    
    final confidenceValues = messages
        .where((m) => m['confidence'] != null)
        .map((m) => m['confidence'] as double)
        .toList();
    
    if (confidenceValues.isEmpty) return 0;
    
    final sum = confidenceValues.reduce((a, b) => a + b);
    return sum / confidenceValues.length;
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required IconData icon,
    required Color color,
    String? subtitle,
  }) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(icon, color: color, size: 24),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      Text(
                        value,
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (subtitle != null)
                        Text(
                          subtitle,
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[500],
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentMessage(Map<String, dynamic> message) {
    final timestamp = DateTime.fromMillisecondsSinceEpoch(message['timestamp']);
    final confidence = message['confidence'] as double?;
    final sources = message['sources'] as List<dynamic>? ?? [];
    final isSynced = message['is_synced'] as bool;
    
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    message['question'],
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (!isSynced)
                  Icon(
                    Icons.schedule,
                    size: 16,
                    color: Colors.orange[600],
                  ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              message['answer'] ?? 'Processing...',
              style: TextStyle(
                color: Colors.grey[700],
                fontSize: 13,
              ),
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                if (confidence != null) ...[
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: _getConfidenceColor(confidence).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      '${(confidence * 100).toInt()}%',
                      style: TextStyle(
                        fontSize: 11,
                        color: _getConfidenceColor(confidence),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                ],
                if (sources.isNotEmpty) ...[
                  Icon(Icons.source, size: 12, color: Colors.grey[500]),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      sources.take(2).join(', '),
                      style: TextStyle(
                        fontSize: 11,
                        color: Colors.grey[500],
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
                const Spacer(),
                Text(
                  DateFormat('MMM d, HH:mm').format(timestamp),
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey[500],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Color _getConfidenceColor(double confidence) {
    if (confidence >= 0.8) return Colors.green;
    if (confidence >= 0.6) return Colors.orange;
    return Colors.red;
  }

  Widget _buildRecentDocument(Map<String, dynamic> document) {
    final timestamp = document['timestamp'] != null 
        ? DateTime.fromMillisecondsSinceEpoch(document['timestamp'])
        : DateTime.now();
    final chunks = document['chunks'] ?? document['chunk_count'] ?? 0;
    final type = document['type'] ?? 'document';
    final isSynced = document['is_synced'] as bool? ?? true;
    
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.blue.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            _getDocumentIcon(type),
            color: Colors.blue[600],
            size: 20,
          ),
        ),
        title: Text(
          document['title'],
          style: const TextStyle(
            fontWeight: FontWeight.w500,
            fontSize: 14,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Text(
          '$chunks chunks • $type • ${DateFormat('MMM d, HH:mm').format(timestamp)}',
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (!isSynced) ...[
              Icon(
                Icons.schedule,
                size: 16,
                color: Colors.orange[600],
              ),
              const SizedBox(width: 4),
            ],
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.1),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                'Active',
                style: TextStyle(
                  fontSize: 10,
                  color: Colors.green[700],
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  IconData _getDocumentIcon(String type) {
    switch (type.toLowerCase()) {
      case 'pdf':
        return Icons.picture_as_pdf;
      case 'docx':
      case 'doc':
        return Icons.description;
      case 'text':
      case 'txt':
        return Icons.text_snippet;
      default:
        return Icons.insert_drive_file;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pulse Dashboard'),
        backgroundColor: Colors.purple[600],
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: Icon(_isOnline ? Icons.cloud_done : Icons.cloud_off),
            onPressed: _loadPulseData,
            tooltip: _isOnline ? 'Online' : 'Offline',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadPulseData,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadPulseData,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Offline indicator
                    if (!_isOnline)
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(12),
                        color: Colors.orange[100],
                        child: Row(
                          children: [
                            Icon(Icons.cloud_off, color: Colors.orange[800]),
                            const SizedBox(width: 8),
                            Text(
                              'Offline mode - Showing cached data',
                              style: TextStyle(color: Colors.orange[800]),
                            ),
                          ],
                        ),
                      ),
                    
                    const SizedBox(height: 16),
                    
                    // Stats cards
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Column(
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: _buildStatCard(
                                  title: 'Total Queries',
                                  value: '${_stats['totalQueries'] ?? 0}',
                                  icon: Icons.chat,
                                  color: Colors.blue,
                                  subtitle: _stats['unsyncedMessages'] > 0 
                                      ? '${_stats['unsyncedMessages']} unsynced'
                                      : null,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: _buildStatCard(
                                  title: 'Documents',
                                  value: '${_stats['totalDocuments'] ?? 0}',
                                  icon: Icons.folder,
                                  color: Colors.green,
                                  subtitle: _stats['unsyncedDocuments'] > 0 
                                      ? '${_stats['unsyncedDocuments']} unsynced'
                                      : null,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              Expanded(
                                child: _buildStatCard(
                                  title: 'Avg Confidence',
                                  value: '${(_stats['avgConfidence'] * 100).toInt()}%',
                                  icon: Icons.trending_up,
                                  color: _getConfidenceColor(_stats['avgConfidence'] ?? 0.0),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: _buildStatCard(
                                  title: 'Pending Sync',
                                  value: '${_stats['pendingRetries'] ?? 0}',
                                  icon: Icons.sync,
                                  color: Colors.orange,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // Recent answers section
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Text(
                        'Recent Answers',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    
                    if (_recentMessages.isEmpty)
                      const Padding(
                        padding: EdgeInsets.all(16),
                        child: Center(
                          child: Text(
                            'No recent answers available',
                            style: TextStyle(color: Colors.grey),
                          ),
                        ),
                      )
                    else
                      ...(_recentMessages.take(5).map(_buildRecentMessage)),
                    
                    const SizedBox(height: 24),
                    
                    // Recent documents section
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Text(
                        'Recent Documents',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    
                    if (_recentDocuments.isEmpty)
                      const Padding(
                        padding: EdgeInsets.all(16),
                        child: Center(
                          child: Text(
                            'No recent documents available',
                            style: TextStyle(color: Colors.grey),
                          ),
                        ),
                      )
                    else
                      ...(_recentDocuments.take(5).map(_buildRecentDocument)),
                    
                    const SizedBox(height: 16),
                  ],
                ),
              ),
            ),
    );
  }
}
