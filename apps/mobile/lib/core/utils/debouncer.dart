import 'dart:async';
import 'package:rxdart/rxdart.dart';

/// Debouncer for preventing excessive API calls or UI updates
class Debouncer {
  final Duration delay;
  Timer? _timer;
  
  Debouncer({
    this.delay = const Duration(milliseconds: 500),
  });
  
  /// Run a function after the delay period
  /// Cancels any previous calls within the delay window
  void run(void Function() action) {
    _timer?.cancel();
    _timer = Timer(delay, action);
  }
  
  /// Cancel any pending debounced actions
  void cancel() {
    _timer?.cancel();
  }
  
  /// Dispose of the timer
  void dispose() {
    _timer?.cancel();
    _timer = null;
  }
  
  /// Check if there's a pending action
  bool get isActive => _timer?.isActive ?? false;
}

/// Stream-based debouncer using RxDart
class StreamDebouncer<T> {
  final Duration delay;
  final _subject = BehaviorSubject<T>();
  late final Stream<T> stream;
  
  StreamDebouncer({
    this.delay = const Duration(milliseconds: 500),
  }) {
    stream = _subject.debounceTime(delay);
  }
  
  /// Add value to be debounced
  void add(T value) {
    _subject.add(value);
  }
  
  /// Get the current value
  T? get value => _subject.valueOrNull;
  
  /// Listen to debounced values
  StreamSubscription<T> listen(
    void Function(T value) onData, {
    Function? onError,
    void Function()? onDone,
    bool? cancelOnError,
  }) {
    return stream.listen(
      onData,
      onError: onError,
      onDone: onDone,
      cancelOnError: cancelOnError,
    );
  }
  
  /// Dispose of the stream
  void dispose() {
    _subject.close();
  }
}

/// Throttler for limiting the rate of function calls
class Throttler {
  final Duration delay;
  Timer? _timer;
  bool _isThrottling = false;
  void Function()? _pendingAction;
  
  Throttler({
    this.delay = const Duration(milliseconds: 1000),
  });
  
  /// Execute action immediately, then throttle subsequent calls
  void run(void Function() action) {
    if (!_isThrottling) {
      // Execute immediately
      action();
      _isThrottling = true;
      
      // Start throttle period
      _timer = Timer(delay, () {
        _isThrottling = false;
        
        // Execute any pending action
        if (_pendingAction != null) {
          final pending = _pendingAction;
          _pendingAction = null;
          run(pending!);
        }
      });
    } else {
      // Store the action to run after throttle period
      _pendingAction = action;
    }
  }
  
  /// Cancel throttling and pending actions
  void cancel() {
    _timer?.cancel();
    _isThrottling = false;
    _pendingAction = null;
  }
  
  /// Dispose of the timer
  void dispose() {
    _timer?.cancel();
    _timer = null;
    _pendingAction = null;
  }
}

/// Search debouncer specifically for text input
class SearchDebouncer {
  final Duration delay;
  final _controller = StreamController<String>.broadcast();
  late final Stream<String> searchStream;
  
  SearchDebouncer({
    this.delay = const Duration(milliseconds: 500),
  }) {
    searchStream = _controller.stream
        .distinct()
        .debounceTime(delay);
  }
  
  /// Add search query to be debounced
  void search(String query) {
    _controller.add(query);
  }
  
  /// Listen to debounced search queries
  StreamSubscription<String> onSearch(void Function(String query) callback) {
    return searchStream.listen(callback);
  }
  
  /// Dispose of resources
  void dispose() {
    _controller.close();
  }
}

/// Extension for TextField debouncing
extension TextEditingControllerDebounce on TextEditingController {
  /// Create a debounced listener for text changes
  void addDebouncedListener({
    required void Function(String) onChanged,
    Duration delay = const Duration(milliseconds: 500),
  }) {
    final debouncer = Debouncer(delay: delay);
    
    addListener(() {
      debouncer.run(() {
        onChanged(text);
      });
    });
  }
}

/// Mixin for adding debouncing to StatefulWidgets
mixin DebounceMixin<T extends StatefulWidget> on State<T> {
  final Map<String, Debouncer> _debouncers = {};
  final Map<String, StreamDebouncer> _streamDebouncers = {};
  final Map<String, Throttler> _throttlers = {};
  
  /// Create or get a debouncer with a specific key
  Debouncer debouncer(
    String key, {
    Duration delay = const Duration(milliseconds: 500),
  }) {
    return _debouncers.putIfAbsent(
      key,
      () => Debouncer(delay: delay),
    );
  }
  
  /// Debounce a function call
  void debounce(
    String key,
    void Function() action, {
    Duration delay = const Duration(milliseconds: 500),
  }) {
    debouncer(key, delay: delay).run(action);
  }
  
  /// Create or get a stream debouncer
  StreamDebouncer<S> streamDebouncer<S>(
    String key, {
    Duration delay = const Duration(milliseconds: 500),
  }) {
    return _streamDebouncers.putIfAbsent(
      key,
      () => StreamDebouncer<S>(delay: delay),
    ) as StreamDebouncer<S>;
  }
  
  /// Create or get a throttler
  Throttler throttler(
    String key, {
    Duration delay = const Duration(milliseconds: 1000),
  }) {
    return _throttlers.putIfAbsent(
      key,
      () => Throttler(delay: delay),
    );
  }
  
  /// Throttle a function call
  void throttle(
    String key,
    void Function() action, {
    Duration delay = const Duration(milliseconds: 1000),
  }) {
    throttler(key, delay: delay).run(action);
  }
  
  @override
  void dispose() {
    // Dispose all debouncers
    for (final debouncer in _debouncers.values) {
      debouncer.dispose();
    }
    _debouncers.clear();
    
    // Dispose all stream debouncers
    for (final debouncer in _streamDebouncers.values) {
      debouncer.dispose();
    }
    _streamDebouncers.clear();
    
    // Dispose all throttlers
    for (final throttler in _throttlers.values) {
      throttler.dispose();
    }
    _throttlers.clear();
    
    super.dispose();
  }
}

/// Example usage in a widget
class ExampleUsage extends StatefulWidget {
  const ExampleUsage({super.key});
  
  @override
  State<ExampleUsage> createState() => _ExampleUsageState();
}

class _ExampleUsageState extends State<ExampleUsage> with DebounceMixin {
  final TextEditingController _searchController = TextEditingController();
  
  @override
  void initState() {
    super.initState();
    
    // Setup debounced search
    _searchController.addDebouncedListener(
      onChanged: _performSearch,
      delay: const Duration(milliseconds: 300),
    );
  }
  
  void _performSearch(String query) {
    // This will only be called after user stops typing for 300ms
    print('Searching for: $query');
  }
  
  void _onButtonTap() {
    // Throttle button taps to prevent rapid clicks
    throttle('button_tap', () {
      print('Button tapped - throttled to once per second');
    });
  }
  
  void _onInputChange(String value) {
    // Debounce input changes
    debounce('input_change', () {
      print('Input changed to: $value');
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TextField(
          controller: _searchController,
          decoration: const InputDecoration(
            hintText: 'Search (debounced)',
          ),
        ),
        ElevatedButton(
          onPressed: _onButtonTap,
          child: const Text('Throttled Button'),
        ),
      ],
    );
  }
  
  @override
  void dispose() {
    _searchController.dispose();
    super.dispose(); // DebounceMixin will clean up debouncers
  }
}
