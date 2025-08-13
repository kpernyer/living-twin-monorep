#!/bin/bash
set -e

echo "🔧 Database initialization script starting..."

# Wait for Neo4j to be ready
echo "⏳ Waiting for Neo4j to be ready..."
until curl -f http://neo4j:7474/db/data/ >/dev/null 2>&1; do
    echo "  Neo4j not ready yet, waiting..."
    sleep 5
done
echo "✅ Neo4j is ready!"

# Wait for Firestore emulator to be ready (if running)
if [ "$USE_LOCAL_MOCK" != "true" ]; then
    echo "⏳ Waiting for Firestore emulator to be ready..."
    until curl -f http://firebase-emulator:8080 >/dev/null 2>&1; do
        echo "  Firestore emulator not ready yet, waiting..."
        sleep 5
    done
    echo "✅ Firestore emulator is ready!"
fi

# Run the seeding script
echo "🌱 Starting database seeding..."
cd /app

if [ "$USE_LOCAL_MOCK" = "true" ]; then
    echo "📁 Using local mock database - seeding Neo4j only..."
    python tools/scripts/seed_databases.py --neo4j-only
else
    echo "🔥 Using Firebase emulators - seeding both databases..."
    python tools/scripts/seed_databases.py
fi

echo "🎉 Database initialization completed!"
