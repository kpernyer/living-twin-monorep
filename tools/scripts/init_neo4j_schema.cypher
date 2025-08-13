// =========================
// Living Twin Neo4j Schema
// =========================

// Create constraints for unique identifiers
CREATE CONSTRAINT tenant_id_unique IF NOT EXISTS FOR (t:Tenant) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT goal_id_unique IF NOT EXISTS FOR (g:Goal) REQUIRE g.id IS UNIQUE;
CREATE CONSTRAINT team_id_unique IF NOT EXISTS FOR (t:Team) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT document_id_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT source_id_unique IF NOT EXISTS FOR (s:Source) REQUIRE s.id IS UNIQUE;

// Create indexes for performance
CREATE INDEX tenant_created_at IF NOT EXISTS FOR (t:Tenant) ON (t.created_at);
CREATE INDEX user_email IF NOT EXISTS FOR (u:User) ON (u.email);
CREATE INDEX user_tenant IF NOT EXISTS FOR (u:User) ON (u.tenant_id);
CREATE INDEX goal_tenant IF NOT EXISTS FOR (g:Goal) ON (g.tenant_id);
CREATE INDEX team_tenant IF NOT EXISTS FOR (t:Team) ON (t.tenant_id);
CREATE INDEX document_tenant IF NOT EXISTS FOR (d:Document) ON (d.tenant_id);
CREATE INDEX chunk_tenant IF NOT EXISTS FOR (c:Chunk) ON (c.tenant_id);
CREATE INDEX source_tenant IF NOT EXISTS FOR (s:Source) ON (s.tenant_id);

// Create indexes for common queries
CREATE INDEX document_created_at IF NOT EXISTS FOR (d:Document) ON (d.created_at);
CREATE INDEX chunk_position IF NOT EXISTS FOR (c:Chunk) ON (c.position);
CREATE INDEX user_role IF NOT EXISTS FOR (u:User) ON (u.role);
CREATE INDEX goal_status IF NOT EXISTS FOR (g:Goal) ON (g.status);

// Create vector indexes for embeddings (384 dimensions - sentence-transformers)
CALL db.index.vector.createNodeIndex(
  'document_embeddings_384',
  'Document',
  'embedding_384',
  384,
  'cosine'
);

CALL db.index.vector.createNodeIndex(
  'chunk_embeddings_384',
  'Chunk',
  'embedding_384',
  384,
  'cosine'
);

CALL db.index.vector.createNodeIndex(
  'goal_embeddings_384',
  'Goal', 
  'embedding_384',
  384,
  'cosine'
);

// Create vector indexes for embeddings (1536 dimensions - OpenAI)
CALL db.index.vector.createNodeIndex(
  'document_embeddings_1536', 
  'Document',
  'embedding_1536',
  1536,
  'cosine'
);

CALL db.index.vector.createNodeIndex(
  'chunk_embeddings_1536',
  'Chunk',
  'embedding_1536',
  1536,
  'cosine'
);

CALL db.index.vector.createNodeIndex(
  'goal_embeddings_1536',
  'Goal',
  'embedding_1536', 
  1536,
  'cosine'
);

// Create sample data structure (optional - for testing)
// Uncomment the following lines if you want to create sample data

/*
// Create sample tenant
CREATE (tenant:Tenant {
  id: 'tenant-demo',
  name: 'Demo Organization',
  created_at: datetime(),
  settings: {
    embedding_model: 'sentence-transformers',
    max_chunk_size: 1000,
    chunk_overlap: 200
  }
});

// Create sample admin user
CREATE (admin:User {
  id: 'user-admin',
  tenant_id: 'tenant-demo',
  email: 'admin@demo.com',
  name: 'Admin User',
  role: 'admin',
  created_at: datetime(),
  last_login: datetime()
});

// Create sample team
CREATE (team:Team {
  id: 'team-engineering',
  tenant_id: 'tenant-demo',
  name: 'Engineering Team',
  description: 'Software development team',
  created_at: datetime()
});

// Create sample goal
CREATE (goal:Goal {
  id: 'goal-product-launch',
  tenant_id: 'tenant-demo',
  title: 'Launch MVP Product',
  description: 'Complete and launch the minimum viable product',
  status: 'in_progress',
  priority: 'high',
  created_at: datetime(),
  due_date: datetime() + duration('P30D')
});

// Create relationships
MATCH (admin:User {id: 'user-admin'}), (tenant:Tenant {id: 'tenant-demo'})
CREATE (admin)-[:BELONGS_TO]->(tenant);

MATCH (admin:User {id: 'user-admin'}), (team:Team {id: 'team-engineering'})
CREATE (admin)-[:MEMBER_OF]->(team);

MATCH (team:Team {id: 'team-engineering'}), (goal:Goal {id: 'goal-product-launch'})
CREATE (team)-[:OWNS]->(goal);

MATCH (team:Team {id: 'team-engineering'}), (tenant:Tenant {id: 'tenant-demo'})
CREATE (team)-[:BELONGS_TO]->(tenant);

MATCH (goal:Goal {id: 'goal-product-launch'}), (tenant:Tenant {id: 'tenant-demo'})
CREATE (goal)-[:BELONGS_TO]->(tenant);
*/
