import 'dart:async';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:noise_meter/noise_meter.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:speech_to_text/speech_to_text.dart';

enum SpeechState {
  idle,
  listening,
  processing,
  speaking,
  error
}

enum VoiceActivityState {
  silence,
  speaking,
  processing
}

class SpeechResult {
  final String text;
  final double confidence;
  final bool isFinal;
  final Duration duration;

  SpeechResult({
    required this.text,
    required this.confidence,
    required this.isFinal,
    required this.duration,
  });
}

class SpeechService extends ChangeNotifier {
  // Core speech engines
  final SpeechToText _speechToText = SpeechToText();
  final FlutterTts _flutterTts = FlutterTts();
  NoiseMeter? _noiseMeter;

  // State management
  SpeechState _state = SpeechState.idle;
  VoiceActivityState _voiceActivity = VoiceActivityState.silence;
  String _currentTranscription = '';
  double _confidence = 0;
  bool _isInitialized = false;
  Timer? _silenceTimer;
  Timer? _listeningTimer;
  StreamSubscription<NoiseReading>? _noiseSubscription;

  // Configuration
  static const Duration _silenceTimeout = Duration(seconds: 2);
  static const Duration _maxListeningDuration = Duration(seconds: 30);
  static const double _voiceThreshold = 20; // dB threshold for voice activity
  static const double _confidenceThreshold = 0.7;

  // Getters
  SpeechState get state => _state;
  VoiceActivityState get voiceActivity => _voiceActivity;
  String get currentTranscription => _currentTranscription;
  double get confidence => _confidence;
  bool get isInitialized => _isInitialized;
  bool get isListening => _state == SpeechState.listening;
  bool get isSpeaking => _state == SpeechState.speaking;
  bool get canListen => _isInitialized && (_state == SpeechState.idle || _state == SpeechState.error);

  // Events
  final StreamController<SpeechResult> _speechResultController = StreamController<SpeechResult>.broadcast();
  final StreamController<String> _partialResultController = StreamController<String>.broadcast();
  final StreamController<SpeechState> _stateController = StreamController<SpeechState>.broadcast();

  Stream<SpeechResult> get onSpeechResult => _speechResultController.stream;
  Stream<String> get onPartialResult => _partialResultController.stream;
  Stream<SpeechState> get onStateChanged => _stateController.stream;

  /// Initialize the speech service with hardware-optimized settings
  Future<bool> initialize() async {
    if (_isInitialized) return true;

    try {
      // Request permissions
      final micPermission = await Permission.microphone.request();
      if (!micPermission.isGranted) {
        debugPrint('Microphone permission denied');
        return false;
      }

      // Initialize Speech-to-Text with hardware acceleration
      final sttAvailable = await _speechToText.initialize(
        onError: _onSpeechError,
        onStatus: _onSpeechStatus,
        debugLogging: kDebugMode,
        finalTimeout: _silenceTimeout,
      );

      if (!sttAvailable) {
        debugPrint('Speech recognition not available');
        return false;
      }

      // Configure TTS for natural speech
      await _configureTts();

      // Initialize sound level monitoring
      await _initializeSoundLevel();

      _isInitialized = true;
      debugPrint('Speech service initialized successfully');
      return true;
    } catch (e) {
      debugPrint('Failed to initialize speech service: $e');
      return false;
    }
  }

  /// Configure TTS with optimal settings for natural conversation
  Future<void> _configureTts() async {
    await _flutterTts.setLanguage('en-US');
    
    // Platform-specific optimizations
    if (Platform.isIOS) {
      // Use iOS Neural voices for better quality
      await _flutterTts.setVoice({
        'name': 'com.apple.voice.compact.en-US.Samantha',
        'locale': 'en-US'
      });
      await _flutterTts.setSpeechRate(0.5); // Natural pace
      await _flutterTts.setPitch(1);
      await _flutterTts.setVolume(0.8);
      
      // iOS-specific settings for better quality
      await _flutterTts.setSharedInstance(true);
      await _flutterTts.setIosAudioCategory(
        IosTextToSpeechAudioCategory.playback,
        [IosTextToSpeechAudioCategoryOptions.allowBluetooth],
        IosTextToSpeechAudioMode.spokenAudio,
      );
    } else if (Platform.isAndroid) {
      // Use Android Neural Network TTS
      await _flutterTts.setEngine('com.google.android.tts');
      await _flutterTts.setSpeechRate(0.5);
      await _flutterTts.setPitch(1);
      await _flutterTts.setVolume(0.8);
      
      // Android-specific optimizations
      await _flutterTts.setQueueMode(1); // Flush mode for immediate response
    }

    // Set up TTS callbacks
    _flutterTts.setStartHandler(() {
      _setState(SpeechState.speaking);
    });

    _flutterTts.setCompletionHandler(() {
      _setState(SpeechState.idle);
    });

    _flutterTts.setErrorHandler((msg) {
      debugPrint('TTS Error: $msg');
      _setState(SpeechState.error);
    });
  }

  /// Initialize sound level monitoring for voice activity detection
  Future<void> _initializeSoundLevel() async {
    try {
      _noiseMeter = NoiseMeter();
      _noiseSubscription = _noiseMeter?.noise.listen((NoiseReading noiseReading) {
        _updateVoiceActivity(noiseReading.meanDecibel);
      });
    } catch (e) {
      debugPrint('Sound level monitoring not available: $e');
    }
  }

  /// Start listening for speech with voice activity detection
  Future<bool> startListening({
    String? localeId,
    Duration? timeout,
  }) async {
    if (!_isInitialized || !canListen) return false;

    try {
      _setState(SpeechState.listening);
      _currentTranscription = '';
      _confidence = 0.0;

      // Start listening with optimized settings
      final success = await _speechToText.listen(
        onResult: _onSpeechResult,
        listenFor: timeout ?? _maxListeningDuration,
        pauseFor: _silenceTimeout,
        partialResults: true,
        localeId: localeId ?? 'en_US',
        onSoundLevelChange: _onSoundLevelChange,
        cancelOnError: false,
        listenMode: ListenMode.confirmation, // Better for conversational flow
      );

      if (success) {
        _startListeningTimer();
        return true;
      } else {
        _setState(SpeechState.error);
        return false;
      }
    } catch (e) {
      debugPrint('Failed to start listening: $e');
      _setState(SpeechState.error);
      return false;
    }
  }

  /// Stop listening and return final result
  Future<SpeechResult?> stopListening() async {
    if (!isListening) return null;

    try {
      await _speechToText.stop();
      _cancelTimers();
      
      if (_currentTranscription.isNotEmpty && _confidence >= _confidenceThreshold) {
        final result = SpeechResult(
          text: _currentTranscription.trim(),
          confidence: _confidence,
          isFinal: true,
          duration: Duration.zero, // Will be set by caller
        );
        
        _speechResultController.add(result);
        return result;
      }
      
      return null;
    } catch (e) {
      debugPrint('Failed to stop listening: $e');
      _setState(SpeechState.error);
      return null;
    }
  }

  /// Speak text with natural flow and interruption handling
  Future<bool> speak(String text, {bool interruptible = true}) async {
    if (!_isInitialized || text.isEmpty) return false;

    try {
      // Stop any current speech if interruptible
      if (isSpeaking && interruptible) {
        await _flutterTts.stop();
      }

      _setState(SpeechState.speaking);
      
      // Break long text into natural chunks for better flow
      final chunks = _breakIntoChunks(text);
      
      for (final chunk in chunks) {
        if (_state != SpeechState.speaking) break; // Check for interruption
        await _flutterTts.speak(chunk);
        
        // Small pause between chunks for natural flow
        if (chunks.length > 1) {
          await Future.delayed(const Duration(milliseconds: 200));
        }
      }
      
      return true;
    } catch (e) {
      debugPrint('Failed to speak: $e');
      _setState(SpeechState.error);
      return false;
    }
  }

  /// Stop current speech
  Future<void> stopSpeaking() async {
    if (isSpeaking) {
      await _flutterTts.stop();
      _setState(SpeechState.idle);
    }
  }

  /// Cancel current listening session
  Future<void> cancelListening() async {
    if (isListening) {
      await _speechToText.cancel();
      _cancelTimers();
      _setState(SpeechState.idle);
    }
  }

  /// Get available languages for speech recognition
  Future<List<LocaleName>> getAvailableLanguages() async {
    if (!_isInitialized) return [];
    return _speechToText.locales();
  }

  /// Get available voices for text-to-speech
  Future<List<dynamic>> getAvailableVoices() async {
    return await _flutterTts.getVoices;
  }

  /// Set TTS voice
  Future<void> setVoice(Map<String, String> voice) async {
    await _flutterTts.setVoice(voice);
  }

  /// Set speech rate (0.0 to 1.0)
  Future<void> setSpeechRate(double rate) async {
    await _flutterTts.setSpeechRate(rate.clamp(0.0, 1.0));
  }

  // Private methods

  void _setState(SpeechState newState) {
    if (_state != newState) {
      _state = newState;
      _stateController.add(_state);
      notifyListeners();
    }
  }

  void _updateVoiceActivity(double soundLevel) {
    final newActivity = soundLevel > _voiceThreshold 
        ? VoiceActivityState.speaking 
        : VoiceActivityState.silence;
    
    if (_voiceActivity != newActivity) {
      _voiceActivity = newActivity;
      notifyListeners();
    }
  }

  void _onSpeechResult(result) {
    _currentTranscription = result.recognizedWords;
    _confidence = result.confidence;
    
    if (result.finalResult) {
      _setState(SpeechState.processing);
      
      final speechResult = SpeechResult(
        text: result.recognizedWords.trim(),
        confidence: result.confidence,
        isFinal: true,
        duration: Duration.zero,
      );
      
      _speechResultController.add(speechResult);
      _setState(SpeechState.idle);
    } else {
      // Emit partial results for real-time feedback
      _partialResultController.add(result.recognizedWords);
    }
    
    notifyListeners();
  }

  void _onSpeechError(error) {
    debugPrint('Speech recognition error: ${error.errorMsg}');
    _setState(SpeechState.error);
    
    // Auto-recover from temporary errors
    if (error.permanent == false) {
      Timer(const Duration(seconds: 1), () {
        if (_state == SpeechState.error) {
          _setState(SpeechState.idle);
        }
      });
    }
  }

  void _onSpeechStatus(String status) {
    debugPrint('Speech status: $status');
    
    switch (status) {
      case 'listening':
        _setState(SpeechState.listening);
        break;
      case 'notListening':
        if (_state == SpeechState.listening) {
          _setState(SpeechState.idle);
        }
        break;
      case 'done':
        _setState(SpeechState.idle);
        break;
    }
  }

  void _onSoundLevelChange(double level) {
    _updateVoiceActivity(level);
    
    // Reset silence timer when voice is detected
    if (level > _voiceThreshold && _silenceTimer?.isActive == true) {
      _silenceTimer?.cancel();
    }
  }

  void _startListeningTimer() {
    _listeningTimer = Timer(_maxListeningDuration, () {
      if (isListening) {
        stopListening();
      }
    });
  }

  void _cancelTimers() {
    _silenceTimer?.cancel();
    _listeningTimer?.cancel();
  }

  /// Break long text into natural speaking chunks
  List<String> _breakIntoChunks(String text, {int maxChunkLength = 200}) {
    if (text.length <= maxChunkLength) return [text];
    
    final chunks = <String>[];
    final sentences = text.split(RegExp('[.!?]+'));
    
    var currentChunk = '';
    for (final sentence in sentences) {
      if (sentence.trim().isEmpty) continue;
      
      final trimmedSentence = sentence.trim();
      if (currentChunk.length + trimmedSentence.length > maxChunkLength) {
        if (currentChunk.isNotEmpty) {
          chunks.add(currentChunk.trim());
          currentChunk = '';
        }
      }
      
      currentChunk += (currentChunk.isEmpty ? '' : '. ') + trimmedSentence;
    }
    
    if (currentChunk.isNotEmpty) {
      chunks.add(currentChunk.trim());
    }
    
    return chunks.isEmpty ? [text] : chunks;
  }

  @override
  void dispose() {
    _speechResultController.close();
    _partialResultController.close();
    _stateController.close();
    _noiseSubscription?.cancel();
    _cancelTimers();
    super.dispose();
  }
}
