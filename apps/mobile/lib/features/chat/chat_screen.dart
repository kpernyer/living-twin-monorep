import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:speech_to_text/speech_to_text.dart';
import '../../personalization/personalization_layer.dart';
import '../../personalization/personalization_service.dart';
import '../../services/api_client_enhanced.dart';
import '../../services/local_storage.dart';
import '../../services/auth.dart';
import '../../config/app_config.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> with SingleTickerProviderStateMixin {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  late final ApiClientEnhanced _apiClient;
  final LocalStorageService _storage = LocalStorageService();
  final PersonalizationService _personalizationService = PersonalizationLayer();
  
  List<Map<String, dynamic>> _messages = [];
  bool _isLoading = false;
  bool _isOnline = true;
  Map<String, dynamic> _offlineStats = {};
  final SpeechToText _speechToText = SpeechToText();
  bool _isListening = false;

  List<String> _todoItems = [];
  List<String> _sampleQuestions = [];

  AnimationController? _animationController;
  Animation<int>? _textAnimation;

  @override
  void initState() {
    super.initState();
    _apiClient = ApiClientEnhanced(
      baseUrl: AppConfig.apiUrl,
      authService: AuthService(),
    );
    _initSpeech();
    _loadMessages();
    _checkConnectivity();
    _loadOfflineStats();
    _loadPersonalizedData();
  }

  Future<void> _loadPersonalizedData() async {
    final todos = await _personalizationService.getTodoItems();
    final questions = await _personalizationService.getSampleQuestions();
    setState(() {
      _todoItems = todos;
      _sampleQuestions = questions;
    });

    if (_sampleQuestions.isNotEmpty) {
      _animationController = AnimationController(
        vsync: this,
        duration: const Duration(seconds: 5),
      )..repeat();
      _textAnimation = StepTween(begin: 0, end: _sampleQuestions.length - 1).animate(_animationController!);
    }
  }

  void _initSpeech() async {
    await _speechToText.initialize();
    setState(() {});
  }

  Future<void> _loadMessages() async {
    final messages = await _storage.getChatMessages();
    setState(() {
      _messages = messages;
    });
    _scrollToBottom();
  }

  Future<void> _checkConnectivity() async {
    final connectivityResult = await Connectivity().checkConnectivity();
    final isOnline = connectivityResult != ConnectivityResult.none;
    
    // Also check if the server is actually reachable
    bool serverReachable = false;
    if (isOnline) {
      try {
        final response = await _apiClient.healthCheck();
        serverReachable = response['success'] == true;
      } catch (e) {
        serverReachable = false;
      }
    }
    
    setState(() {
      _isOnline = isOnline && serverReachable;
    });
    
    if (_isOnline) {
      // Refresh messages when coming back online
      await _loadMessages();
      await _loadOfflineStats();
    }
  }

  Future<void> _loadOfflineStats() async {
    // Mock offline stats for now
    final stats = {
      'totalMessages': _messages.length,
      'unsyncedMessages': 0,
      'isOnline': _isOnline,
    };
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
      
      // Debug: Print the response to see what we're getting
      print('API Response: $response');
      
      // Handle null safety for response fields
      final success = response['success'] as bool? ?? false;
      final isOffline = response['offline'] as bool? ?? false;
      final error = response['error'] as String?;
      
      print('Parsed values - success: $success, isOffline: $isOffline, error: $error');
      
      if (success) {
        // Message was successfully processed
        await _loadMessages();
      } else {
        // Save message locally if server is not available
        if (isOffline || (error != null && error.contains('Connection refused'))) {
          await _saveMessageLocally(question, 'Server not available. Message saved locally.');
        }
        
        await _loadMessages();
        
        if (mounted) {
          // Provide user-friendly error messages
          String userMessage;
          Color backgroundColor;
          
          if (isOffline) {
            userMessage = 'Message saved locally. Will sync when server is available.';
            backgroundColor = Colors.orange;
          } else if (error != null && error.contains('Connection refused')) {
            userMessage = 'Server not available. Message saved locally.';
            backgroundColor = Colors.orange;
          } else if (error != null && error.contains('Network error')) {
            userMessage = 'Network connection issue. Please check your internet connection.';
            backgroundColor = Colors.red;
          } else {
            userMessage = 'Error: ${error ?? 'Unknown error occurred'}';
            backgroundColor = Colors.red;
          }
          
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(userMessage),
              backgroundColor: backgroundColor,
              duration: const Duration(seconds: 4),
              action: SnackBarAction(
                label: 'Retry',
                textColor: Colors.white,
                onPressed: () => _sendMessage(),
              ),
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

  Future<void> _saveMessageLocally(String question, String answer) async {
    await _storage.saveChatMessage(
      question: question,
      answer: answer,
    );
  }

  void _listen() async {
    if (!_isListening) {
      bool available = await _speechToText.initialize(
        onStatus: (val) => print('onStatus: $val'),
        onError: (val) => print('onError: $val'),
      );
      if (available) {
        setState(() => _isListening = true);
        _speechToText.listen(
          onResult: (val) => setState(() {
            _controller.text = val.recognizedWords;
          }),
        );
      }
    } else {
      setState(() => _isListening = false);
      _speechToText.stop();
    }
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
    final isSynced = message['is_synced'] as bool? ?? true;
    final isLocal = message['is_local'] as bool? ?? false;
    
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
              if (!isSynced || isLocal) ...[
                const SizedBox(width: 4),
                Icon(
                  isLocal ? Icons.save : Icons.schedule,
                  size: 12,
                  color: isLocal ? Colors.blue[600] : Colors.orange[600],
                ),
                const SizedBox(width: 2),
                Text(
                  isLocal ? 'Local' : 'Pending',
                  style: TextStyle(
                    color: isLocal ? Colors.blue[600] : Colors.orange[600],
                    fontSize: 10,
                  ),
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
              'Server not available - Messages will be saved locally',
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
  void dispose() {
    _animationController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Living Twin Chat'),
        actions: [
          IconButton(
            icon: Icon(_isOnline ? Icons.cloud_done : Icons.cloud_off),
            tooltip: _isOnline ? 'Connected to server' : 'Server not available',
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(_isOnline 
                    ? 'Connected to Living Twin server' 
                    : 'Server not available. Check your connection.'),
                  duration: const Duration(seconds: 2),
                ),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh connection',
            onPressed: _isLoading ? null : () async {
              setState(() {
                _isLoading = true;
              });
              await _checkConnectivity();
              await _loadMessages();
              await _loadOfflineStats();
              setState(() {
                _isLoading = false;
              });
            },
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              switch (value) {
                case 'clear':
                  _showClearDialog();
                  break;
                case 'stats':
                  _showOfflineStats();
                  break;
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'stats',
                child: Row(
                  children: [
                    Icon(Icons.analytics),
                    SizedBox(width: 8),
                    Text('View Statistics'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'clear',
                child: Row(
                  children: [
                    Icon(Icons.clear_all),
                    SizedBox(width: 8),
                    Text('Clear History'),
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
                ? Center(
                    child: _textAnimation != null
                        ? AnimatedBuilder(
                            animation: _textAnimation!,
                            builder: (context, child) {
                              return Text(
                                _sampleQuestions[_textAnimation!.value],
                                style: const TextStyle(
                                  fontSize: 18,
                                  color: Colors.grey,
                                ),
                                textAlign: TextAlign.center,
                              );
                            },
                          )
                        : const Text(
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
                IconButton(
                  icon: const Icon(Icons.add),
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Attach functionality coming soon!'),
                      ),
                    );
                  },
                ),
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
                IconButton(
                  icon: Icon(_isListening ? Icons.mic_off : Icons.mic),
                  onPressed: _listen,
                ),
                FloatingActionButton(
                  onPressed: _isLoading ? null : _sendMessage,
                  mini: true,
                  heroTag: "chat_send_button", // Add unique hero tag
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
