"""Validate the generated Asana simulation database."""
import sqlite3
import sys
from pathlib import Path

def validate_database(db_path='output/asana_simulation.sqlite'):
    """Run validation checks on the generated database."""
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("ASANA SIMULATION DATABASE VALIDATION")
    print("=" * 60)
    
    # Check table counts
    print("\n📊 Table Record Counts:")
    tables = [
        'organizations', 'users', 'teams', 'team_memberships',
        'projects', 'sections', 'tasks', 'comments',
        'custom_field_definitions', 'custom_field_values',
        'tags', 'task_tags', 'attachments'
    ]
    
    counts = {}
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        counts[table] = count
        print(f"  {table:.<30} {count:>6} records")
    
    # Validation checks
    print("\n✅ Data Quality Checks:")
    
    issues = []
    
    # Check 1: All users belong to organization
    cursor.execute("""
        SELECT COUNT(*) FROM users u 
        WHERE NOT EXISTS (SELECT 1 FROM organizations o WHERE o.org_id = u.org_id)
    """)
    orphan_users = cursor.fetchone()[0]
    if orphan_users > 0:
        issues.append(f"Found {orphan_users} users without valid organization")
    else:
        print("  ✓ All users belong to valid organization")
    
    # Check 2: Tasks created after projects
    cursor.execute("""
        SELECT COUNT(*) FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE t.created_at < p.created_at
    """)
    invalid_task_dates = cursor.fetchone()[0]
    if invalid_task_dates > 0:
        issues.append(f"Found {invalid_task_dates} tasks created before their projects")
    else:
        print("  ✓ All tasks created after their projects")
    
    # Check 3: Completed tasks have completion dates
    cursor.execute("""
        SELECT COUNT(*) FROM tasks
        WHERE completed = 1 AND completed_at IS NULL
    """)
    missing_completion = cursor.fetchone()[0]
    if missing_completion > 0:
        issues.append(f"Found {missing_completion} completed tasks missing completion dates")
    else:
        print("  ✓ All completed tasks have completion dates")
    
    # Check 4: Completion dates after creation dates
    cursor.execute("""
        SELECT COUNT(*) FROM tasks
        WHERE completed = 1 AND completed_at <= created_at
    """)
    invalid_completions = cursor.fetchone()[0]
    if invalid_completions > 0:
        issues.append(f"Found {invalid_completions} tasks completed before creation")
    else:
        print("  ✓ All completions after task creation")
    
    # Check 5: Custom field values reference valid fields
    cursor.execute("""
        SELECT COUNT(*) FROM custom_field_values v
        WHERE NOT EXISTS (
            SELECT 1 FROM custom_field_definitions d 
            WHERE d.field_id = v.field_id
        )
    """)
    orphan_values = cursor.fetchone()[0]
    if orphan_values > 0:
        issues.append(f"Found {orphan_values} custom field values without definitions")
    else:
        print("  ✓ All custom field values have valid definitions")
    
    # Check 6: Team memberships reference valid teams and users
    cursor.execute("""
        SELECT COUNT(*) FROM team_memberships m
        WHERE NOT EXISTS (SELECT 1 FROM teams t WHERE t.team_id = m.team_id)
           OR NOT EXISTS (SELECT 1 FROM users u WHERE u.user_id = m.user_id)
    """)
    invalid_memberships = cursor.fetchone()[0]
    if invalid_memberships > 0:
        issues.append(f"Found {invalid_memberships} invalid team memberships")
    else:
        print("  ✓ All team memberships are valid")
    
    # Statistics
    print("\n📈 Data Statistics:")
    
    # Completion rate
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1")
    completed = cursor.fetchone()[0]
    if counts['tasks'] > 0:
        completion_rate = (completed / counts['tasks']) * 100
        print(f"  Task completion rate: {completion_rate:.1f}%")
    
    # Average tasks per project
    if counts['projects'] > 0:
        avg_tasks = counts['tasks'] / counts['projects']
        print(f"  Average tasks per project: {avg_tasks:.1f}")
    
    # Average team members
    if counts['teams'] > 0:
        avg_members = counts['team_memberships'] / counts['teams']
        print(f"  Average members per team: {avg_members:.1f}")
    
    # Comments per task
    if counts['tasks'] > 0:
        avg_comments = counts['comments'] / counts['tasks']
        print(f"  Average comments per task: {avg_comments:.1f}")
    
    # Sample data
    print("\n📝 Sample Records:")
    
    # Sample project
    cursor.execute("SELECT name, project_type FROM projects LIMIT 1")
    project = cursor.fetchone()
    if project:
        print(f"  Sample project: {project[0]} (type: {project[1]})")
    
    # Sample task
    cursor.execute("SELECT name, completed, priority FROM tasks LIMIT 1")
    task = cursor.fetchone()
    if task:
        status = "✓ completed" if task[1] else "○ open"
        priority = task[2] or "normal"
        print(f"  Sample task: {task[0]} ({status}, priority: {priority})")
    
    # Sample user
    cursor.execute("SELECT name, role, department FROM users LIMIT 1")
    user = cursor.fetchone()
    if user:
        print(f"  Sample user: {user[0]} - {user[1]} ({user[2]})")
    
    conn.close()
    
    # Summary
    print("\n" + "=" * 60)
    if issues:
        print("❌ VALIDATION FAILED")
        print("\nIssues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ VALIDATION PASSED")
        print("\nDatabase is ready for use!")
        return True
    print("=" * 60)

if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'output/asana_simulation.sqlite'
    success = validate_database(db_path)
    sys.exit(0 if success else 1)
