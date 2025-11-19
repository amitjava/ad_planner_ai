#!/usr/bin/env python3
"""
ChromaDB Query Examples - Understanding Vector Database Queries
Unlike SQL which uses exact matches, ChromaDB uses semantic similarity
"""
import chromadb
import json

# Connect to the database
client = chromadb.PersistentClient(path='./vector_store')

print("="*70)
print("  CHROMADB QUERY EXAMPLES - Vector Database 101")
print("="*70)

# Get collections (like SQL tables)
plan_memory = client.get_collection('plan_memory')
user_memory = client.get_collection('user_memory')

print("\n📚 EXAMPLE 1: Get All Documents (like SELECT * FROM table)")
print("-"*70)
print("SQL equivalent: SELECT * FROM plan_memory LIMIT 3;\n")

results = plan_memory.get(limit=3, include=['documents', 'metadatas'])

for i, (doc_id, meta) in enumerate(zip(results['ids'], results['metadatas']), 1):
    print(f"{i}. ID: {doc_id[:40]}...")
    print(f"   Metadata: {meta}")
    print()

print("\n📚 EXAMPLE 2: Get by ID (like SELECT WHERE id = 'xxx')")
print("-"*70)
print("SQL equivalent: SELECT * FROM user_memory WHERE id = 'profile_xxx';\n")

# Get the first profile ID
first_id = user_memory.get(limit=1)['ids'][0]
result = user_memory.get(ids=[first_id], include=['documents', 'metadatas'])

print(f"Query: Get profile {first_id[:40]}...")
print(f"Result: {result['documents'][0][:200]}...")
print()

print("\n📚 EXAMPLE 3: Filter by Metadata (like SELECT WHERE column = value)")
print("-"*70)
print("SQL equivalent: SELECT * FROM user_memory WHERE type = 'profile';\n")

results = user_memory.get(
    where={"type": "profile"},
    limit=3,
    include=['metadatas']
)

print(f"Found {len(results['ids'])} profiles:")
for i, meta in enumerate(results['metadatas'][:3], 1):
    print(f"{i}. Session: {meta['session_id'][:20]}... | Type: {meta['type']}")
print()

print("\n📚 EXAMPLE 4: Semantic Search (UNIQUE TO VECTOR DB - No SQL equivalent!)")
print("-"*70)
print("This is where vector databases shine - finding similar content by meaning\n")

# Query 1: Coffee shop
print("Query 1: 'Coffee shop in Portland with morning rush hour focus'")
results = user_memory.query(
    query_texts=["Coffee shop in Portland with morning rush hour focus"],
    n_results=3,
    include=['documents', 'metadatas', 'distances']
)

for i, (doc, meta, dist) in enumerate(zip(
    results['documents'][0],
    results['metadatas'][0],
    results['distances'][0]
), 1):
    similarity = (1 - dist) * 100
    print(f"\n  [{i}] Similarity: {similarity:.1f}%")
    print(f"      Session: {meta['session_id'][:20]}...")
    lines = [l.strip() for l in doc.split('\n') if l.strip()][:3]
    for line in lines:
        print(f"      {line}")

print("\n" + "-"*70)

# Query 2: Yoga studio
print("\nQuery 2: 'Yoga studio targeting health-conscious professionals'")
results = user_memory.query(
    query_texts=["Yoga studio targeting health-conscious professionals"],
    n_results=2,
    include=['distances']
)

for i, dist in enumerate(results['distances'][0], 1):
    similarity = (1 - dist) * 100
    print(f"  [{i}] Similarity: {similarity:.1f}%")

print("\n" + "-"*70)

# Query 3: Budget-focused
print("\nQuery 3: 'Small business with $2500 monthly budget'")
results = plan_memory.query(
    query_texts=["Small business with $2500 monthly budget"],
    n_results=3,
    include=['documents', 'distances']
)

for i, (doc, dist) in enumerate(zip(results['documents'][0], results['distances'][0]), 1):
    try:
        plan = json.loads(doc)
        budget = plan.get('scenarios', {}).get('standard_plan', {}).get('total_budget', 'N/A')
        persona = plan.get('persona', {}).get('name', 'N/A')
        similarity = (1 - dist) * 100

        print(f"  [{i}] Similarity: {similarity:.1f}% | Budget: ${budget} | Persona: {persona}")
    except:
        pass

print("\n📚 EXAMPLE 5: Count Documents (like SELECT COUNT(*) FROM table)")
print("-"*70)

print(f"Total profiles: {user_memory.count()}")
print(f"Total plans: {plan_memory.count()}")

print("\n📚 EXAMPLE 6: Complex Query with Filters + Semantic Search")
print("-"*70)
print("Find plans similar to 'local marketing' with specific metadata\n")

# Note: ChromaDB supports combining semantic search with metadata filters
results = plan_memory.query(
    query_texts=["local marketing strategy for small business"],
    n_results=3,
    include=['documents', 'distances']
    # You can add metadata filters here
    # where={"session_id": {"$ne": "some_id"}}  # Not equal
)

print(f"Found {len(results['documents'][0])} similar plans")
for i, dist in enumerate(results['distances'][0], 1):
    similarity = (1 - dist) * 100
    print(f"  [{i}] Similarity: {similarity:.1f}%")

print("\n" + "="*70)
print("  KEY DIFFERENCES: SQL vs Vector Database")
print("="*70)

print("""
SQL (Relational Database):
  SELECT * FROM plans WHERE business_type = 'Coffee Shop';
  → Exact match on text
  → Returns only perfect matches
  → Fast for structured queries

ChromaDB (Vector Database):
  collection.query("coffee shop business")
  → Semantic similarity search
  → Returns similar results even with different wording
  → Understands context and meaning
  → Returns results ranked by similarity

WHEN TO USE EACH:
  SQL: Exact lookups, structured data, transactions
  Vector DB: Similarity search, recommendations, AI/ML applications
""")

print("\n" + "="*70)
print("  COMMON CHROMADB OPERATIONS")
print("="*70)

print("""
1. Get all documents:
   collection.get(limit=100)

2. Get by ID:
   collection.get(ids=['id1', 'id2'])

3. Filter by metadata:
   collection.get(where={"type": "profile"})

4. Semantic search:
   collection.query(query_texts=["your search"], n_results=5)

5. Count documents:
   collection.count()

6. Delete documents:
   collection.delete(ids=['id1'])

7. Update documents:
   collection.update(ids=['id1'], documents=['new text'])

8. Add new documents:
   collection.add(
       documents=["text"],
       metadatas=[{"key": "value"}],
       ids=["unique_id"]
   )
""")

print("="*70)
print("  ✓ Run this script anytime: python3 query_examples.py")
print("="*70)
