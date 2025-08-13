import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../services/api_client_enhanced.dart';
import '../../services/local_storage.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final ApiClientEnhanced _apiClient = ApiClientEnhanced();
  final LocalStorageService _storage = LocalStorageService();
  
  List<Map<String, dynamic>> _messages = [];
  bool _isLoading = false;
  bool _isOnline = true;
  Map<String, dynamic> _offlineStats = {};

  @override
  void initState() {
    super.initState();
    _loadMessages();
    _checkConnectivity();
    _loadOfflineStats();
  }

  Future<void> _loadMessages() async {
    final messages = await _storage.getChatMessages();
    setState(() {
      _messages = messages;
    });
    _scrollToBottom();
  }

  Future<void> _checkConnectivity() async {
    final isOnline = await _apiClient.isOnline;
    setState(() {
      _isOnline = isOnline;
    });
    
    if (isOnline) {
      // Process retry queue when coming back online
      await _apiClient.processRetryQueue();
      await _loadMessages(); // Refresh to show synced messages
      await _loadOfflineStats();
    }
  }

  Future<void> _loadOfflineStats() async {
    final stats = await _apiClient.getOfflineStats();
    setState(() {
      _offlineStats = stats;
    });
  }

  Future<void> _sendMessage() async {
    final question = _controller.text.trim();
    if (question.isEmpty) return;

    _controller.clear();
    setState(() {
      _isLoading = true;
    });

    try {
      final response = await _apiClient.query(question: question);
      
      if (response['success']) {
        // Message was successfully processed
        await _loadMessages();
      } else {
        // Message was saved offline or failed
        await _loadMessages();
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(response['offline'] 
                ? 'Message saved offline. Will sync when online.'
                : 'Error: ${response['error']}'),
              backgroundColor: response['offline'] ? Colors.orange : Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
      await _loadOfflineStats();
    }

    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Widget _buildMessage(Map<String, dynamic> message) {
    final isUser = message['answer'] == null;
    final timestamp = DateTime.fromMillisecondsSinceEpoch(message['timestamp']);
    final isSynced = message['is_synced'] as bool;
    
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
      child: Column(
        crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          Container(
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.8,
            ),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: isUser ? Colors.blue[600] : Colors.grey[200],
              borderRadius: BorderRadius.circular(18),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isUser ? message['question'] : (message['answer'] ?? 'Processing...'),
                  style: TextStyle(
                    color: isUser ? Colors.white : Colors.black87,
                    fontSize: 16,
                  ),
                ),
                if (!isUser && message['confidence'] != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    'Confidence: ${(message['confidence'] * 100).toInt()}%',
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                    ),
                  ),
                ],
                if (!isUser && message['sources'] != null && (message['sources'] as List).isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    'Sources: ${(message['sources'] as List).join(', ')}',
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: 2),
          Row(
            mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
            children: [
              Text(
                DateFormat('HH:mm').format(timestamp),
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 12,
                ),
              ),
              if (!isSynced) ...[
                const SizedBox(width: 4),
                Icon(
                  Icons.schedule,
                  size: 12,
                  color: Colors.orange[600],
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildOfflineIndicator() {
    if (_isOnline) return const SizedBox.shrink();
    
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: Colors.orange[100],
      child: Row(
        children: [
          Icon(Icons.cloud_off, size: 16, color: Colors.orange[800]),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'Offline mode - Messages will sync when online',
              style: TextStyle(
                color: Colors.orange[800],
                fontSize: 14,
              ),
            ),
          ),
          if (_offlineStats['pendingRetries'] != null && _offlineStats['pendingRetries'] > 0)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.orange[600],
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                '${_offlineStats['pendingRetries']} pending',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                ),
              ),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Chat with Twin'),
        backgroundColor: Colors.blue[600],
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: Icon(_isOnline ? Icons.cloud_done : Icons.cloud_off),
            onPressed: _checkConnectivity,
            tooltip: _isOnline ? 'Online' : 'Offline',
          ),
          PopupMenuButton<String>(
            onSelected: (value) async {
              switch (value) {
                case 'refresh':
                  await _checkConnectivity();
                  await _loadMessages();
                  break;
                case 'stats':
                  _showOfflineStats();
                  break;
                case 'clear':
                  _showClearDialog();
                  break;
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'refresh',
                child: Row(
                  children: [
                    Icon(Icons.refresh),
                    SizedBox(width: 8),
                    Text('Refresh'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'stats',
                child: Row(
                  children: [
                    Icon(Icons.info),
                    SizedBox(width: 8),
                    Text('Offline Stats'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'clear',
                child: Row(
                  children: [
                    Icon(Icons.clear_all),
                    SizedBox(width: 8),
                    Text('Clear Chat'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          _buildOfflineIndicator(),
          Expanded(
            child: _messages.isEmpty
                ? const Center(
                    child: Text(
                      'Start a conversation with your Living Twin',
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey,
                      ),
                    ),
                  )
                : ListView.builder(
                    controller: _scrollController,
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      return _buildMessage(_messages[index]);
                    },
                  ),
          ),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  offset: const Offset(0, -2),
                  blurRadius: 4,
                  color: Colors.black.withOpacity(0.1),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: 'Ask your Living Twin...',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                    ),
                    maxLines: null,
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 8),
                FloatingActionButton(
                  onPressed: _isLoading ? null : _sendMessage,
                  mini: true,
                  backgroundColor: Colors.blue[600],
                  child: _isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Icon(Icons.send, color: Colors.white),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showOfflineStats() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Offline Statistics'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Status: ${_offlineStats['isOnline'] ? 'Online' : 'Offline'}'),
            const SizedBox(height: 8),
            Text('Total Messages: ${_offlineStats['totalMessages'] ?? 0}'),
            Text('Unsynced Messages: ${_offlineStats['unsyncedMessages'] ?? 0}'),
            const SizedBox(height: 8),
            Text('Total Documents: ${_offlineStats['totalDocuments'] ?? 0}'),
            Text('Unsynced Documents: ${_offlineStats['unsyncedDocuments'] ?? 0}'),
            const SizedBox(height: 8),
            Text('Pending Retries: ${_offlineStats['pendingRetries'] ?? 0}'),
          ],
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

  void _showClearDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear Chat History'),
        content: const Text('This will clear all chat messages from local storage. Are you sure?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.of(context).pop();
              // Clear chat messages (implementation would go in LocalStorageService)
              await _storage.clearOldData(daysToKeep: 0);
              await _loadMessages();
              await _loadOfflineStats();
            },
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }
}
