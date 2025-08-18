import 'package:flutter/material.dart';

import '../../main.dart';
import '../../services/auth.dart';

class OrganizationSetupScreen extends StatefulWidget {
  const OrganizationSetupScreen({super.key});

  @override
  State<OrganizationSetupScreen> createState() => _OrganizationSetupScreenState();
}

class _OrganizationSetupScreenState extends State<OrganizationSetupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _organizationNameController = TextEditingController();
  final _departmentController = TextEditingController();
  final _roleController = TextEditingController();
  final AuthService _authService = AuthService();
  
  bool _isLoading = false;
  String _selectedIndustry = 'Technology';
  String _selectedSize = '1-10 employees';

  final List<String> _industries = [
    'Technology',
    'Healthcare',
    'Finance',
    'Education',
    'Manufacturing',
    'Retail',
    'Consulting',
    'Other',
  ];

  final List<String> _companySizes = [
    '1-10 employees',
    '11-50 employees',
    '51-200 employees',
    '201-1000 employees',
    '1000+ employees',
  ];

  @override
  void dispose() {
    _organizationNameController.dispose();
    _departmentController.dispose();
    _roleController.dispose();
    super.dispose();
  }

  Future<void> _createOrganization() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final result = await _authService.createOrganization(
        name: _organizationNameController.text.trim(),
        industry: _selectedIndustry,
        size: _selectedSize,
        department: _departmentController.text.trim(),
        role: _roleController.text.trim(),
      );

      if (result['success']) {
        if (mounted) {
          // Show success message
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Organization created successfully!'),
              backgroundColor: Colors.green,
            ),
          );
          
          // Navigate to main app
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (context) => const MainScreen()),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['error'] ?? 'Failed to create organization'),
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

  Future<void> _skipSetup() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // Create a default organization for the user
      await _authService.createOrganization(
        name: 'Personal Workspace',
        industry: 'Other',
        size: '1-10 employees',
        department: 'General',
        role: 'User',
      );

      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => const MainScreen()),
        );
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
        title: const Text('Setup Organization'),
        backgroundColor: Colors.blue[600],
        foregroundColor: Colors.white,
        automaticallyImplyLeading: false,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header
              Column(
                children: [
                  Icon(
                    Icons.business,
                    size: 80,
                    color: Colors.blue[600],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Setup Your Organization',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Help us customize your Living Twin experience',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.grey[600],
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
              
              const SizedBox(height: 32),
              
              // Organization Name
              TextFormField(
                controller: _organizationNameController,
                decoration: const InputDecoration(
                  labelText: 'Organization Name',
                  hintText: 'e.g., Acme Corporation',
                  prefixIcon: Icon(Icons.business),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Please enter your organization name';
                  }
                  return null;
                },
              ),
              
              const SizedBox(height: 16),
              
              // Industry Dropdown
              DropdownButtonFormField<String>(
                value: _selectedIndustry,
                decoration: const InputDecoration(
                  labelText: 'Industry',
                  prefixIcon: Icon(Icons.category),
                ),
                items: _industries.map((industry) {
                  return DropdownMenuItem(
                    value: industry,
                    child: Text(industry),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedIndustry = value!;
                  });
                },
              ),
              
              const SizedBox(height: 16),
              
              // Company Size Dropdown
              DropdownButtonFormField<String>(
                value: _selectedSize,
                decoration: const InputDecoration(
                  labelText: 'Company Size',
                  prefixIcon: Icon(Icons.people),
                ),
                items: _companySizes.map((size) {
                  return DropdownMenuItem(
                    value: size,
                    child: Text(size),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedSize = value!;
                  });
                },
              ),
              
              const SizedBox(height: 16),
              
              // Department
              TextFormField(
                controller: _departmentController,
                decoration: const InputDecoration(
                  labelText: 'Department (Optional)',
                  hintText: 'e.g., Engineering, Marketing',
                  prefixIcon: Icon(Icons.group),
                ),
              ),
              
              const SizedBox(height: 16),
              
              // Role
              TextFormField(
                controller: _roleController,
                decoration: const InputDecoration(
                  labelText: 'Your Role (Optional)',
                  hintText: 'e.g., Software Engineer, Manager',
                  prefixIcon: Icon(Icons.person),
                ),
              ),
              
              const SizedBox(height: 32),
              
              // Create Organization Button
              ElevatedButton(
                onPressed: _isLoading ? null : _createOrganization,
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
                    : const Text('Create Organization'),
              ),
              
              const SizedBox(height: 16),
              
              // Skip Button
              TextButton(
                onPressed: _isLoading ? null : _skipSetup,
                child: const Text('Skip for now'),
              ),
              
              const SizedBox(height: 24),
              
              // Info Card
              Card(
                color: Colors.blue[50],
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.info, color: Colors.blue[600]),
                          const SizedBox(width: 8),
                          Text(
                            'Why do we need this?',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.blue[600],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'This information helps us:\n'
                        '• Customize your Living Twin experience\n'
                        '• Provide relevant industry insights\n'
                        '• Enable team collaboration features\n'
                        '• Generate invitation codes for your team',
                        style: TextStyle(
                          color: Colors.blue[700],
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
