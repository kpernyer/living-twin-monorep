import 'package:flutter/material.dart';

import 'config/app_config.dart';
import 'features/auth/login_screen.dart';
import 'features/chat/chat_screen.dart';
import 'features/home/home_screen.dart';
import 'services/api_client_enhanced.dart';
import 'services/auth.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize auth service
  await AuthService().initialize();
  
  runApp(const LivingTwinApp());
}

class LivingTwinApp extends StatelessWidget {
  const LivingTwinApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Living Twin',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 2,
        ),
        cardTheme: const CardThemeData(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(12)),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 12,
          ),
        ),
      ),
      home: const AuthWrapper(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    final authService = AuthService();
    
    // Check if user is authenticated
    if (authService.isAuthenticated) {
      return const MainScreen();
    } else {
      return const LoginScreen();
    }
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;
  final ApiClientEnhanced _apiClient = ApiClientEnhanced(
    baseUrl: AppConfig.apiUrl,
    authService: AuthService(),
  );
  
  final List<Widget> _screens = [
    const HomeScreen(),
    const ChatScreen(),
  ];

  final List<BottomNavigationBarItem> _navItems = [
    const BottomNavigationBarItem(
      icon: Icon(Icons.home),
      label: 'Home',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.chat),
      label: 'Chat',
    ),
  ];

  @override
  void initState() {
    super.initState();
    _initializeApp();
  }

  Future<void> _initializeApp() async {
    // TODO: Implement retry queue processing if needed
  }

  Future<void> _handleLogout() async {
    final authService = AuthService();
    await authService.signOut();
    
    if (mounted) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (context) => const LoginScreen()),
      );
    }
  }

  void _showUserMenu() {
    final authService = AuthService();
    final user = authService.currentUser;
    final organization = authService.getOrganization();
    
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // User Info
            Row(
              children: [
                CircleAvatar(
                  radius: 30,
                  backgroundColor: Colors.blue[600],
                  child: Text(
                    (user?['displayName'] ?? 'U')[0].toUpperCase(),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        user?['displayName'] ?? 'User',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      Text(
                        user?['email'] ?? '',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.grey[600],
                        ),
                      ),
                      if (organization != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          organization['name'] ?? '',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.blue[600],
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 24),
            const Divider(),
            
            // Menu Items
            ListTile(
              leading: const Icon(Icons.person),
              title: const Text('Profile'),
              onTap: () {
                Navigator.pop(context);
                // TODO: Navigate to profile screen
              },
            ),
            
            if (authService.isOrganizationAdmin()) ...[
              ListTile(
                leading: const Icon(Icons.business),
                title: const Text('Organization Settings'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: Navigate to organization settings
                },
              ),
              
              ListTile(
                leading: const Icon(Icons.group_add),
                title: const Text('Invite Members'),
                onTap: () async {
                  Navigator.pop(context);
                  final inviteCode = await authService.generateInvitationCode();
                  if (inviteCode != null && mounted) {
                    showDialog(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: const Text('Invitation Code'),
                        content: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Text('Share this code with team members:'),
                            const SizedBox(height: 16),
                            Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: Colors.grey[100],
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                inviteCode,
                                style: const TextStyle(
                                  fontFamily: 'monospace',
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(context),
                            child: const Text('Close'),
                          ),
                        ],
                      ),
                    );
                  }
                },
              ),
            ],
            
            ListTile(
              leading: const Icon(Icons.settings),
              title: const Text('Settings'),
              onTap: () {
                Navigator.pop(context);
                // TODO: Navigate to settings screen
              },
            ),
            
            ListTile(
              leading: const Icon(Icons.help),
              title: const Text('Help & Support'),
              onTap: () {
                Navigator.pop(context);
                // TODO: Navigate to help screen
              },
            ),
            
            const Divider(),
            
            ListTile(
              leading: const Icon(Icons.logout, color: Colors.red),
              title: const Text('Sign Out', style: TextStyle(color: Colors.red)),
              onTap: () {
                Navigator.pop(context);
                _handleLogout();
              },
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final authService = AuthService();
    final user = authService.currentUser;
    
    return Scaffold(
      appBar: AppBar(
        title: Text(_getScreenTitle()),
        backgroundColor: Colors.blue[600],
        foregroundColor: Colors.white,
        actions: [
          GestureDetector(
            onTap: _showUserMenu,
            child: Padding(
              padding: const EdgeInsets.only(right: 16),
              child: CircleAvatar(
                radius: 18,
                backgroundColor: Colors.white,
                child: Text(
                  (user?['displayName'] ?? 'U')[0].toUpperCase(),
                  style: TextStyle(
                    color: Colors.blue[600],
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: _navItems,
        type: BottomNavigationBarType.fixed,
        selectedItemColor: Colors.blue[600],
        unselectedItemColor: Colors.grey[600],
        backgroundColor: Colors.white,
        elevation: 8,
      ),
    );
  }

  String _getScreenTitle() {
    switch (_currentIndex) {
      case 0:
        return 'Home';
      case 1:
        return 'Chat';
      default:
        return 'Living Twin';
    }
  }
}
