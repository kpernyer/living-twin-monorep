
CREATE CONSTRAINT doc_id IF NOT EXISTS
FOR (d:Doc) REQUIRE d.id IS UNIQUE;

CREATE VECTOR INDEX docEmbeddings IF NOT EXISTS
FOR (d:Doc) ON (d.embedding)
OPTIONS {indexConfig: { `vector.dimensions`: 1536, `vector.similarity_function`: 'cosine' }};
