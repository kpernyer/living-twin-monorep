"""Local mock repository for development and testing."""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from ..domain.models import Tenant


class LocalMockRepository:
    """Local file-based mock repository for development."""

    def __init__(self, data_dir: str = "./local_data"):
        self.data_dir = data_dir
        self.tenants_file = os.path.join(data_dir, "tenants.json")
        self.users_file = os.path.join(data_dir, "users.json")
        self.invitations_file = os.path.join(data_dir, "invitations.json")
        self.organizations_file = os.path.join(data_dir, "organizations.json")

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Initialize with demo data if files don't exist
        self._init_demo_data()

    def _init_demo_data(self):
        """Initialize with demo organizations and users."""

        # Demo organizations
        if not os.path.exists(self.organizations_file):
            demo_orgs = {
                "aprio_org_acme": {
                    "id": "aprio_org_acme",
                    "name": "Acme Corporation",
                    "webUrl": "https://acme.com",
                    "industry": "Technology",
                    "size": "201-1000 employees",
                    "techContact": "tech@acme.com",
                    "businessContact": "hr@acme.com",
                    "adminPortalUrl": "https://admin.acme.aprioone.com",
                    "status": "active",
                    "features": ["chat", "pulse", "ingest", "analytics"],
                    "branding": {
                        "primaryColor": "#1976D2",
                        "logo": "https://acme.com/logo.png",
                        "theme": "corporate",
                    },
                    "emailDomains": ["acme.com"],
                    "autoBindNewUsers": True,
                    "createdAt": "2024-01-01T00:00:00Z",
                },
                "aprio_org_techcorp": {
                    "id": "aprio_org_techcorp",
                    "name": "TechCorp Industries",
                    "webUrl": "https://techcorp.io",
                    "industry": "Manufacturing",
                    "size": "1001-5000 employees",
                    "techContact": "it@techcorp.io",
                    "businessContact": "admin@techcorp.io",
                    "adminPortalUrl": "https://admin.techcorp.aprioone.com",
                    "status": "active",
                    "features": ["chat", "pulse", "ingest"],
                    "branding": {
                        "primaryColor": "#FF5722",
                        "logo": "https://techcorp.io/logo.png",
                        "theme": "industrial",
                    },
                    "emailDomains": ["techcorp.io"],
                    "autoBindNewUsers": True,
                    "createdAt": "2024-01-15T00:00:00Z",
                },
                "demo": {
                    "id": "demo",
                    "name": "Demo Organization",
                    "webUrl": "https://demo.aprioone.com",
                    "industry": "Demo",
                    "size": "1-50 employees",
                    "techContact": "demo@aprioone.com",
                    "businessContact": "demo@aprioone.com",
                    "adminPortalUrl": "https://demo.aprioone.com",
                    "status": "active",
                    "features": ["chat", "pulse", "ingest", "analytics", "debug"],
                    "branding": {
                        "primaryColor": "#9C27B0",
                        "logo": "https://demo.aprioone.com/logo.png",
                        "theme": "demo",
                    },
                    "emailDomains": [],
                    "autoBindNewUsers": False,
                    "createdAt": "2024-01-01T00:00:00Z",
                },
                "aprio_org_bigcorp": {
                    "id": "aprio_org_bigcorp",
                    "name": "BIG Corp Solutions",
                    "webUrl": "https://bigcorp.com",
                    "industry": "Enterprise Software & Technology Solutions",
                    "size": "1001-5000 employees",
                    "techContact": "it@bigcorp.com",
                    "businessContact": "hr@bigcorp.com",
                    "adminPortalUrl": "https://admin.bigcorp.aprioone.com",
                    "status": "active",
                    "features": [
                        "chat",
                        "pulse",
                        "ingest",
                        "analytics",
                        "reporting",
                        "integrations",
                    ],
                    "branding": {
                        "primaryColor": "#2E7D32",
                        "secondaryColor": "#66BB6A",
                        "logo": "https://bigcorp.com/assets/logo.png",
                        "theme": "enterprise",
                    },
                    "emailDomains": ["bigcorp.com"],
                    "autoBindNewUsers": True,
                    "headquarters": {
                        "address": "1500 Technology Drive, Suite 400",
                        "city": "San Jose",
                        "state": "CA",
                        "zipCode": "95110",
                        "country": "USA",
                    },
                    "offices": [
                        {
                            "name": "Austin Engineering Center",
                            "address": "2100 Innovation Blvd",
                            "city": "Austin",
                            "state": "TX",
                            "country": "USA",
                        },
                        {
                            "name": "New York Sales Office",
                            "address": "350 Fifth Avenue, Floor 32",
                            "city": "New York",
                            "state": "NY",
                            "country": "USA",
                        },
                        {
                            "name": "Chicago Regional Office",
                            "address": "233 S Wacker Drive, Suite 8400",
                            "city": "Chicago",
                            "state": "IL",
                            "country": "USA",
                        },
                    ],
                    "employeeCount": 1247,
                    "founded": "2018",
                    "createdAt": "2024-02-01T00:00:00Z",
                },
            }
            self._save_json(self.organizations_file, demo_orgs)

        # Demo tenants (maps to organizations)
        if not os.path.exists(self.tenants_file):
            demo_tenants = {
                "aprio_org_acme": {
                    "id": "aprio_org_acme",
                    "name": "Acme Corporation",
                    "domain": "acme.com",
                    "settings": {
                        "features": ["chat", "pulse", "ingest", "analytics"],
                        "branding": {"primaryColor": "#1976D2", "theme": "corporate"},
                    },
                    "created_at": "2024-01-01T00:00:00Z",
                    "is_active": True,
                },
                "aprio_org_techcorp": {
                    "id": "aprio_org_techcorp",
                    "name": "TechCorp Industries",
                    "domain": "techcorp.io",
                    "settings": {
                        "features": ["chat", "pulse", "ingest"],
                        "branding": {"primaryColor": "#FF5722", "theme": "industrial"},
                    },
                    "created_at": "2024-01-15T00:00:00Z",
                    "is_active": True,
                },
                "demo": {
                    "id": "demo",
                    "name": "Demo Organization",
                    "domain": None,
                    "settings": {
                        "features": ["chat", "pulse", "ingest", "analytics", "debug"],
                        "branding": {"primaryColor": "#9C27B0", "theme": "demo"},
                    },
                    "created_at": "2024-01-01T00:00:00Z",
                    "is_active": True,
                },
                "aprio_org_bigcorp": {
                    "id": "aprio_org_bigcorp",
                    "name": "BIG Corp Solutions",
                    "domain": "bigcorp.com",
                    "settings": {
                        "features": [
                            "chat",
                            "pulse",
                            "ingest",
                            "analytics",
                            "reporting",
                            "integrations",
                        ],
                        "branding": {
                            "primaryColor": "#2E7D32",
                            "secondaryColor": "#66BB6A",
                            "theme": "enterprise",
                        },
                    },
                    "created_at": "2024-02-01T00:00:00Z",
                    "is_active": True,
                },
            }
            self._save_json(self.tenants_file, demo_tenants)

        # Demo users
        if not os.path.exists(self.users_file):
            demo_users = {
                "aprio_org_acme": {
                    "john@acme.com": {
                        "id": "user_john_acme",
                        "email": "john@acme.com",
                        "name": "John Doe",
                        "tenant_id": "aprio_org_acme",
                        "roles": ["employee"],
                        "department": "Engineering",
                        "permissions": ["read", "write"],
                        "created_at": "2024-01-01T00:00:00Z",
                    },
                    "admin@acme.com": {
                        "id": "user_admin_acme",
                        "email": "admin@acme.com",
                        "name": "Alice Admin",
                        "tenant_id": "aprio_org_acme",
                        "roles": ["admin", "employee"],
                        "department": "IT",
                        "permissions": ["read", "write", "admin"],
                        "created_at": "2024-01-01T00:00:00Z",
                    },
                },
                "aprio_org_techcorp": {
                    "bob@techcorp.io": {
                        "id": "user_bob_techcorp",
                        "email": "bob@techcorp.io",
                        "name": "Bob Smith",
                        "tenant_id": "aprio_org_techcorp",
                        "roles": ["employee"],
                        "department": "Operations",
                        "permissions": ["read", "write"],
                        "created_at": "2024-01-15T00:00:00Z",
                    }
                },
                "demo": {
                    "demo@example.com": {
                        "id": "user_demo",
                        "email": "demo@example.com",
                        "name": "Demo User",
                        "tenant_id": "demo",
                        "roles": ["admin"],
                        "department": "Demo",
                        "permissions": ["read", "write", "admin", "debug"],
                        "created_at": "2024-01-01T00:00:00Z",
                    }
                },
                "aprio_org_bigcorp": {
                    # Executive Leadership
                    "sarah.chen@bigcorp.com": {
                        "id": "user_sarah_chen_bigcorp",
                        "email": "sarah.chen@bigcorp.com",
                        "name": "Sarah Chen",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["ceo", "executive"],
                        "department": "Executive",
                        "title": "Chief Executive Officer",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write", "admin", "executive"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "marcus.johnson@bigcorp.com": {
                        "id": "user_marcus_johnson_bigcorp",
                        "email": "marcus.johnson@bigcorp.com",
                        "name": "Marcus Johnson",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["vp", "executive"],
                        "department": "Engineering",
                        "title": "VP of Engineering",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write", "admin"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "elena.rodriguez@bigcorp.com": {
                        "id": "user_elena_rodriguez_bigcorp",
                        "email": "elena.rodriguez@bigcorp.com",
                        "name": "Elena Rodriguez",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["vp", "executive"],
                        "department": "Sales",
                        "title": "VP of Sales",
                        "location": "New York, NY",
                        "permissions": ["read", "write", "admin"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "david.kim@bigcorp.com": {
                        "id": "user_david_kim_bigcorp",
                        "email": "david.kim@bigcorp.com",
                        "name": "David Kim",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["vp", "executive"],
                        "department": "Marketing",
                        "title": "VP of Marketing",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write", "admin"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "fatima.al-zahra@bigcorp.com": {
                        "id": "user_fatima_al_zahra_bigcorp",
                        "email": "fatima.al-zahra@bigcorp.com",
                        "name": "Fatima Al-Zahra",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["vp", "executive"],
                        "department": "Human Resources",
                        "title": "VP of Human Resources",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write", "admin"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "james.oconnor@bigcorp.com": {
                        "id": "user_james_oconnor_bigcorp",
                        "email": "james.oconnor@bigcorp.com",
                        "name": "James O'Connor",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["vp", "executive"],
                        "department": "Operations",
                        "title": "VP of Operations",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write", "admin"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    # Engineering - Platform Team (San Jose)
                    "priya.patel@bigcorp.com": {
                        "id": "user_priya_patel_bigcorp",
                        "email": "priya.patel@bigcorp.com",
                        "name": "Priya Patel",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["manager", "employee"],
                        "department": "Engineering",
                        "title": "Engineering Manager - Platform",
                        "team": "Platform Engineering",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "alex.petrov@bigcorp.com": {
                        "id": "user_alex_petrov_bigcorp",
                        "email": "alex.petrov@bigcorp.com",
                        "name": "Alex Petrov",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Engineering",
                        "title": "Senior Software Engineer",
                        "team": "Platform Engineering",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "maria.santos@bigcorp.com": {
                        "id": "user_maria_santos_bigcorp",
                        "email": "maria.santos@bigcorp.com",
                        "name": "Maria Santos",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Engineering",
                        "title": "Software Engineer",
                        "team": "Platform Engineering",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "yuki.tanaka@bigcorp.com": {
                        "id": "user_yuki_tanaka_bigcorp",
                        "email": "yuki.tanaka@bigcorp.com",
                        "name": "Yuki Tanaka",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Engineering",
                        "title": "DevOps Engineer",
                        "team": "Platform Engineering",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    # Engineering - Frontend Team (San Jose)
                    "ahmed.hassan@bigcorp.com": {
                        "id": "user_ahmed_hassan_bigcorp",
                        "email": "ahmed.hassan@bigcorp.com",
                        "name": "Ahmed Hassan",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["manager", "employee"],
                        "department": "Engineering",
                        "title": "Engineering Manager - Frontend",
                        "team": "Frontend Engineering",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "lisa.andersson@bigcorp.com": {
                        "id": "user_lisa_andersson_bigcorp",
                        "email": "lisa.andersson@bigcorp.com",
                        "name": "Lisa Andersson",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Engineering",
                        "title": "Senior Frontend Engineer",
                        "team": "Frontend Engineering",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "carlos.mendoza@bigcorp.com": {
                        "id": "user_carlos_mendoza_bigcorp",
                        "email": "carlos.mendoza@bigcorp.com",
                        "name": "Carlos Mendoza",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Engineering",
                        "title": "Frontend Engineer",
                        "team": "Frontend Engineering",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    # Engineering - Backend Team (San Jose)
                    "raj.sharma@bigcorp.com": {
                        "id": "user_raj_sharma_bigcorp",
                        "email": "raj.sharma@bigcorp.com",
                        "name": "Raj Sharma",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["manager", "employee"],
                        "department": "Engineering",
                        "title": "Engineering Manager - Backend",
                        "team": "Backend Engineering",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "jennifer.wong@bigcorp.com": {
                        "id": "user_jennifer_wong_bigcorp",
                        "email": "jennifer.wong@bigcorp.com",
                        "name": "Jennifer Wong",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Engineering",
                        "title": "Senior Backend Engineer",
                        "team": "Backend Engineering",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "mikhail.volkov@bigcorp.com": {
                        "id": "user_mikhail_volkov_bigcorp",
                        "email": "mikhail.volkov@bigcorp.com",
                        "name": "Mikhail Volkov",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Engineering",
                        "title": "Backend Engineer",
                        "team": "Backend Engineering",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    # Engineering - Austin Team (Remote Location)
                    "robert.taylor@bigcorp.com": {
                        "id": "user_robert_taylor_bigcorp",
                        "email": "robert.taylor@bigcorp.com",
                        "name": "Robert Taylor",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["manager", "employee"],
                        "department": "Engineering",
                        "title": "Site Engineering Manager - Austin",
                        "team": "Austin Engineering",
                        "location": "Austin, TX",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "aisha.okafor@bigcorp.com": {
                        "id": "user_aisha_okafor_bigcorp",
                        "email": "aisha.okafor@bigcorp.com",
                        "name": "Aisha Okafor",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Engineering",
                        "title": "Senior Software Engineer",
                        "team": "Austin Engineering",
                        "location": "Austin, TX",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "thomas.mueller@bigcorp.com": {
                        "id": "user_thomas_mueller_bigcorp",
                        "email": "thomas.mueller@bigcorp.com",
                        "name": "Thomas Mueller",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Engineering",
                        "title": "Software Engineer",
                        "team": "Austin Engineering",
                        "location": "Austin, TX",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "grace.liu@bigcorp.com": {
                        "id": "user_grace_liu_bigcorp",
                        "email": "grace.liu@bigcorp.com",
                        "name": "Grace Liu",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Engineering",
                        "title": "QA Engineer",
                        "team": "Austin Engineering",
                        "location": "Austin, TX",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    # Sales - Pre-Sales Team
                    "michael.brown@bigcorp.com": {
                        "id": "user_michael_brown_bigcorp",
                        "email": "michael.brown@bigcorp.com",
                        "name": "Michael Brown",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["manager", "employee"],
                        "department": "Sales",
                        "title": "Director of Pre-Sales",
                        "team": "Pre-Sales",
                        "location": "New York, NY",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "sofia.rossi@bigcorp.com": {
                        "id": "user_sofia_rossi_bigcorp",
                        "email": "sofia.rossi@bigcorp.com",
                        "name": "Sofia Rossi",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Sales",
                        "title": "Senior Solutions Engineer",
                        "team": "Pre-Sales",
                        "location": "New York, NY",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "daniel.cohen@bigcorp.com": {
                        "id": "user_daniel_cohen_bigcorp",
                        "email": "daniel.cohen@bigcorp.com",
                        "name": "Daniel Cohen",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Sales",
                        "title": "Solutions Engineer",
                        "team": "Pre-Sales",
                        "location": "New York, NY",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    # Sales - Enterprise Sales
                    "patricia.williams@bigcorp.com": {
                        "id": "user_patricia_williams_bigcorp",
                        "email": "patricia.williams@bigcorp.com",
                        "name": "Patricia Williams",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["manager", "employee"],
                        "department": "Sales",
                        "title": "Director of Enterprise Sales",
                        "team": "Enterprise Sales",
                        "location": "New York, NY",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "omar.ibrahim@bigcorp.com": {
                        "id": "user_omar_ibrahim_bigcorp",
                        "email": "omar.ibrahim@bigcorp.com",
                        "name": "Omar Ibrahim",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Sales",
                        "title": "Senior Account Executive",
                        "team": "Enterprise Sales",
                        "location": "New York, NY",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "anna.kowalski@bigcorp.com": {
                        "id": "user_anna_kowalski_bigcorp",
                        "email": "anna.kowalski@bigcorp.com",
                        "name": "Anna Kowalski",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Sales",
                        "title": "Account Executive",
                        "team": "Enterprise Sales",
                        "location": "New York, NY",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    # Sales - Key Account Management
                    "kevin.nakamura@bigcorp.com": {
                        "id": "user_kevin_nakamura_bigcorp",
                        "email": "kevin.nakamura@bigcorp.com",
                        "name": "Kevin Nakamura",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["manager", "employee"],
                        "department": "Sales",
                        "title": "Director of Key Accounts",
                        "team": "Key Account Management",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "rebecca.davis@bigcorp.com": {
                        "id": "user_rebecca_davis_bigcorp",
                        "email": "rebecca.davis@bigcorp.com",
                        "name": "Rebecca Davis",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Sales",
                        "title": "Senior Key Account Manager",
                        "team": "Key Account Management",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    # Sales - Regional Offices
                    "stephanie.martin@bigcorp.com": {
                        "id": "user_stephanie_martin_bigcorp",
                        "email": "stephanie.martin@bigcorp.com",
                        "name": "Stephanie Martin",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["manager", "employee"],
                        "department": "Sales",
                        "title": "Regional Sales Manager - Midwest",
                        "team": "Regional Sales",
                        "location": "Chicago, IL",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "hassan.ali@bigcorp.com": {
                        "id": "user_hassan_ali_bigcorp",
                        "email": "hassan.ali@bigcorp.com",
                        "name": "Hassan Ali",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Sales",
                        "title": "Regional Account Executive",
                        "team": "Regional Sales",
                        "location": "Chicago, IL",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    # Sales - Customer Success (After-Sales)
                    "linda.garcia@bigcorp.com": {
                        "id": "user_linda_garcia_bigcorp",
                        "email": "linda.garcia@bigcorp.com",
                        "name": "Linda Garcia",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["manager", "employee"],
                        "department": "Sales",
                        "title": "Director of Customer Success",
                        "team": "Customer Success",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "benjamin.lee@bigcorp.com": {
                        "id": "user_benjamin_lee_bigcorp",
                        "email": "benjamin.lee@bigcorp.com",
                        "name": "Benjamin Lee",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Sales",
                        "title": "Senior Customer Success Manager",
                        "team": "Customer Success",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "nadia.popov@bigcorp.com": {
                        "id": "user_nadia_popov_bigcorp",
                        "email": "nadia.popov@bigcorp.com",
                        "name": "Nadia Popov",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Sales",
                        "title": "Customer Success Manager",
                        "team": "Customer Success",
                        "location": "New York, NY",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    # Marketing Team
                    "jessica.thompson@bigcorp.com": {
                        "id": "user_jessica_thompson_bigcorp",
                        "email": "jessica.thompson@bigcorp.com",
                        "name": "Jessica Thompson",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["manager", "employee"],
                        "department": "Marketing",
                        "title": "Director of Digital Marketing",
                        "team": "Digital Marketing",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "antonio.silva@bigcorp.com": {
                        "id": "user_antonio_silva_bigcorp",
                        "email": "antonio.silva@bigcorp.com",
                        "name": "Antonio Silva",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Marketing",
                        "title": "Senior Marketing Manager",
                        "team": "Digital Marketing",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "rachel.goldberg@bigcorp.com": {
                        "id": "user_rachel_goldberg_bigcorp",
                        "email": "rachel.goldberg@bigcorp.com",
                        "name": "Rachel Goldberg",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Marketing",
                        "title": "Content Marketing Specialist",
                        "team": "Digital Marketing",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    # Human Resources Team
                    "michelle.jones@bigcorp.com": {
                        "id": "user_michelle_jones_bigcorp",
                        "email": "michelle.jones@bigcorp.com",
                        "name": "Michelle Jones",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["manager", "employee"],
                        "department": "Human Resources",
                        "title": "Director of Talent Acquisition",
                        "team": "Talent Acquisition",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "hiroshi.yamamoto@bigcorp.com": {
                        "id": "user_hiroshi_yamamoto_bigcorp",
                        "email": "hiroshi.yamamoto@bigcorp.com",
                        "name": "Hiroshi Yamamoto",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Human Resources",
                        "title": "Senior HR Business Partner",
                        "team": "HR Business Partners",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "samantha.white@bigcorp.com": {
                        "id": "user_samantha_white_bigcorp",
                        "email": "samantha.white@bigcorp.com",
                        "name": "Samantha White",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Human Resources",
                        "title": "Diversity & Inclusion Manager",
                        "team": "People Operations",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    # Operations Team
                    "christopher.anderson@bigcorp.com": {
                        "id": "user_christopher_anderson_bigcorp",
                        "email": "christopher.anderson@bigcorp.com",
                        "name": "Christopher Anderson",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["manager", "employee"],
                        "department": "Operations",
                        "title": "Director of IT Operations",
                        "team": "IT Operations",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write", "admin"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "fatou.diallo@bigcorp.com": {
                        "id": "user_fatou_diallo_bigcorp",
                        "email": "fatou.diallo@bigcorp.com",
                        "name": "Fatou Diallo",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Operations",
                        "title": "Senior Systems Administrator",
                        "team": "IT Operations",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                    "erik.larsson@bigcorp.com": {
                        "id": "user_erik_larsson_bigcorp",
                        "email": "erik.larsson@bigcorp.com",
                        "name": "Erik Larsson",
                        "tenant_id": "aprio_org_bigcorp",
                        "roles": ["employee"],
                        "department": "Operations",
                        "title": "Security Operations Analyst",
                        "team": "Security Operations",
                        "location": "San Jose, CA",
                        "permissions": ["read", "write"],
                        "created_at": "2024-02-01T00:00:00Z",
                    },
                },
            }
            self._save_json(self.users_file, demo_users)

        # Demo invitation codes
        if not os.path.exists(self.invitations_file):
            demo_invitations = {
                "APRIO-ACME-INV123456789": {
                    "code": "APRIO-ACME-INV123456789",
                    "organizationId": "aprio_org_acme",
                    "createdBy": "admin@acme.com",
                    "role": "employee",
                    "department": "Engineering",
                    "permissions": ["read", "write"],
                    "expiresAt": "2024-12-31T23:59:59Z",
                    "maxUses": 50,
                    "usedCount": 0,
                    "isActive": True,
                },
                "APRIO-TECHCORP-INVITE001": {
                    "code": "APRIO-TECHCORP-INVITE001",
                    "organizationId": "aprio_org_techcorp",
                    "createdBy": "admin@techcorp.io",
                    "role": "employee",
                    "department": "Operations",
                    "permissions": ["read", "write"],
                    "expiresAt": "2024-12-31T23:59:59Z",
                    "maxUses": 25,
                    "usedCount": 0,
                    "isActive": True,
                },
                "APRIO-BIGCORP-ENG2024": {
                    "code": "APRIO-BIGCORP-ENG2024",
                    "organizationId": "aprio_org_bigcorp",
                    "createdBy": "marcus.johnson@bigcorp.com",
                    "role": "employee",
                    "department": "Engineering",
                    "permissions": ["read", "write"],
                    "expiresAt": "2024-12-31T23:59:59Z",
                    "maxUses": 100,
                    "usedCount": 0,
                    "isActive": True,
                },
                "APRIO-BIGCORP-SALES2024": {
                    "code": "APRIO-BIGCORP-SALES2024",
                    "organizationId": "aprio_org_bigcorp",
                    "createdBy": "elena.rodriguez@bigcorp.com",
                    "role": "employee",
                    "department": "Sales",
                    "permissions": ["read", "write"],
                    "expiresAt": "2024-12-31T23:59:59Z",
                    "maxUses": 75,
                    "usedCount": 0,
                    "isActive": True,
                },
                "APRIO-BIGCORP-EXEC2024": {
                    "code": "APRIO-BIGCORP-EXEC2024",
                    "organizationId": "aprio_org_bigcorp",
                    "createdBy": "sarah.chen@bigcorp.com",
                    "role": "manager",
                    "department": "Executive",
                    "permissions": ["read", "write", "admin"],
                    "expiresAt": "2024-12-31T23:59:59Z",
                    "maxUses": 10,
                    "usedCount": 0,
                    "isActive": True,
                },
            }
            self._save_json(self.invitations_file, demo_invitations)

    def _load_json(self, filepath: str) -> Dict[str, Any]:
        """Load JSON data from file."""
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_json(self, filepath: str, data: Dict[str, Any]):
        """Save JSON data to file."""
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    # Organization methods
    async def get_organization_by_email_domain(self, email_domain: str) -> Optional[Dict[str, Any]]:
        """Get organization by email domain."""
        orgs = self._load_json(self.organizations_file)
        for org_id, org in orgs.items():
            if email_domain in org.get("emailDomains", []):
                return org
        return None

    async def get_organization(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get organization by ID."""
        orgs = self._load_json(self.organizations_file)
        return orgs.get(org_id)

    async def validate_invitation_code(self, invitation_code: str) -> Optional[Dict[str, Any]]:
        """Validate invitation code and return invitation data."""
        invitations = self._load_json(self.invitations_file)
        invitation = invitations.get(invitation_code)

        if not invitation or not invitation.get("isActive"):
            return None

        # Check expiration
        expires_at = datetime.fromisoformat(invitation["expiresAt"].replace("Z", "+00:00"))
        if datetime.now(expires_at.tzinfo) > expires_at:
            return None

        # Check usage limit
        if invitation["usedCount"] >= invitation["maxUses"]:
            return None

        return invitation

    async def use_invitation_code(self, invitation_code: str) -> bool:
        """Mark invitation code as used."""
        invitations = self._load_json(self.invitations_file)
        if invitation_code in invitations:
            invitations[invitation_code]["usedCount"] += 1
            self._save_json(self.invitations_file, invitations)
            return True
        return False

    # Tenant methods (compatible with existing Firestore interface)
    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        tenants = self._load_json(self.tenants_file)
        tenant_data = tenants.get(tenant_id)

        if tenant_data:
            return Tenant(
                id=tenant_data["id"],
                name=tenant_data["name"],
                domain=tenant_data.get("domain"),
                settings=tenant_data.get("settings", {}),
                created_at=datetime.fromisoformat(tenant_data["created_at"].replace("Z", "+00:00")),
                updated_at=tenant_data.get("updated_at"),
                is_active=tenant_data.get("is_active", True),
            )
        return None

    async def create_tenant(self, tenant: Tenant) -> bool:
        """Create a new tenant."""
        tenants = self._load_json(self.tenants_file)
        tenants[tenant.id] = {
            "id": tenant.id,
            "name": tenant.name,
            "domain": tenant.domain,
            "settings": tenant.settings,
            "created_at": tenant.created_at.isoformat(),
            "updated_at": tenant.updated_at.isoformat() if tenant.updated_at else None,
            "is_active": tenant.is_active,
        }
        self._save_json(self.tenants_file, tenants)
        return True

    # User methods
    async def get_user_by_email(self, email: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get user by email within tenant."""
        users = self._load_json(self.users_file)
        tenant_users = users.get(tenant_id, {})
        return tenant_users.get(email)

    async def create_user_from_invitation(
        self, email: str, invitation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create user from invitation data."""
        users = self._load_json(self.users_file)
        tenant_id = invitation_data["organizationId"]

        if tenant_id not in users:
            users[tenant_id] = {}

        user_data = {
            "id": f"user_{email.split('@')[0]}_{tenant_id}",
            "email": email,
            "name": email.split("@")[0].title(),
            "tenant_id": tenant_id,
            "roles": [invitation_data["role"]],
            "department": invitation_data["department"],
            "permissions": invitation_data["permissions"],
            "created_at": datetime.now().isoformat(),
            "source": "aprioone_invitation",
        }

        users[tenant_id][email] = user_data
        self._save_json(self.users_file, users)
        return user_data

    async def create_user_from_email_domain(
        self, email: str, org_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create user from email domain binding."""
        users = self._load_json(self.users_file)
        tenant_id = org_data["id"]

        if tenant_id not in users:
            users[tenant_id] = {}

        user_data = {
            "id": f"user_{email.split('@')[0]}_{tenant_id}",
            "email": email,
            "name": email.split("@")[0].title(),
            "tenant_id": tenant_id,
            "roles": ["employee"],
            "department": "General",
            "permissions": ["read", "write"],
            "created_at": datetime.now().isoformat(),
            "source": "email_domain_binding",
        }

        users[tenant_id][email] = user_data
        self._save_json(self.users_file, users)
        return user_data
