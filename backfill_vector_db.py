#!/usr/bin/env python3
"""
Backfill existing plans from SQLite to ChromaDB Vector Store
"""
import sqlite3
import json
import sys
sys.path.insert(0, '.')

from app.memory.vector_memory import VectorMemory

def backfill():
    """Backfill all existing plans from SQLite to Vector DB"""

    # Connect to SQLite
    conn = sqlite3.connect('ad_planner.db')
    cursor = conn.cursor()

    # Initialize Vector Memory
    vector_memory = VectorMemory(persist_directory="./vector_store")

    print("=" * 60)
    print("  BACKFILLING PLANS TO VECTOR DATABASE")
    print("=" * 60)

    # Get all plans
    cursor.execute('''
        SELECT p.id, u.session_id, p.profile_json, p.plan_json, p.created_at
        FROM plans p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at ASC
    ''')

    plans = cursor.fetchall()
    total_plans = len(plans)

    print(f"\nFound {total_plans} plans to backfill\n")

    success_count = 0
    error_count = 0

    for i, (plan_id, session_id, profile_json, plan_json, created_at) in enumerate(plans, 1):
        try:
            profile = json.loads(profile_json)
            plan = json.loads(plan_json)

            # Store business profile
            vector_memory.store_business_profile(session_id, profile)

            # Store plan
            plan_doc_id = f"plan_{session_id}_{int(created_at.replace('-', '').replace(':', '').replace(' ', '_'))}"
            vector_memory.store_plan(session_id, plan_doc_id, plan)

            print(f"[{i}/{total_plans}] ✓ Backfilled: {profile.get('business_name')} ({profile.get('business_type')})")
            success_count += 1

        except Exception as e:
            print(f"[{i}/{total_plans}] ✗ Error: {e}")
            error_count += 1

    conn.close()

    print("\n" + "=" * 60)
    print(f"  BACKFILL COMPLETE")
    print(f"  Success: {success_count} | Errors: {error_count}")
    print("=" * 60)

    # Verify the backfill
    print("\n\nVERIFYING VECTOR DATABASE...")
    print("-" * 60)

    if vector_memory.user_memory:
        user_count = vector_memory.user_memory.count()
        print(f"User Profiles in Vector DB: {user_count}")

    if vector_memory.plan_memory:
        plan_count = vector_memory.plan_memory.count()
        print(f"Plans in Vector DB: {plan_count}")

    print("\n✓ Backfill completed successfully!\n")

if __name__ == "__main__":
    backfill()
