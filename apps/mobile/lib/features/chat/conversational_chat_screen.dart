import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/speech_service.dart';
import '../../services/api_client_enhanced.dart';
import '../../services/local_storage.dart';
import '../../services/auth.dart';
import '../../config/app_config.dart';

class ConversationalChatScreen extends StatefulWidget {
  const ConversationalChatScreen({super.key});

  @override
  State<ConversationalChatScreen> createState() => _ConversationalChatScreenState();
}

class _ConversationalChatScreenState extends State<ConversationalChatScreen>
    with TickerProviderStateMixin {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  
  late SpeechService _speechService;
  late ApiClientEnhanced _apiClient;
  late LocalStorageService _localStorage;
  
  String? _currentConversationId;
  bool _isLoading = false;
  bool _isListening = false;
  bool _isSpeaking = false;
  String _partialTranscription = '';
  
  // Animation controllers for visual feedback
  late AnimationController _pulseController;
  late AnimationController _waveController;
  late Animation<double> _pulseAnimation;
  late Animation<double> _waveAnimation;

  @override
  void initState() {
    super.initState();
    _initializeServices();
    _setupAnimations();
    _loadConversationHistory();
  }

  void _initializeServices() {
    _speechService = SpeechService();
    _apiClient = ApiClientEnhanced(
      baseUrl: AppConfig.apiUrl,
      authService: AuthService(),
    );
    _localStorage = LocalStorageService();
    
    // Initialize speech service
    _speechService.initialize().then((success) {
      if (!success) {
        _showError('Speech recognition not available');
      }
    });
    
    // Listen to speech events
    _speechService.onSpeechResult.listen(_handleSpeechResult);
    _speechService.onPartialResult.listen(_handlePartialResult);
    _speechService.onStateChanged.listen(_handleSpeechStateChange);
  }

  void _setupAnimations() {
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    
    _waveController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );
    
    _pulseAnimation = Tween<double>(
      begin: 0.8,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));
    
    _waveAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _waveController,
      curve: Curves.easeInOut,
    ));
  }

  Future<void> _loadConversationHistory() async {
    try {
      final messages = await _localStorage.getChatMessages();
      if (messages.isNotEmpty) {
        setState(() {
          _messages.clear();
          _messages.addAll(messages.map((msg) => ChatMessage.fromMap(msg)));
        });
        
        _scrollToBottom();
      }
    } catch (e) {
      debugPrint('Failed to load conversation history: $e');
    }
  }

  void _handleSpeechResult(SpeechResult result) {
    if (result.isFinal && result.text.isNotEmpty) {
      _sendMessage(result.text);
      setState(() {
        _partialTranscription = '';
      });
    }
  }

  void _handlePartialResult(String partial) {
    setState(() {
      _partialTranscription = partial;
    });
  }

  void _handleSpeechStateChange(SpeechState state) {
    setState(() {
      _isListening = state == SpeechState.listening;
      _isSpeaking = state == SpeechState.speaking;
    });
    
    // Update animations based on state
    switch (state) {
      case SpeechState.listening:
        _pulseController.repeat(reverse: true);
        _waveController.repeat();
        break;
      case SpeechState.speaking:
        _pulseController.repeat(reverse: true);
        _waveController.stop();
        break;
      case SpeechState.idle:
      case SpeechState.error:
        _pulseController.stop();
        _waveController.stop();
        break;
      case SpeechState.processing:
        _pulseController.stop();
        _waveController.repeat();
        break;
    }
  }

  Future<void> _sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    final userMessage = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      text: text.trim(),
      isUser: true,
      timestamp: DateTime.now(),
    );

    setState(() {
      _messages.add(userMessage);
      _isLoading = true;
    });

    _scrollToBottom();
    _textController.clear();

    try {
      // Use conversational query API
      final response = await _apiClient.conversationalQuery(
        question: text.trim(),
        conversationId: _currentConversationId,
      );

      if (response['success']) {
        _currentConversationId = response['conversationId'];
        
        final assistantMessage = ChatMessage(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          text: response['answer'],
          isUser: false,
          timestamp: DateTime.now(),
          sources: List<String>.from(response['sources'] ?? []),
          confidence: response['confidence']?.toDouble() ?? 0.0,
        );

        setState(() {
          _messages.add(assistantMessage);
        });

        // Save conversation locally
        await _localStorage.saveChatMessage(
          question: text.trim(),
          answer: response['answer'],
          confidence: response['confidence']?.toDouble(),
          sources: response['sources'] != null ? List<String>.from(response['sources']) : null,
        );

        // Speak the response if speech is enabled
        if (_speechService.isInitialized) {
          await _speechService.speak(response['answer']);
        }

        _scrollToBottom();
      } else {
        _showError(response['error'] ?? 'Failed to get response');
      }
    } catch (e) {
      _showError('Network error: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _startListening() async {
    if (!_speechService.canListen) return;
    
    final success = await _speechService.startListening();
    if (!success) {
      _showError('Failed to start listening');
    }
  }

  Future<void> _stopListening() async {
    await _speechService.stopListening();
  }

  Future<void> _stopSpeaking() async {
    await _speechService.stopSpeaking();
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

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  Widget _buildVoiceButton() {
    return AnimatedBuilder(
      animation: Listenable.merge([_pulseAnimation, _waveAnimation]),
      builder: (context, child) {
        return Transform.scale(
          scale: _isListening ? _pulseAnimation.value : 1.0,
          child: Container(
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: _isListening
                  ? RadialGradient(
                      colors: [
                        Colors.blue.withOpacity(0.3),
                        Colors.blue.withOpacity(0.1),
                        Colors.transparent,
                      ],
                      stops: [0.3, 0.7, 1.0],
                    )
                  : null,
            ),
            child: FloatingActionButton(
              onPressed: _isListening ? _stopListening : _startListening,
              backgroundColor: _isListening ? Colors.red : Colors.blue,
              child: Icon(
                _isListening ? Icons.mic : Icons.mic_none,
                color: Colors.white,
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildPartialTranscription() {
    if (_partialTranscription.isEmpty) return const SizedBox.shrink();
    
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.mic, color: Colors.blue, size: 16),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              _partialTranscription,
              style: TextStyle(
                color: Colors.blue.shade700,
                fontStyle: FontStyle.italic,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSpeechStatus() {
    if (!_isListening && !_isSpeaking) return const SizedBox.shrink();
    
    String statusText;
    Color statusColor;
    IconData statusIcon;
    
    if (_isListening) {
      statusText = 'Listening...';
      statusColor = Colors.blue;
      statusIcon = Icons.mic;
    } else {
      statusText = 'Speaking...';
      statusColor = Colors.green;
      statusIcon = Icons.volume_up;
    }
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(statusIcon, color: statusColor, size: 16),
          const SizedBox(width: 8),
          Text(
            statusText,
            style: TextStyle(
              color: statusColor,
              fontWeight: FontWeight.w500,
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
        title: const Text('Living Twin Chat'),
        actions: [
          if (_isSpeaking)
            IconButton(
              icon: const Icon(Icons.stop),
              onPressed: _stopSpeaking,
              tooltip: 'Stop speaking',
            ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {
                _messages.clear();
                _currentConversationId = null;
              });
            },
            tooltip: 'New conversation',
          ),
        ],
      ),
      body: Column(
        children: [
          _buildSpeechStatus(),
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length + (_isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (index == _messages.length) {
                  return const ChatBubble.loading();
                }
                return ChatBubble(message: _messages[index]);
              },
            ),
          ),
          _buildPartialTranscription(),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).scaffoldBackgroundColor,
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
                    controller: _textController,
                    decoration: InputDecoration(
                      hintText: 'Ask your organizational twin...',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                    ),
                    onSubmitted: _sendMessage,
                    enabled: !_isLoading && !_isListening,
                  ),
                ),
                const SizedBox(width: 8),
                _buildVoiceButton(),
                const SizedBox(width: 8),
                FloatingActionButton(
                  mini: true,
                  onPressed: _isLoading || _isListening
                      ? null
                      : () => _sendMessage(_textController.text),
                  child: const Icon(Icons.send),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    _pulseController.dispose();
    _waveController.dispose();
    _speechService.dispose();
    super.dispose();
  }
}

class ChatMessage {
  final String id;
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final List<String>? sources;
  final double? confidence;

  ChatMessage({
    required this.id,
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.sources,
    this.confidence,
  });

  factory ChatMessage.fromMap(Map<String, dynamic> map) {
    return ChatMessage(
      id: map['id'] ?? '',
      text: map['text'] ?? '',
      isUser: map['is_user'] ?? false,
      timestamp: DateTime.fromMillisecondsSinceEpoch(map['timestamp'] ?? 0),
      sources: map['sources'] != null ? List<String>.from(map['sources']) : null,
      confidence: map['confidence']?.toDouble(),
    );
  }
}

class ChatBubble extends StatelessWidget {
  final ChatMessage? message;
  final bool isLoading;

  const ChatBubble({
    super.key,
    this.message,
    this.isLoading = false,
  });

  const ChatBubble.loading({super.key})
      : message = null,
        isLoading = true;

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return Container(
        margin: const EdgeInsets.only(bottom: 16),
        child: Row(
          children: [
            const CircleAvatar(
              backgroundColor: Colors.grey,
              child: Icon(Icons.smart_toy, color: Colors.white),
            ),
            const SizedBox(width: 12),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey.shade200,
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  SizedBox(width: 8),
                  Text('Thinking...'),
                ],
              ),
            ),
          ],
        ),
      );
    }

    final msg = message!;
    final isUser = msg.isUser;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) ...[
            CircleAvatar(
              backgroundColor: Colors.blue,
              child: Icon(
                Icons.smart_toy,
                color: Colors.white,
              ),
            ),
            const SizedBox(width: 12),
          ],
          Flexible(
            child: Column(
              crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: isUser ? Colors.blue : Colors.grey.shade200,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    msg.text,
                    style: TextStyle(
                      color: isUser ? Colors.white : Colors.black87,
                    ),
                  ),
                ),
                if (!isUser && msg.sources != null && msg.sources!.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Sources:',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: Colors.blue.shade700,
                          ),
                        ),
                        ...msg.sources!.take(3).map((source) => Text(
                              '• $source',
                              style: TextStyle(
                                fontSize: 11,
                                color: Colors.blue.shade600,
                              ),
                            )),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 4),
                Text(
                  _formatTime(msg.timestamp),
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 12),
            CircleAvatar(
              backgroundColor: Colors.green,
              child: Icon(
                Icons.person,
                color: Colors.white,
              ),
            ),
          ],
        ],
      ),
    );
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final difference = now.difference(time);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h ago';
    } else {
      return '${time.day}/${time.month} ${time.hour}:${time.minute.toString().padLeft(2, '0')}';
    }
  }
}
