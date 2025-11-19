#!/usr/bin/env python3
"""
Quick Database Viewer
Run: python3 view_db.py
"""
import sqlite3
import json
from datetime import datetime

db_path = "ad_planner.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("DATABASE SUMMARY")
print("=" * 80)

# Count records
cursor.execute("SELECT COUNT(*) FROM users")
total_users = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM plans")
total_plans = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM feedback")
total_feedback = cursor.fetchone()[0]

print(f"Total Users: {total_users}")
print(f"Total Plans: {total_plans}")
print(f"Total Feedback: {total_feedback}")

print("\n" + "=" * 80)
print("RECENT PLANS (Last 5)")
print("=" * 80)

cursor.execute("""
    SELECT p.id, u.session_id, p.created_at
    FROM plans p
    JOIN users u ON p.user_id = u.id
    ORDER BY p.created_at DESC
    LIMIT 5
""")

for row in cursor.fetchall():
    plan_id = row[0]
    session_id = row[1][:16] + "..." if len(row[1]) > 16 else row[1]
    created_at = row[2]
    print(f"Plan ID: {plan_id:2d} | Session: {session_id:20s} | Created: {created_at}")

print("\n" + "=" * 80)
print("FEEDBACK STATS")
print("=" * 80)

cursor.execute("""
    SELECT plan_type, AVG(rating) as avg_rating, COUNT(*) as count
    FROM feedback
    GROUP BY plan_type
""")

feedback_rows = cursor.fetchall()
if feedback_rows:
    for row in feedback_rows:
        print(f"{row[0]}: {row[1]:.2f} stars ({row[2]} ratings)")
else:
    print("No feedback yet")

print("\n" + "=" * 80)
print("SAMPLE PLAN DATA")
print("=" * 80)

cursor.execute("""
    SELECT profile_json, plan_json
    FROM plans
    ORDER BY created_at DESC
    LIMIT 1
""")

result = cursor.fetchone()
if result:
    profile = json.loads(result[0])
    plan = json.loads(result[1])

    print(f"Business Name: {profile.get('business_name')}")
    print(f"Business Type: {profile.get('business_type')}")
    print(f"Location: {profile.get('zip_code', profile.get('location'))}")
    print(f"Budget: ${profile.get('monthly_budget'):,.0f}")
    print(f"Goal: {profile.get('goal')[:100]}...")

    if 'persona' in plan:
        print(f"\nPersona: {plan['persona'].get('name')}")

    if 'critic_evaluation' in plan:
        print(f"Critic Score: {plan['critic_evaluation'].get('overall_score', 'N/A')}")
else:
    print("No plans found")

conn.close()

print("\n" + "=" * 80)
print("To explore further, run: sqlite3 ad_planner.db")
print("=" * 80)
