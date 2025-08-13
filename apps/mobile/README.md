# Living Twin Mobile App

A Flutter mobile application for conversational AI interactions with your organizational knowledge base.

## Features

- **Voice-First Interface**: Natural speech recognition and synthesis
- **Conversational Memory**: Persistent chat history with context awareness
- **Offline Support**: Local storage with sync capabilities
- **Firebase Authentication**: Secure user authentication
- **Multi-Environment Support**: Development, staging, and production configurations

## Configuration

### API URL Configuration

The app automatically selects the appropriate API URL based on the build mode:

- **Development (Debug)**: `http://localhost:8000` (default)
- **Production (Release)**: `https://api.livingtwin.com`

#### Override API URL

You can override the API URL using environment variables:

```bash
# For development with custom API URL
flutter run --dart-define=API_URL=http://192.168.1.100:8000

# For staging environment
flutter run --dart-define=API_URL=https://api-staging.livingtwin.com

# For production build
flutter build apk --dart-define=API_URL=https://api.livingtwin.com
```

#### Firebase Configuration

Set your Firebase project ID:

```bash
flutter run --dart-define=FIREBASE_PROJECT_ID=your-project-id
```

### Environment Setup

1. **Install Flutter**: Follow the [Flutter installation guide](https://flutter.dev/docs/get-started/install)

2. **Install Dependencies**:
   ```bash
   flutter pub get
   ```

3. **Configure Firebase**:
   - Add your `google-services.json` (Android) and `GoogleService-Info.plist` (iOS)
   - Update Firebase configuration in the app

4. **Run the App**:
   ```bash
   # Development mode (localhost API)
   flutter run
   
   # With custom API URL
   flutter run --dart-define=API_URL=http://your-api-server:8000
   ```

## Architecture

### Services

- **ApiClientEnhanced**: HTTP client with authentication and error handling
- **SpeechService**: Voice recognition and synthesis
- **LocalStorageService**: SQLite-based local storage
- **AuthService**: Firebase authentication wrapper

### Features

- **Chat**: Conversational interface with voice support
- **Pulse**: Dashboard and analytics
- **Ingest**: Document upload and processing
- **Auth**: User authentication and onboarding

### Configuration

The `AppConfig` class manages environment-specific settings:

```dart
// Access current API URL
String apiUrl = AppConfig.apiUrl;

// Check environment
String env = AppConfig.environment;

// Feature flags
bool speechEnabled = AppConfig.enableSpeechRecognition;
```

## Development

### Local Development

1. Start your API server locally:
   ```bash
   cd ../api
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Run the Flutter app:
   ```bash
   flutter run
   ```

The app will automatically connect to `http://localhost:8000` in debug mode.

### Testing with Remote API

To test with a remote API server:

```bash
flutter run --dart-define=API_URL=https://your-remote-api.com
```

### Building for Production

```bash
# Android
flutter build apk --dart-define=API_URL=https://api.livingtwin.com

# iOS
flutter build ios --dart-define=API_URL=https://api.livingtwin.com
```

## Troubleshooting

### Common Issues

1. **API Connection Failed**:
   - Check if the API server is running
   - Verify the API URL configuration
   - Check network connectivity

2. **Speech Recognition Not Working**:
   - Ensure microphone permissions are granted
   - Check device compatibility
   - Verify speech service initialization

3. **Firebase Authentication Issues**:
   - Verify Firebase configuration files
   - Check project ID and API keys
   - Ensure proper SHA-1 fingerprints (Android)

### Debug Information

The app logs configuration information at startup:

```
I/flutter: Environment: development
I/flutter: API URL: http://localhost:8000
I/flutter: Firebase Project: living-twin-demo
```

## Contributing

1. Follow Flutter best practices
2. Use the established architecture patterns
3. Add proper error handling and logging
4. Test on both iOS and Android
5. Update documentation for new features

## License

[Your License Here]
