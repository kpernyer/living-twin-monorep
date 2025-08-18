import 'package:flutter/material.dart';

import '../../main.dart';
import '../../services/auth.dart';
import '../onboarding/organization_setup_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final AuthService _authService = AuthService();
  
  bool _isLoading = false;
  bool _obscurePassword = true;
  bool _isSignUp = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleEmailAuth() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
    });

    try {
      Map<String, dynamic> result;
      
      if (_isSignUp) {
        result = await _authService.createUserWithEmailAndPassword(
          email: _emailController.text.trim(),
          password: _passwordController.text,
        );
      } else {
        result = await _authService.signInWithEmailAndPassword(
          email: _emailController.text.trim(),
          password: _passwordController.text,
        );
      }

      if (result['success']) {
        if (mounted) {
          // Check if user has organization setup
          final user = result['user'] as Map<String, dynamic>;
          final hasOrganization = user['organizationId'] != null;
          
          if (hasOrganization) {
            // Go directly to main app
            Navigator.of(context).pushReplacement(
              MaterialPageRoute(builder: (context) => const MainScreen()),
            );
          } else {
            // Go to organization setup
            Navigator.of(context).pushReplacement(
              MaterialPageRoute(builder: (context) => const OrganizationSetupScreen()),
            );
          }
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['error'] ?? 'Authentication failed'),
              backgroundColor: Colors.red,
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
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _handleGoogleSignIn() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // Mock Google Sign-In for demo
      final result = await _authService.signInWithGoogle();
      
      if (result['success']) {
        if (mounted) {
          final user = result['user'] as Map<String, dynamic>;
          final hasOrganization = user['organizationId'] != null;
          
          if (hasOrganization) {
            Navigator.of(context).pushReplacement(
              MaterialPageRoute(builder: (context) => const MainScreen()),
            );
          } else {
            Navigator.of(context).pushReplacement(
              MaterialPageRoute(builder: (context) => const OrganizationSetupScreen()),
            );
          }
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['error'] ?? 'Google Sign-In failed'),
              backgroundColor: Colors.red,
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
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _handleAnonymousSignIn() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final result = await _authService.signInAnonymously();
      
      if (result['success']) {
        if (mounted) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (context) => const MainScreen()),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['error'] ?? 'Anonymous sign-in failed'),
              backgroundColor: Colors.red,
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
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 40),
              
              // Logo and title
              Column(
                children: [
                  Container(
                    width: 80,
                    height: 80,
                    decoration: BoxDecoration(
                      color: Colors.blue[600],
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Icon(
                      Icons.psychology,
                      color: Colors.white,
                      size: 40,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Living Twin',
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Colors.blue[600],
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _isSignUp ? 'Create your account' : 'Welcome back',
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 40),
              
              // Email/Password Form
              Form(
                key: _formKey,
                child: Column(
                  children: [
                    TextFormField(
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      decoration: const InputDecoration(
                        labelText: 'Email',
                        prefixIcon: Icon(Icons.email),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your email';
                        }
                        if (!value.contains('@')) {
                          return 'Please enter a valid email';
                        }
                        return null;
                      },
                    ),
                    
                    const SizedBox(height: 16),
                    
                    TextFormField(
                      controller: _passwordController,
                      obscureText: _obscurePassword,
                      decoration: InputDecoration(
                        labelText: 'Password',
                        prefixIcon: const Icon(Icons.lock),
                        suffixIcon: IconButton(
                          icon: Icon(_obscurePassword ? Icons.visibility : Icons.visibility_off),
                          onPressed: () {
                            setState(() {
                              _obscurePassword = !_obscurePassword;
                            });
                          },
                        ),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your password';
                        }
                        if (_isSignUp && value.length < 6) {
                          return 'Password must be at least 6 characters';
                        }
                        return null;
                      },
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // Sign In/Up Button
                    ElevatedButton(
                      onPressed: _isLoading ? null : _handleEmailAuth,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue[600],
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: _isLoading
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            )
                          : Text(_isSignUp ? 'Create Account' : 'Sign In'),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 24),
              
              // Divider
              Row(
                children: [
                  const Expanded(child: Divider()),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: Text(
                      'or',
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                  ),
                  const Expanded(child: Divider()),
                ],
              ),
              
              const SizedBox(height: 24),
              
              // Google Sign In
              OutlinedButton.icon(
                onPressed: _isLoading ? null : _handleGoogleSignIn,
                icon: Container(
                  width: 20,
                  height: 20,
                  decoration: const BoxDecoration(
                    image: DecorationImage(
                      image: NetworkImage('https://developers.google.com/identity/images/g-logo.png'),
                      fit: BoxFit.contain,
                    ),
                  ),
                ),
                label: const Text('Continue with Google'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
              
              const SizedBox(height: 16),
              
              // Anonymous Sign In
              TextButton(
                onPressed: _isLoading ? null : _handleAnonymousSignIn,
                child: const Text('Continue as Guest'),
              ),
              
              const SizedBox(height: 32),
              
              // Toggle Sign In/Up
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    _isSignUp ? 'Already have an account? ' : "Don't have an account? ",
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                  TextButton(
                    onPressed: () {
                      setState(() {
                        _isSignUp = !_isSignUp;
                      });
                    },
                    child: Text(_isSignUp ? 'Sign In' : 'Sign Up'),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              // Invitation Link
              TextButton.icon(
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (context) => const InvitationScreen(),
                    ),
                  );
                },
                icon: const Icon(Icons.mail),
                label: const Text('Have an invitation code?'),
                style: TextButton.styleFrom(
                  foregroundColor: Colors.blue[600],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class InvitationScreen extends StatefulWidget {
  const InvitationScreen({super.key});

  @override
  State<InvitationScreen> createState() => _InvitationScreenState();
}

class _InvitationScreenState extends State<InvitationScreen> {
  final _invitationController = TextEditingController();
  final AuthService _authService = AuthService();
  bool _isLoading = false;

  @override
  void dispose() {
    _invitationController.dispose();
    super.dispose();
  }

  Future<void> _handleInvitation() async {
    final invitationCode = _invitationController.text.trim();
    if (invitationCode.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter an invitation code'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final result = await _authService.acceptInvitation(invitationCode);
      
      if (result['success']) {
        if (mounted) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (context) => const MainScreen()),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['error'] ?? 'Invalid invitation code'),
              backgroundColor: Colors.red,
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
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Join Organization'),
        backgroundColor: Colors.blue[600],
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 40),
            
            Icon(
              Icons.mail_outline,
              size: 80,
              color: Colors.blue[600],
            ),
            
            const SizedBox(height: 24),
            
            Text(
              'Enter Invitation Code',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            
            const SizedBox(height: 8),
            
            Text(
              'Enter the invitation code you received from your organization admin via email or SMS',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
            
            const SizedBox(height: 32),
            
            TextField(
              controller: _invitationController,
              decoration: const InputDecoration(
                labelText: 'AprioOne Invitation Code',
                hintText: 'e.g., APRIO-ACME-INV123456789',
                prefixIcon: Icon(Icons.vpn_key),
                helperText: 'Format: APRIO-[ORG]-[INVITE_ID]',
              ),
              textCapitalization: TextCapitalization.characters,
            ),
            
            const SizedBox(height: 24),
            
            ElevatedButton(
              onPressed: _isLoading ? null : _handleInvitation,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue[600],
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: _isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    )
                  : const Text('Join Organization'),
            ),
            
            const Spacer(),
            
            Text(
              'Don\'t have an invitation code? Contact your organization admin.',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
