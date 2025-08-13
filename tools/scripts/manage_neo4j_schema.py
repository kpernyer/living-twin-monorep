#!/usr/bin/env python3
"""
Neo4j Schema Management for Living Twin

This script manages Neo4j schema operations including:
- Creating constraints and indexes
- Setting up vector indexes for embeddings
- Managing schema migrations
- Validating schema integrity
"""

import os
import sys
import argparse
import json
from typing import List, Dict, Any
from neo4j import GraphDatabase
from neo4j.exceptions import ClientError

class Neo4jSchemaManager:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        """Close the database connection"""
        self.driver.close()
        
    def run_cypher_file(self, file_path: str) -> None:
        """Run a Cypher file against Neo4j"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Cypher file not found: {file_path}")
            
        with open(file_path, 'r') as f:
            cypher_content = f.read()
        
        # Remove comments and split by semicolon
        lines = cypher_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove comments but preserve lines inside /* */ blocks
            if not line.strip().startswith('//'):
                cleaned_lines.append(line)
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in cleaned_content.split(';') if stmt.strip()]
        
        with self.driver.session() as session:
            for statement in statements:
                if statement and not statement.startswith('/*'):
                    try:
                        print(f"Executing: {statement[:80]}...")
                        result = session.run(statement)
                        # Consume the result to ensure execution
                        summary = result.consume()
                        print(f"✅ Success - {summary.counters}")
                    except ClientError as e:
                        if "already exists" in str(e) or "equivalent" in str(e):
                            print(f"⚠️  Already exists: {statement[:50]}...")
                        else:
                            print(f"❌ Error: {e}")
                            raise
                            
    def check_constraints(self) -> List[Dict[str, Any]]:
        """Check existing constraints"""
        with self.driver.session() as session:
            result = session.run("SHOW CONSTRAINTS")
            constraints = []
            for record in result:
                constraints.append({
                    'name': record.get('name'),
                    'type': record.get('type'),
                    'entityType': record.get('entityType'),
                    'labelsOrTypes': record.get('labelsOrTypes'),
                    'properties': record.get('properties')
                })
            return constraints
            
    def check_indexes(self) -> List[Dict[str, Any]]:
        """Check existing indexes"""
        with self.driver.session() as session:
            result = session.run("SHOW INDEXES")
            indexes = []
            for record in result:
                indexes.append({
                    'name': record.get('name'),
                    'type': record.get('type'),
                    'entityType': record.get('entityType'),
                    'labelsOrTypes': record.get('labelsOrTypes'),
                    'properties': record.get('properties'),
                    'state': record.get('state')
                })
            return indexes
            
    def check_vector_indexes(self) -> List[Dict[str, Any]]:
        """Check vector indexes specifically"""
        indexes = self.check_indexes()
        vector_indexes = [idx for idx in indexes if idx.get('type') == 'VECTOR']
        return vector_indexes
        
    def validate_schema(self) -> Dict[str, Any]:
        """Validate the current schema against expected structure"""
        validation_results = {
            'constraints': {'expected': 7, 'actual': 0, 'missing': []},
            'indexes': {'expected': 8, 'actual': 0, 'missing': []},
            'vector_indexes': {'expected': 6, 'actual': 0, 'missing': []},
            'valid': True
        }
        
        # Expected constraints
        expected_constraints = [
            'tenant_id_unique', 'user_id_unique', 'goal_id_unique',
            'team_id_unique', 'document_id_unique', 'chunk_id_unique', 'source_id_unique'
        ]
        
        # Expected regular indexes
        expected_indexes = [
            'tenant_created_at', 'user_email', 'user_tenant', 'goal_tenant',
            'team_tenant', 'document_tenant', 'chunk_tenant', 'source_tenant'
        ]
        
        # Expected vector indexes
        expected_vector_indexes = [
            'document_embeddings_384', 'document_embeddings_1536',
            'chunk_embeddings_384', 'chunk_embeddings_1536',
            'goal_embeddings_384', 'goal_embeddings_1536'
        ]
        
        # Check constraints
        constraints = self.check_constraints()
        constraint_names = [c['name'] for c in constraints if c['name']]
        validation_results['constraints']['actual'] = len(constraint_names)
        validation_results['constraints']['missing'] = [
            name for name in expected_constraints if name not in constraint_names
        ]
        
        # Check regular indexes
        indexes = self.check_indexes()
        regular_indexes = [idx for idx in indexes if idx.get('type') != 'VECTOR']
        index_names = [idx['name'] for idx in regular_indexes if idx['name']]
        validation_results['indexes']['actual'] = len(index_names)
        validation_results['indexes']['missing'] = [
            name for name in expected_indexes if name not in index_names
        ]
        
        # Check vector indexes
        vector_indexes = self.check_vector_indexes()
        vector_index_names = [idx['name'] for idx in vector_indexes if idx['name']]
        validation_results['vector_indexes']['actual'] = len(vector_index_names)
        validation_results['vector_indexes']['missing'] = [
            name for name in expected_vector_indexes if name not in vector_index_names
        ]
        
        # Determine if schema is valid
        validation_results['valid'] = (
            len(validation_results['constraints']['missing']) == 0 and
            len(validation_results['indexes']['missing']) == 0 and
            len(validation_results['vector_indexes']['missing']) == 0
        )
        
        return validation_results
        
    def create_sample_data(self) -> None:
        """Create sample data for testing"""
        sample_cypher = """
        // Create sample tenant
        MERGE (tenant:Tenant {id: 'tenant-demo'})
        SET tenant.name = 'Demo Organization',
            tenant.created_at = datetime(),
            tenant.settings = {
                embedding_model: 'sentence-transformers',
                max_chunk_size: 1000,
                chunk_overlap: 200
            };

        // Create sample admin user
        MERGE (admin:User {id: 'user-admin'})
        SET admin.tenant_id = 'tenant-demo',
            admin.email = 'admin@demo.com',
            admin.name = 'Admin User',
            admin.role = 'admin',
            admin.created_at = datetime(),
            admin.last_login = datetime();

        // Create sample team
        MERGE (team:Team {id: 'team-engineering'})
        SET team.tenant_id = 'tenant-demo',
            team.name = 'Engineering Team',
            team.description = 'Software development team',
            team.created_at = datetime();

        // Create sample goal
        MERGE (goal:Goal {id: 'goal-product-launch'})
        SET goal.tenant_id = 'tenant-demo',
            goal.title = 'Launch MVP Product',
            goal.description = 'Complete and launch the minimum viable product',
            goal.status = 'in_progress',
            goal.priority = 'high',
            goal.created_at = datetime(),
            goal.due_date = datetime() + duration('P30D');

        // Create relationships
        MATCH (admin:User {id: 'user-admin'}), (tenant:Tenant {id: 'tenant-demo'})
        MERGE (admin)-[:BELONGS_TO]->(tenant);

        MATCH (admin:User {id: 'user-admin'}), (team:Team {id: 'team-engineering'})
        MERGE (admin)-[:MEMBER_OF]->(team);

        MATCH (team:Team {id: 'team-engineering'}), (goal:Goal {id: 'goal-product-launch'})
        MERGE (team)-[:OWNS]->(goal);

        MATCH (team:Team {id: 'team-engineering'}), (tenant:Tenant {id: 'tenant-demo'})
        MERGE (team)-[:BELONGS_TO]->(tenant);

        MATCH (goal:Goal {id: 'goal-product-launch'}), (tenant:Tenant {id: 'tenant-demo'})
        MERGE (goal)-[:BELONGS_TO]->(tenant);
        """
        
        with self.driver.session() as session:
            print("🌱 Creating sample data...")
            session.run(sample_cypher)
            print("✅ Sample data created successfully!")
            
    def cleanup_sample_data(self) -> None:
        """Remove sample data"""
        cleanup_cypher = """
        MATCH (n) WHERE n.id STARTS WITH 'tenant-demo' OR n.id STARTS WITH 'user-admin' 
                     OR n.id STARTS WITH 'team-engineering' OR n.id STARTS WITH 'goal-product-launch'
        DETACH DELETE n;
        """
        
        with self.driver.session() as session:
            print("🧹 Cleaning up sample data...")
            session.run(cleanup_cypher)
            print("✅ Sample data cleaned up!")

def main():
    parser = argparse.ArgumentParser(description="Manage Neo4j schema for Living Twin")
    parser.add_argument("--uri", required=True, help="Neo4j URI (e.g., bolt://localhost:7687)")
    parser.add_argument("--user", required=True, help="Neo4j username")
    parser.add_argument("--password", required=True, help="Neo4j password")
    
    # Actions
    parser.add_argument("--init", action="store_true", help="Initialize schema from Cypher file")
    parser.add_argument("--validate", action="store_true", help="Validate current schema")
    parser.add_argument("--list-constraints", action="store_true", help="List all constraints")
    parser.add_argument("--list-indexes", action="store_true", help="List all indexes")
    parser.add_argument("--list-vector-indexes", action="store_true", help="List vector indexes")
    parser.add_argument("--create-sample-data", action="store_true", help="Create sample data")
    parser.add_argument("--cleanup-sample-data", action="store_true", help="Remove sample data")
    
    # Options
    parser.add_argument("--cypher-file", default="tools/scripts/init_neo4j_schema.cypher", 
                       help="Path to Cypher file for initialization")
    parser.add_argument("--json-output", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    # Create schema manager
    manager = Neo4jSchemaManager(args.uri, args.user, args.password)
    
    try:
        if args.init:
            print("🔧 Initializing Neo4j schema...")
            manager.run_cypher_file(args.cypher_file)
            print("✅ Schema initialized successfully!")
            
        elif args.validate:
            print("🔍 Validating Neo4j schema...")
            validation = manager.validate_schema()
            
            if args.json_output:
                print(json.dumps(validation, indent=2))
            else:
                print(f"Schema validation: {'✅ VALID' if validation['valid'] else '❌ INVALID'}")
                print(f"Constraints: {validation['constraints']['actual']}/{validation['constraints']['expected']}")
                print(f"Indexes: {validation['indexes']['actual']}/{validation['indexes']['expected']}")
                print(f"Vector Indexes: {validation['vector_indexes']['actual']}/{validation['vector_indexes']['expected']}")
                
                if validation['constraints']['missing']:
                    print(f"Missing constraints: {validation['constraints']['missing']}")
                if validation['indexes']['missing']:
                    print(f"Missing indexes: {validation['indexes']['missing']}")
                if validation['vector_indexes']['missing']:
                    print(f"Missing vector indexes: {validation['vector_indexes']['missing']}")
                    
        elif args.list_constraints:
            constraints = manager.check_constraints()
            if args.json_output:
                print(json.dumps(constraints, indent=2))
            else:
                print("📋 Neo4j Constraints:")
                for constraint in constraints:
                    print(f"  • {constraint['name']} ({constraint['type']})")
                    
        elif args.list_indexes:
            indexes = manager.check_indexes()
            if args.json_output:
                print(json.dumps(indexes, indent=2))
            else:
                print("📋 Neo4j Indexes:")
                for index in indexes:
                    print(f"  • {index['name']} ({index['type']}) - {index['state']}")
                    
        elif args.list_vector_indexes:
            vector_indexes = manager.check_vector_indexes()
            if args.json_output:
                print(json.dumps(vector_indexes, indent=2))
            else:
                print("📋 Neo4j Vector Indexes:")
                for index in vector_indexes:
                    print(f"  • {index['name']} - {index['state']}")
                    
        elif args.create_sample_data:
            manager.create_sample_data()
            
        elif args.cleanup_sample_data:
            manager.cleanup_sample_data()
            
        else:
            print("❌ No action specified. Use --help for available options.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        manager.close()

if __name__ == "__main__":
    main()
