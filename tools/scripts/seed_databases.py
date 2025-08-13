#!/usr/bin/env python3
"""
Database seeding script for local development.
Seeds both Firebase/Firestore and Neo4j with demo organizations and users.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'api'))

from app.adapters.local_mock_repo import LocalMockRepository
from app.adapters.neo4j_store import Neo4jVectorStore
from app.config import get_settings


class DatabaseSeeder:
    """Seeds databases with demo data for development."""
    
    def __init__(self):
        self.settings = get_settings()
        self.mock_repo = LocalMockRepository()
        self.neo4j_store = None
        
    async def init_neo4j(self):
        """Initialize Neo4j connection."""
        try:
            self.neo4j_store = Neo4jVectorStore(
                uri=self.settings.neo4j_uri,
                user=self.settings.neo4j_user,
                password=self.settings.neo4j_password,
                database=self.settings.neo4j_db
            )
            print("✅ Connected to Neo4j")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            return False
        return True
    
    async def seed_neo4j_demo_documents(self):
        """Seed Neo4j with demo documents for each organization."""
        if not self.neo4j_store:
            print("❌ Neo4j not initialized")
            return
            
        print("🌱 Seeding Neo4j with demo documents...")
        
        # Demo documents for each organization
        demo_docs = {
            "aprio_org_acme": [
                {
                    "content": "Acme Corporation Engineering Handbook: Our engineering team follows agile methodologies with 2-week sprints. We use React for frontend, Python/FastAPI for backend, and PostgreSQL for data storage. Code reviews are mandatory for all pull requests.",
                    "metadata": {
                        "title": "Engineering Handbook",
                        "department": "Engineering",
                        "document_type": "handbook",
                        "author": "John Doe",
                        "created_date": "2024-01-15"
                    }
                },
                {
                    "content": "Acme Corporation HR Policy: All employees are entitled to 20 days of paid vacation per year, plus 10 sick days. Remote work is allowed up to 3 days per week with manager approval. Performance reviews are conducted quarterly.",
                    "metadata": {
                        "title": "HR Policy Manual",
                        "department": "Human Resources",
                        "document_type": "policy",
                        "author": "Alice Admin",
                        "created_date": "2024-01-10"
                    }
                }
            ],
            "aprio_org_techcorp": [
                {
                    "content": "TechCorp Industries Safety Manual: All manufacturing floor personnel must wear safety equipment including hard hats, safety glasses, and steel-toed boots. Emergency procedures are posted at each workstation. Report all incidents immediately to your supervisor.",
                    "metadata": {
                        "title": "Safety Manual",
                        "department": "Operations",
                        "document_type": "manual",
                        "author": "Bob Smith",
                        "created_date": "2024-01-20"
                    }
                }
            ],
            "aprio_org_bigcorp": [
                {
                    "content": "BIG Corp Solutions Platform Architecture: Our microservices architecture consists of API Gateway, Authentication Service, User Management Service, and Analytics Service. All services communicate via REST APIs and are deployed on Kubernetes clusters.",
                    "metadata": {
                        "title": "Platform Architecture Guide",
                        "department": "Engineering",
                        "document_type": "technical_doc",
                        "author": "Marcus Johnson",
                        "created_date": "2024-02-01"
                    }
                },
                {
                    "content": "BIG Corp Sales Playbook: Our enterprise sales process follows a 7-stage methodology: Lead Qualification, Discovery, Solution Design, Proposal, Negotiation, Closing, and Onboarding. Average sales cycle is 6-9 months for enterprise deals.",
                    "metadata": {
                        "title": "Enterprise Sales Playbook",
                        "department": "Sales",
                        "document_type": "playbook",
                        "author": "Elena Rodriguez",
                        "created_date": "2024-02-05"
                    }
                },
                {
                    "content": "BIG Corp Engineering Team Structure: Platform Engineering (San Jose) - 12 engineers, Frontend Engineering (San Jose) - 8 engineers, Backend Engineering (San Jose) - 10 engineers, Austin Engineering (Austin, TX) - 15 engineers. Each team has dedicated DevOps and QA resources.",
                    "metadata": {
                        "title": "Engineering Organization Chart",
                        "department": "Engineering",
                        "document_type": "org_chart",
                        "author": "Priya Patel",
                        "created_date": "2024-02-10"
                    }
                },
                {
                    "content": "BIG Corp Customer Success Framework: Our customer success team manages accounts through three phases: Onboarding (0-90 days), Adoption (90-365 days), and Growth (365+ days). Success metrics include product adoption rate, customer satisfaction score, and renewal rate.",
                    "metadata": {
                        "title": "Customer Success Framework",
                        "department": "Sales",
                        "document_type": "framework",
                        "author": "Linda Garcia",
                        "created_date": "2024-02-15"
                    }
                }
            ]
        }
        
        # Seed documents for each organization
        for tenant_id, documents in demo_docs.items():
            print(f"  📄 Seeding documents for {tenant_id}...")
            for i, doc in enumerate(documents):
                try:
                    # Create document chunks (simulate document processing)
                    chunks = self._create_document_chunks(doc["content"], doc["metadata"])
                    
                    for chunk_idx, chunk in enumerate(chunks):
                        # Generate a simple embedding (in real scenario, this would use OpenAI/local embeddings)
                        embedding = self._generate_mock_embedding(chunk["content"])
                        
                        # Store in Neo4j
                        await self.neo4j_store.upsert_document(
                            doc_id=f"{tenant_id}_doc_{i}_chunk_{chunk_idx}",
                            content=chunk["content"],
                            embedding=embedding,
                            metadata={
                                **chunk["metadata"],
                                "tenant_id": tenant_id,
                                "chunk_index": chunk_idx,
                                "total_chunks": len(chunks)
                            }
                        )
                    
                    print(f"    ✅ Added document: {doc['metadata']['title']}")
                    
                except Exception as e:
                    print(f"    ❌ Failed to add document {doc['metadata']['title']}: {e}")
        
        print("✅ Neo4j seeding completed!")
    
    def _create_document_chunks(self, content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split document content into chunks."""
        # Simple chunking by sentences (in real scenario, use more sophisticated chunking)
        sentences = content.split('. ')
        chunks = []
        
        chunk_size = 2  # 2 sentences per chunk
        for i in range(0, len(sentences), chunk_size):
            chunk_sentences = sentences[i:i + chunk_size]
            chunk_content = '. '.join(chunk_sentences)
            if not chunk_content.endswith('.'):
                chunk_content += '.'
                
            chunks.append({
                "content": chunk_content,
                "metadata": metadata.copy()
            })
        
        return chunks
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate a mock embedding vector for development."""
        # Simple hash-based mock embedding (1536 dimensions like OpenAI)
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert hex to float values between -1 and 1
        embedding = []
        for i in range(0, len(hash_hex), 2):
            hex_pair = hash_hex[i:i+2]
            # Convert hex to int, normalize to [-1, 1]
            val = (int(hex_pair, 16) - 127.5) / 127.5
            embedding.append(val)
        
        # Pad or truncate to 1536 dimensions
        while len(embedding) < 1536:
            embedding.extend(embedding[:min(len(embedding), 1536 - len(embedding))])
        
        return embedding[:1536]
    
    async def seed_firestore_emulator(self):
        """Seed Firestore emulator with demo data."""
        print("🌱 Seeding Firestore emulator...")
        
        try:
            # Check if Firebase emulator is running
            import requests
            response = requests.get("http://localhost:8080", timeout=5)
            if response.status_code != 200:
                print("❌ Firestore emulator not running on localhost:8080")
                return
        except:
            print("❌ Firestore emulator not accessible")
            return
        
        try:
            from google.cloud import firestore
            from google.auth.credentials import AnonymousCredentials
            
            # Connect to emulator
            os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
            db = firestore.Client(
                project="demo-project",
                credentials=AnonymousCredentials()
            )
            
            # Load demo data from mock repository
            orgs = self.mock_repo._load_json(self.mock_repo.organizations_file)
            users = self.mock_repo._load_json(self.mock_repo.users_file)
            invitations = self.mock_repo._load_json(self.mock_repo.invitations_file)
            
            # Seed organizations
            print("  📊 Seeding organizations...")
            for org_id, org_data in orgs.items():
                db.collection("organizations").document(org_id).set(org_data)
                print(f"    ✅ Added organization: {org_data['name']}")
            
            # Seed users
            print("  👥 Seeding users...")
            for tenant_id, tenant_users in users.items():
                for email, user_data in tenant_users.items():
                    # Store in users collection with tenant-based document structure
                    db.collection("tenants").document(tenant_id).collection("users").document(user_data["id"]).set(user_data)
                    print(f"    ✅ Added user: {user_data['name']} ({email})")
            
            # Seed invitation codes
            print("  🎫 Seeding invitation codes...")
            for code, invitation_data in invitations.items():
                db.collection("invitations").document(code).set(invitation_data)
                print(f"    ✅ Added invitation: {code}")
            
            print("✅ Firestore seeding completed!")
            
        except ImportError:
            print("❌ google-cloud-firestore not installed. Install with: pip install google-cloud-firestore")
        except Exception as e:
            print(f"❌ Failed to seed Firestore: {e}")
    
    async def create_neo4j_indexes(self):
        """Create necessary indexes and constraints in Neo4j."""
        if not self.neo4j_store:
            return
            
        print("🔧 Creating Neo4j indexes and constraints...")
        
        try:
            # Read the setup script
            setup_script_path = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', 'apps', 'api', 'app', 'ingest', 'neo4j_setup.cypher'
            )
            
            if os.path.exists(setup_script_path):
                with open(setup_script_path, 'r') as f:
                    setup_commands = f.read().split(';')
                
                for command in setup_commands:
                    command = command.strip()
                    if command:
                        await self.neo4j_store._execute_query(command)
                        print(f"    ✅ Executed: {command[:50]}...")
                
                print("✅ Neo4j setup completed!")
            else:
                print("❌ Neo4j setup script not found")
                
        except Exception as e:
            print(f"❌ Failed to setup Neo4j: {e}")
    
    async def run_seeding(self, seed_neo4j: bool = True, seed_firestore: bool = True):
        """Run the complete seeding process."""
        print("🌱 Starting database seeding...")
        print("=" * 50)
        
        if seed_neo4j:
            if await self.init_neo4j():
                await self.create_neo4j_indexes()
                await self.seed_neo4j_demo_documents()
            else:
                print("⚠️  Skipping Neo4j seeding due to connection issues")
        
        if seed_firestore:
            await self.seed_firestore_emulator()
        
        print("=" * 50)
        print("🎉 Database seeding completed!")
        print("\n📚 Demo Data Available:")
        print("  • 4 Organizations (Acme, TechCorp, Demo, BIG Corp)")
        print("  • 50+ Users across all organizations")
        print("  • 5+ Invitation codes")
        print("  • 10+ Demo documents with embeddings")
        print("\n🚀 Ready for development!")


async def main():
    """Main seeding function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed databases with demo data")
    parser.add_argument("--neo4j-only", action="store_true", help="Seed only Neo4j")
    parser.add_argument("--firestore-only", action="store_true", help="Seed only Firestore")
    parser.add_argument("--skip-neo4j", action="store_true", help="Skip Neo4j seeding")
    parser.add_argument("--skip-firestore", action="store_true", help="Skip Firestore seeding")
    
    args = parser.parse_args()
    
    seed_neo4j = not args.skip_neo4j and not args.firestore_only
    seed_firestore = not args.skip_firestore and not args.neo4j_only
    
    seeder = DatabaseSeeder()
    await seeder.run_seeding(seed_neo4j=seed_neo4j, seed_firestore=seed_firestore)


if __name__ == "__main__":
    asyncio.run(main())
