#!/usr/bin/env python3
"""Index verification helper.

This file is useful for manual EXPLAIN QUERY PLAN checks, but it's not a unit
test suite.
"""

import pytest

pytestmark = pytest.mark.integration

pytest.skip("manual index verification script", allow_module_level=True)

import sqlite3
from pathlib import Path
from typing import List, Tuple


def get_db_path() -> Path:
    """Get the database path."""
    return Path(__file__).parent / "forgeos.db"


def run_explain_query(conn: sqlite3.Connection, query: str, params: tuple = ()) -> List[str]:
    """Run EXPLAIN QUERY PLAN and return the plan lines."""
    cursor = conn.cursor()
    cursor.execute(f"EXPLAIN QUERY PLAN {query}", params)
    results = cursor.fetchall()
    cursor.close()
    return [row[3] for row in results]  # Column 3 contains the detail


def check_index_used(plan_lines: List[str], expected_index: str) -> bool:
    """Check if a specific index is mentioned in the query plan."""
    plan_text = " ".join(plan_lines).upper()
    return expected_index.upper() in plan_text


def test_query(
    conn: sqlite3.Connection,
    name: str,
    query: str,
    expected_index: str,
    params: tuple = ()
) -> Tuple[bool, str]:
    """Test a single query and check if expected index is used."""
    try:
        plan = run_explain_query(conn, query, params)
        plan_str = "\n    ".join(plan)
        
        if check_index_used(plan, expected_index):
            return True, plan_str
        else:
            return False, f"Index '{expected_index}' NOT FOUND in plan:\n    {plan_str}"
    except Exception as e:
        return False, f"ERROR: {str(e)}"


def main():
    """Run all index tests."""
    db_path = get_db_path()
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return 1
    
    conn = sqlite3.connect(str(db_path))
    
    print("=" * 80)
    print("DATABASE INDEX VERIFICATION TEST")
    print("=" * 80)
    print()
    
    # Test cases: (name, query, expected_index, params)
    tests = [
        (
            "PipelineRun - deleted filter + sort",
            "SELECT * FROM pipelinerun WHERE organization_id = ? AND deleted = 0 ORDER BY created_at DESC",
            "idx_pipelinerun_org_deleted_created",
            ("test-org",)
        ),
        (
            "PipelineRun - status filter",
            "SELECT * FROM pipelinerun WHERE organization_id = ? AND status = 'active'",
            "idx_pipelinerun_org_status",
            ("test-org",)
        ),
        (
            "CalendarEvent - status filter",
            "SELECT * FROM calendarevent WHERE organization_id = ? AND status != 'cancelled'",
            "idx_calendarevent_org_status",
            ("test-org",)
        ),
        (
            "CalendarEvent - sync status",
            "SELECT * FROM calendarevent WHERE organization_id = ? AND sync_status = 'offline'",
            "idx_calendarevent_org_sync_status",
            ("test-org",)
        ),
        (
            "CalendarEvent - project filter",
            "SELECT * FROM calendarevent WHERE organization_id = ? AND project_id = 1",
            "idx_calendarevent_org_project",
            ("test-org",)
        ),
        (
            "Deliverable - status filter + sort",
            "SELECT * FROM deliverable WHERE organization_id = ? AND status = 'active' ORDER BY created_at DESC",
            "idx_deliverable_org_status_created",
            ("test-org",)
        ),
        (
            "Brief - user filter + sort",
            "SELECT * FROM brief WHERE organization_id = ? AND user_id = ? ORDER BY created_at DESC",
            "idx_brief_org_user_created",
            ("test-org", "user-123")
        ),
        (
            "Project - status filter",
            "SELECT * FROM project WHERE organization_id = ? AND status = 'active'",
            "idx_project_org_status",
            ("test-org",)
        ),
        (
            "ScrapeItem - score + created sort",
            "SELECT * FROM scrapeitem WHERE organization_id = ? ORDER BY score DESC, created_at DESC",
            "idx_scrape_org_score_created",
            ("test-org",)
        ),
        (
            "ScrapeItem - dismissed filter",
            "SELECT * FROM scrapeitem WHERE organization_id = ? AND dismissed_at IS NULL",
            "idx_scrape_org_dismissed",
            ("test-org",)
        ),
        (
            "ChatMessage - session + role",
            "SELECT * FROM chatmessage WHERE organization_id = ? AND session_id = 1 AND role = 'assistant'",
            "idx_chatmessage_org_session_role",
            ("test-org",)
        ),
        (
            "UsageEvent - user + time",
            "SELECT * FROM usageevent WHERE organization_id = ? AND user_id = ? ORDER BY occurred_at DESC",
            "idx_usageevent_org_user_time",
            ("test-org", "user-123")
        ),
        (
            "UsageEvent - event type",
            "SELECT * FROM usageevent WHERE organization_id = ? AND event_type = 'chat_message' ORDER BY occurred_at DESC",
            "idx_usageevent_org_type_time",
            ("test-org",)
        ),
        (
            "AuditEvent - user filter",
            "SELECT * FROM auditevent WHERE organization_id = ? AND user_id = ? ORDER BY created_at DESC",
            "idx_auditevent_org_user_time",
            ("test-org", "user-123")
        ),
        (
            "RuntimeCredential - validity check",
            "SELECT * FROM runtimecredential WHERE organization_id = ? AND user_id = ? AND is_valid = 1",
            "idx_runtimecredential_org_user_valid",
            ("test-org", "user-123")
        ),
        (
            "DoctrineVersion - user history",
            "SELECT * FROM doctrineversion WHERE organization_id = ? AND saved_by_user_id = ? ORDER BY created_at DESC",
            "idx_doctrine_org_user_time",
            ("test-org", "user-123")
        ),
    ]
    
    passed = 0
    failed = 0
    
    for name, query, expected_index, params in tests:
        success, result = test_query(conn, name, query, expected_index, params)
        
        if success:
            print(f"✅ PASS: {name}")
            print(f"   Index: {expected_index}")
            print(f"   Plan:  {result}")
            print()
            passed += 1
        else:
            print(f"❌ FAIL: {name}")
            print(f"   Expected: {expected_index}")
            print(f"   {result}")
            print()
            failed += 1
    
    conn.close()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 80)
    
    if failed > 0:
        print("\n⚠️  Some indexes are not being used as expected.")
        print("This may indicate missing indexes or query patterns that need optimization.")
        return 1
    else:
        print("\n✅ All indexes are working correctly!")
        return 0


if __name__ == "__main__":
    exit(main())
