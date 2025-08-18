# Free & Open Source Crash Reporting Setup for Flutter

## 🎯 Recommended Solutions (All Free)

### Option 1: **GlitchTip** (Easiest) ✅
**Why:** 100% Sentry-compatible API, easy self-host with Docker

```yaml
# docker-compose.yml for GlitchTip
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: glitchtip
      POSTGRES_USER: glitchtip
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  glitchtip:
    image: glitchtip/glitchtip:latest
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgres://glitchtip:your_secure_password@postgres:5432/glitchtip
      SECRET_KEY: your_secret_key_here
      PORT: 8000
      EMAIL_URL: smtp://email@example.com
      GLITCHTIP_DOMAIN: https://your-domain.com
      DEFAULT_FROM_EMAIL: noreply@your-domain.com
      CELERY_WORKER_AUTOSCALE: "1,3"

  worker:
    image: glitchtip/glitchtip:latest
    command: celery -A glitchtip worker -B -l info
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgres://glitchtip:your_secure_password@postgres:5432/glitchtip
      SECRET_KEY: your_secret_key_here

volumes:
  postgres-data:
```

**Flutter Integration (Works with Sentry SDK!):**
```dart
// pubspec.yaml
dependencies:
  sentry_flutter: ^7.14.0  # GlitchTip is Sentry-compatible!

// main.dart
import 'package:sentry_flutter/sentry_flutter.dart';

void main() async {
  await SentryFlutter.init(
    (options) {
      // Point to YOUR GlitchTip instance
      options.dsn = 'https://YOUR_KEY@your-glitchtip.com/PROJECT_ID';
      options.tracesSampleRate = 1.0;
      options.environment = 'production';
      
      // Optional: Custom error filtering
      options.beforeSend = (event, hint) {
        // Don't send errors in debug mode
        if (kDebugMode) return null;
        return event;
      };
    },
    appRunner: () => runApp(const MyApp()),
  );
}
```

### Option 2: **Self-Hosted Sentry** (Full Features)
**Why:** All enterprise features, but complex setup

```bash
# Clone Sentry self-hosted
git clone https://github.com/getsentry/self-hosted.git
cd self-hosted

# Install (requires Docker)
./install.sh

# Start Sentry
docker compose up -d

# Access at http://localhost:9000
```

**Requirements:**
- 4GB+ RAM minimum
- 20GB+ disk space
- Docker & Docker Compose
- PostgreSQL, Redis, Kafka

### Option 3: **SigNoz** (Full Observability)
**Why:** Crash reporting + APM + logs + metrics in one

```yaml
# Install SigNoz with Docker
git clone -b main https://github.com/SigNoz/signoz.git
cd signoz/deploy
./install.sh
```

**Flutter Integration:**
```dart
// For SigNoz, use OpenTelemetry
dependencies:
  opentelemetry: ^0.18.0
  
// Configure OpenTelemetry to send to SigNoz
final tracer = GlobalTracer.instance;
tracer.init(
  serviceName: 'flutter-app',
  endpoint: 'http://your-signoz:4317',
);
```

## 🔨 Implementation Guide

### Step 1: Choose Your Solution

| Solution | Pros | Cons | Best For |
|----------|------|------|----------|
| **GlitchTip** | • Sentry-compatible<br>• Easy setup<br>• Low resource | • Fewer features<br>• Smaller community | Small teams, quick setup |
| **Self-Hosted Sentry** | • Full features<br>• Large community<br>• Best docs | • Complex setup<br>• High resources<br>• Maintenance | Large teams, enterprise |
| **SigNoz** | • Full observability<br>• Modern UI<br>• OpenTelemetry | • Different API<br>• Learning curve | Full stack monitoring |

### Step 2: Basic Error Handler (Works with All)

```dart
// lib/core/error/error_handler.dart
import 'package:flutter/foundation.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

class ErrorHandler {
  static void init() {
    // Catch Flutter errors
    FlutterError.onError = (details) {
      if (kDebugMode) {
        FlutterError.dumpErrorToConsole(details);
      } else {
        Sentry.captureException(
          details.exception,
          stackTrace: details.stack,
        );
      }
    };
    
    // Catch async errors
    PlatformDispatcher.instance.onError = (error, stack) {
      if (kDebugMode) {
        debugPrint('Async error: $error');
      } else {
        Sentry.captureException(error, stackTrace: stack);
      }
      return true;
    };
  }
  
  // Manual error reporting with context
  static void reportError(
    dynamic error,
    StackTrace? stackTrace, {
    Map<String, dynamic>? extra,
    String? userMessage,
  }) {
    Sentry.captureException(
      error,
      stackTrace: stackTrace,
      withScope: (scope) {
        if (extra != null) {
          extra.forEach((key, value) {
            scope.setExtra(key, value);
          });
        }
        if (userMessage != null) {
          scope.setTag('user_message', userMessage);
        }
      },
    );
  }
  
  // Log breadcrumbs for context
  static void addBreadcrumb(String message, {String? category}) {
    Sentry.addBreadcrumb(
      Breadcrumb(
        message: message,
        category: category,
        timestamp: DateTime.now(),
      ),
    );
  }
}
```

### Step 3: Enhanced Error Tracking

```dart
// lib/core/error/error_boundary.dart
class ErrorBoundary extends StatefulWidget {
  final Widget child;
  
  const ErrorBoundary({required this.child, super.key});
  
  @override
  State<ErrorBoundary> createState() => _ErrorBoundaryState();
}

class _ErrorBoundaryState extends State<ErrorBoundary> {
  bool hasError = false;
  dynamic error;
  StackTrace? stackTrace;
  
  @override
  void initState() {
    super.initState();
    // Reset error state when widget rebuilds
    hasError = false;
  }
  
  @override
  Widget build(BuildContext context) {
    if (hasError) {
      return _buildErrorWidget();
    }
    
    return ErrorWidgetBuilder(
      onError: (error, stack) {
        setState(() {
          hasError = true;
          this.error = error;
          stackTrace = stack;
        });
        
        // Report to crash service
        ErrorHandler.reportError(
          error,
          stack,
          extra: {
            'widget': widget.child.runtimeType.toString(),
            'timestamp': DateTime.now().toIso8601String(),
          },
        );
      },
      child: widget.child,
    );
  }
  
  Widget _buildErrorWidget() {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            const Text('Something went wrong'),
            if (kDebugMode) ...[
              const SizedBox(height: 8),
              Text(error.toString(), style: const TextStyle(fontSize: 12)),
            ],
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  hasError = false;
                  error = null;
                  stackTrace = null;
                });
              },
              child: const Text('Try Again'),
            ),
          ],
        ),
      ),
    );
  }
}
```

## 🚀 Quick Start (GlitchTip)

### 1. Deploy GlitchTip (10 minutes)
```bash
# Create directory
mkdir glitchtip && cd glitchtip

# Download docker-compose
curl -O https://raw.githubusercontent.com/glitchtip/glitchtip/master/docker-compose.yml

# Start services
docker-compose up -d

# Create superuser
docker-compose run --rm glitchtip ./manage.py createsuperuser
```

### 2. Configure Flutter (5 minutes)
```dart
// main.dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize error handling
  await SentryFlutter.init(
    (options) {
      options.dsn = 'http://YOUR_KEY@localhost:8000/1';
      options.environment = kDebugMode ? 'debug' : 'production';
      options.tracesSampleRate = kDebugMode ? 1.0 : 0.1;
    },
    appRunner: () => runApp(
      ErrorBoundary(
        child: const MyApp(),
      ),
    ),
  );
  
  // Initialize custom error handler
  ErrorHandler.init();
}
```

### 3. Test Error Reporting
```dart
// Add test button to trigger error
ElevatedButton(
  onPressed: () {
    ErrorHandler.addBreadcrumb('User clicked test error button');
    throw Exception('Test error for crash reporting');
  },
  child: const Text('Test Crash Reporting'),
)
```

## 📊 Comparison Table

| Feature | GlitchTip | Self-Hosted Sentry | SigNoz | Commercial Sentry |
|---------|-----------|-------------------|---------|-------------------|
| **Cost** | Free | Free | Free | $26+/month |
| **Setup Time** | 10 min | 2+ hours | 30 min | 5 min |
| **Resources** | 1GB RAM | 4GB+ RAM | 2GB RAM | Cloud |
| **Error Tracking** | ✅ | ✅ | ✅ | ✅ |
| **Performance** | Basic | ✅ | ✅ | ✅ |
| **Source Maps** | ✅ | ✅ | ❌ | ✅ |
| **User Feedback** | ✅ | ✅ | ❌ | ✅ |
| **Releases** | ✅ | ✅ | ✅ | ✅ |
| **Metrics** | ❌ | Limited | ✅ | ✅ |
| **Logs** | ❌ | ❌ | ✅ | Limited |
| **Maintenance** | Low | High | Medium | None |

## 🎯 Recommendation

**For Your Use Case: Start with GlitchTip**
- ✅ 100% free forever
- ✅ Sentry SDK compatible (no code changes)
- ✅ Docker setup in 10 minutes
- ✅ Low resource usage (runs on $5 VPS)
- ✅ All essential error tracking features

**When to Upgrade:**
- **To Self-Hosted Sentry:** When you need advanced features like performance monitoring
- **To SigNoz:** When you want full observability (APM + logs + metrics)
- **To Commercial Sentry:** Never needed for most startups

## 🔐 Security Notes

1. **Always use environment variables for DSN**
```dart
// .env
GLITCHTIP_DSN=https://key@your-instance.com/1

// main.dart
options.dsn = const String.fromEnvironment('GLITCHTIP_DSN');
```

2. **Filter sensitive data**
```dart
options.beforeSend = (event, hint) {
  // Remove sensitive data
  event.extra?.remove('password');
  event.extra?.remove('token');
  event.extra?.remove('creditCard');
  return event;
};
```

3. **Use VPN/Private network for self-hosted instances**
