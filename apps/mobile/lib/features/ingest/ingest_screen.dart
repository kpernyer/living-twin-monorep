import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../config/app_config.dart';
import '../../services/api_client_enhanced.dart';
import '../../services/auth.dart';
import '../../services/local_storage.dart';

class IngestScreen extends StatefulWidget {
  const IngestScreen({super.key});

  @override
  State<IngestScreen> createState() => _IngestScreenState();
}

class _IngestScreenState extends State<IngestScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final ApiClientEnhanced _apiClient = ApiClientEnhanced(
    baseUrl: AppConfig.apiUrl,
    authService: AuthService(),
  );
  final LocalStorageService _storage = LocalStorageService();
  
  // Text ingest form
  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _textController = TextEditingController();
  
  // State
  List<Map<String, dynamic>> _recentDocuments = [];
  bool _isLoading = false;
  bool _isOnline = true;
  Map<String, dynamic> _offlineStats = {};

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _titleController.dispose();
    _textController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // _isOnline = await _apiClient.isOnline;
      
      // Load recent documents
      // final documentsResponse = await _apiClient.getRecentDocuments();
      final documentsResponse = {'items': []};
      final documents = (documentsResponse['items'] as List? ?? []).map((item) => Map<String, dynamic>.from(item)).toList();
      
      // Load offline stats
      // final stats = await _apiClient.getOfflineStats();
      final stats = <String, dynamic>{};
      
      setState(() {
        _recentDocuments = documents;
        _offlineStats = stats;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading data: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _ingestText() async {
    final title = _titleController.text.trim();
    final text = _textController.text.trim();
    
    if (title.isEmpty || text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter both title and text'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final response = await _apiClient.ingestDocument(
        title: title,
        content: text,
      );

      if (response['success']) {
        _titleController.clear();
        _textController.clear();
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Document ingested successfully! ${response['chunks']} chunks created.'),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['offline'] 
              ? 'Document saved offline. Will sync when online.'
              : 'Error: ${response['error']}'),
            backgroundColor: response['offline'] ? Colors.orange : Colors.red,
          ),
        );
      }
      
      await _loadData(); // Refresh the documents list
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Widget _buildTextIngestTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Offline indicator
          if (!_isOnline)
            Container(
              padding: const EdgeInsets.all(12),
              margin: const EdgeInsets.only(bottom: 16),
              decoration: BoxDecoration(
                color: Colors.orange[100],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.orange[300]!),
              ),
              child: Row(
                children: [
                  Icon(Icons.cloud_off, color: Colors.orange[800]),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Offline mode - Documents will sync when online',
                      style: TextStyle(color: Colors.orange[800]),
                    ),
                  ),
                ],
              ),
            ),
          
          // Title field
          TextField(
            controller: _titleController,
            decoration: const InputDecoration(
              labelText: 'Document Title',
              hintText: 'Enter a descriptive title for your document',
              border: OutlineInputBorder(),
              prefixIcon: Icon(Icons.title),
            ),
            textInputAction: TextInputAction.next,
          ),
          
          const SizedBox(height: 16),
          
          // Text content field
          TextField(
            controller: _textController,
            decoration: const InputDecoration(
              labelText: 'Document Content',
              hintText: 'Paste your domain knowledge here...',
              border: OutlineInputBorder(),
              prefixIcon: Icon(Icons.text_snippet),
              alignLabelWithHint: true,
            ),
            maxLines: 12,
            textInputAction: TextInputAction.newline,
          ),
          
          const SizedBox(height: 24),
          
          // Ingest button
          ElevatedButton.icon(
            onPressed: _isLoading ? null : _ingestText,
            icon: _isLoading 
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.upload),
            label: Text(_isLoading ? 'Ingesting...' : 'Ingest Document'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green[600],
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Quick templates
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Quick Templates',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _buildTemplateChip(
                        'Meeting Notes',
                        'Meeting with [Team] on [Date]\n\nAgenda:\n- \n\nDecisions:\n- \n\nAction Items:\n- ',
                      ),
                      _buildTemplateChip(
                        'Project Update',
                        'Project: [Name]\nStatus: [In Progress/Complete]\n\nProgress:\n- \n\nChallenges:\n- \n\nNext Steps:\n- ',
                      ),
                      _buildTemplateChip(
                        'Knowledge Base',
                        'Topic: [Subject]\n\nOverview:\n[Brief description]\n\nKey Points:\n- \n\nReferences:\n- ',
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTemplateChip(String title, String template) {
    return ActionChip(
      label: Text(title),
      onPressed: () {
        if (_titleController.text.isEmpty) {
          _titleController.text = title;
        }
        _textController.text = template;
      },
      backgroundColor: Colors.blue[50],
      side: BorderSide(color: Colors.blue[200]!),
    );
  }

  Widget _buildRecentDocumentsTab() {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: _recentDocuments.isEmpty
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.folder_open, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text(
                    'No documents ingested yet',
                    style: TextStyle(
                      fontSize: 18,
                      color: Colors.grey,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Start by adding some domain knowledge',
                    style: TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _recentDocuments.length,
              itemBuilder: (context, index) {
                return _buildDocumentCard(_recentDocuments[index]);
              },
            ),
    );
  }

  Widget _buildDocumentCard(Map<String, dynamic> document) {
    final timestamp = document['timestamp'] != null 
        ? DateTime.fromMillisecondsSinceEpoch(document['timestamp'])
        : (document['createdAt'] != null 
            ? DateTime.tryParse(document['createdAt']) ?? DateTime.now()
            : DateTime.now());
    final chunks = document['chunks'] ?? document['chunk_count'] ?? 0;
    final type = document['type'] ?? 'text';
    final isSynced = document['is_synced'] as bool? ?? true;
    
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
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
                    color: _getTypeColor(type).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    _getDocumentIcon(type),
                    color: _getTypeColor(type),
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        document['title'],
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 16,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '$chunks chunks • $type',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
                if (!isSynced) ...[
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.orange[100],
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.schedule,
                          size: 14,
                          color: Colors.orange[700],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          'Pending',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.orange[700],
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ] else ...[
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.green[100],
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.check_circle,
                          size: 14,
                          color: Colors.green[700],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          'Synced',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.green[700],
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(Icons.access_time, size: 16, color: Colors.grey[500]),
                const SizedBox(width: 4),
                Text(
                  DateFormat('MMM d, yyyy • HH:mm').format(timestamp),
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 13,
                  ),
                ),
                const Spacer(),
                if (document['content'] != null)
                  TextButton.icon(
                    onPressed: () => _showDocumentPreview(document),
                    icon: const Icon(Icons.visibility, size: 16),
                    label: const Text('Preview'),
                    style: TextButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 8),
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Color _getTypeColor(String type) {
    switch (type.toLowerCase()) {
      case 'pdf':
        return Colors.red;
      case 'docx':
      case 'doc':
        return Colors.blue;
      case 'text':
      case 'txt':
        return Colors.green;
      default:
        return Colors.grey;
    }
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

  void _showDocumentPreview(Map<String, dynamic> document) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(document['title']),
        content: SizedBox(
          width: double.maxFinite,
          height: 300,
          child: SingleChildScrollView(
            child: Text(
              document['content'] ?? 'No content available',
              style: const TextStyle(fontSize: 14),
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ingest Knowledge'),
        backgroundColor: Colors.green[600],
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(
              icon: Icon(Icons.edit),
              text: 'Add Text',
            ),
            Tab(
              icon: Icon(Icons.folder),
              text: 'Recent',
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(_isOnline ? Icons.cloud_done : Icons.cloud_off),
            onPressed: _loadData,
            tooltip: _isOnline ? 'Online' : 'Offline',
          ),
          if (_offlineStats['pendingRetries'] != null && _offlineStats['pendingRetries'] > 0)
            Padding(
              padding: const EdgeInsets.only(right: 8),
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.orange,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${_offlineStats['pendingRetries']} pending',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildTextIngestTab(),
          _buildRecentDocumentsTab(),
        ],
      ),
    );
  }
}
