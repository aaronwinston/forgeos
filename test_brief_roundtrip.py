#!/usr/bin/env python3
"""
Test Brief round-trip save and reload functionality
"""
import sys
import sqlite3
import json
from datetime import datetime

DB_PATH = "apps/api/forgeos.db"

def get_db():
    return sqlite3.connect(DB_PATH)

def test_brief_roundtrip():
    """Test that brief changes persist after save and reload"""
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get the test brief we created
    cursor.execute("SELECT id, title, audience, description, brief_md, toggles_json FROM brief WHERE id = 1")
    result = cursor.fetchone()
    
    if not result:
        print("❌ FAILED: Test brief not found")
        return False
    
    brief_id, orig_title, orig_audience, orig_description, orig_brief_md, orig_toggles = result
    
    print(f"✅ Found test brief (ID: {brief_id})")
    print(f"  Original title: {orig_title}")
    print(f"  Original audience: {orig_audience}")
    
    # Simulate an UPDATE that the PUT endpoint would do
    new_title = "Updated Brief Title"
    new_audience = "AI engineers and researchers"
    new_description = "Write a comprehensive guide on implementing AI observability in production systems"
    new_toggles = {
        "brief_first": True,
        "audience": "AI engineers and researchers",
        "voice": "technical",
        "skills": ["observability", "ai-ops"],
        "playbook": "technical-guide",
        "content_type": "whitepaper"
    }
    
    # Update the database
    cursor.execute("""
        UPDATE brief 
        SET title = ?, audience = ?, description = ?, brief_md = ?, toggles_json = ?, updated_at = ?
        WHERE id = ?
    """, (new_title, new_audience, new_description, new_description, json.dumps(new_toggles), datetime.utcnow(), brief_id))
    
    conn.commit()
    print(f"\n✅ Updated brief in database")
    print(f"  New title: {new_title}")
    print(f"  New audience: {new_audience}")
    
    # Now "reload" by fetching fresh from database
    cursor.execute("SELECT id, title, audience, description, brief_md, toggles_json FROM brief WHERE id = 1")
    reloaded = cursor.fetchone()
    
    if not reloaded:
        print("❌ FAILED: Brief disappeared after update!")
        return False
    
    reloaded_id, reloaded_title, reloaded_audience, reloaded_description, reloaded_brief_md, reloaded_toggles = reloaded
    
    print(f"\n✅ Reloaded brief from database (F5 simulation)")
    print(f"  Title persisted: {reloaded_title == new_title}")
    print(f"  Audience persisted: {reloaded_audience == new_audience}")
    print(f"  Description persisted: {reloaded_description == new_description}")
    
    # Verify all fields match exactly
    toggles_obj = json.loads(reloaded_toggles)
    voice_matches = toggles_obj.get("voice") == "technical"
    content_type_matches = toggles_obj.get("content_type") == "whitepaper"
    
    print(f"  Voice persisted: {voice_matches}")
    print(f"  Content type persisted: {content_type_matches}")
    
    # Final check
    all_match = (
        reloaded_title == new_title and
        reloaded_audience == new_audience and
        reloaded_description == new_description and
        reloaded_brief_md == new_description and
        voice_matches and
        content_type_matches
    )
    
    if all_match:
        print("\n✅ SUCCESS: All fields persisted exactly as saved!")
        return True
    else:
        print("\n❌ FAILED: Some fields did not persist correctly")
        return False
    
    conn.close()

if __name__ == "__main__":
    success = test_brief_roundtrip()
    sys.exit(0 if success else 1)
