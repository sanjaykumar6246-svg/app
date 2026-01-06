"""Generate sample data queries for the Asana simulation database."""

SAMPLE_QUERIES = """
# Asana Simulation Database - Sample Queries

## Basic Statistics

### 1. Count all entities
```sql
SELECT 
    (SELECT COUNT(*) FROM organizations) as organizations,
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM teams) as teams,
    (SELECT COUNT(*) FROM projects) as projects,
    (SELECT COUNT(*) FROM tasks) as tasks,
    (SELECT COUNT(*) FROM comments) as comments;
```

### 2. Overall task completion rate
```sql
SELECT 
    COUNT(*) as total_tasks,
    SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_tasks,
    ROUND(100.0 * SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as completion_percentage
FROM tasks;
```

### 3. Average team size
```sql
SELECT 
    t.name as team,
    COUNT(tm.user_id) as members
FROM teams t
LEFT JOIN team_memberships tm ON t.team_id = tm.team_id
GROUP BY t.team_id, t.name
ORDER BY members DESC;
```

## Project Analysis

### 4. Projects by status
```sql
SELECT 
    status,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage
FROM projects
GROUP BY status;
```

### 5. Tasks per project
```sql
SELECT 
    p.name as project,
    p.project_type,
    COUNT(t.task_id) as task_count,
    SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) as completed,
    ROUND(100.0 * SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) / COUNT(t.task_id), 1) as completion_rate
FROM projects p
LEFT JOIN tasks t ON p.project_id = t.project_id
GROUP BY p.project_id, p.name, p.project_type
ORDER BY task_count DESC
LIMIT 10;
```

### 6. Completion rate by project type
```sql
SELECT 
    p.project_type,
    COUNT(t.task_id) as total_tasks,
    SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) as completed_tasks,
    ROUND(100.0 * SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) / COUNT(t.task_id), 2) as completion_rate
FROM projects p
JOIN tasks t ON p.project_id = t.project_id
GROUP BY p.project_type
ORDER BY completion_rate DESC;
```

## Task Analysis

### 7. Overdue tasks
```sql
SELECT 
    t.name as task,
    t.due_date,
    DATE('now') - t.due_date as days_overdue,
    u.name as assignee,
    p.name as project
FROM tasks t
LEFT JOIN users u ON t.assignee_id = u.user_id
JOIN projects p ON t.project_id = p.project_id
WHERE t.completed = 0 
  AND t.due_date < DATE('now')
ORDER BY days_overdue DESC
LIMIT 20;
```

### 8. Unassigned tasks
```sql
SELECT 
    t.name as task,
    p.name as project,
    p.project_type,
    t.created_at,
    t.priority
FROM tasks t
JOIN projects p ON t.project_id = p.project_id
WHERE t.assignee_id IS NULL
ORDER BY t.created_at DESC
LIMIT 20;
```

### 9. Tasks by priority
```sql
SELECT 
    COALESCE(priority, 'none') as priority,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage
FROM tasks
GROUP BY priority
ORDER BY count DESC;
```

### 10. Average cycle time (creation to completion)
```sql
SELECT 
    ROUND(AVG(JULIANDAY(completed_at) - JULIANDAY(created_at)), 2) as avg_days_to_complete,
    MIN(JULIANDAY(completed_at) - JULIANDAY(created_at)) as min_days,
    MAX(JULIANDAY(completed_at) - JULIANDAY(created_at)) as max_days
FROM tasks
WHERE completed = 1 AND completed_at IS NOT NULL;
```

## User & Team Analysis

### 11. User workload (tasks assigned)
```sql
SELECT 
    u.name,
    u.role,
    u.department,
    COUNT(t.task_id) as assigned_tasks,
    SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) as completed_tasks,
    COUNT(t.task_id) - SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) as open_tasks
FROM users u
LEFT JOIN tasks t ON u.user_id = t.assignee_id
GROUP BY u.user_id, u.name, u.role, u.department
HAVING assigned_tasks > 0
ORDER BY assigned_tasks DESC
LIMIT 20;
```

### 12. Team workload distribution
```sql
SELECT 
    tm.name as team,
    COUNT(DISTINCT u.user_id) as team_members,
    COUNT(DISTINCT p.project_id) as projects,
    COUNT(DISTINCT t.task_id) as total_tasks,
    ROUND(COUNT(DISTINCT t.task_id) * 1.0 / COUNT(DISTINCT u.user_id), 2) as tasks_per_member
FROM teams tm
JOIN team_memberships tmb ON tm.team_id = tmb.team_id
JOIN users u ON tmb.user_id = u.user_id
JOIN projects p ON tm.team_id = p.team_id
LEFT JOIN tasks t ON p.project_id = t.project_id
GROUP BY tm.team_id, tm.name
ORDER BY total_tasks DESC;
```

### 13. Most active commenters
```sql
SELECT 
    u.name,
    u.role,
    COUNT(c.comment_id) as comments_made,
    COUNT(DISTINCT c.task_id) as tasks_commented_on
FROM users u
JOIN comments c ON u.user_id = c.user_id
GROUP BY u.user_id, u.name, u.role
ORDER BY comments_made DESC
LIMIT 10;
```

## Collaboration Metrics

### 14. Tasks with most comments
```sql
SELECT 
    t.name as task,
    p.name as project,
    COUNT(c.comment_id) as comment_count,
    t.completed
FROM tasks t
JOIN projects p ON t.project_id = p.project_id
LEFT JOIN comments c ON t.task_id = c.task_id
GROUP BY t.task_id, t.name, p.name, t.completed
ORDER BY comment_count DESC
LIMIT 10;
```

### 15. Tag usage frequency
```sql
SELECT 
    tg.name as tag,
    COUNT(tt.task_tag_id) as usage_count
FROM tags tg
LEFT JOIN task_tags tt ON tg.tag_id = tt.tag_id
GROUP BY tg.tag_id, tg.name
ORDER BY usage_count DESC;
```

### 16. Most used custom fields
```sql
SELECT 
    cfd.name as field_name,
    cfd.field_type,
    p.name as project,
    COUNT(cfv.value_id) as times_used
FROM custom_field_definitions cfd
JOIN projects p ON cfd.project_id = p.project_id
LEFT JOIN custom_field_values cfv ON cfd.field_id = cfv.field_id
GROUP BY cfd.field_id, cfd.name, cfd.field_type, p.name
ORDER BY times_used DESC
LIMIT 20;
```

## Time-Based Analysis

### 17. Task creation over time (by month)
```sql
SELECT 
    STRFTIME('%Y-%m', created_at) as month,
    COUNT(*) as tasks_created
FROM tasks
GROUP BY month
ORDER BY month;
```

### 18. Completion rate by weekday
```sql
SELECT 
    CASE CAST(STRFTIME('%w', completed_at) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as weekday,
    COUNT(*) as completions
FROM tasks
WHERE completed = 1
GROUP BY STRFTIME('%w', completed_at)
ORDER BY CAST(STRFTIME('%w', completed_at) AS INTEGER);
```

### 19. Tasks by section distribution
```sql
SELECT 
    s.name as section,
    p.project_type,
    COUNT(t.task_id) as task_count
FROM sections s
JOIN projects p ON s.project_id = p.project_id
LEFT JOIN tasks t ON s.section_id = t.section_id
GROUP BY s.section_id, s.name, p.project_type
ORDER BY task_count DESC
LIMIT 20;
```

## Advanced Queries

### 20. Projects at risk (low completion rate, many overdue tasks)
```sql
SELECT 
    p.name as project,
    p.project_type,
    COUNT(t.task_id) as total_tasks,
    SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN t.due_date < DATE('now') AND t.completed = 0 THEN 1 ELSE 0 END) as overdue,
    ROUND(100.0 * SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) / COUNT(t.task_id), 1) as completion_rate
FROM projects p
LEFT JOIN tasks t ON p.project_id = t.project_id
GROUP BY p.project_id, p.name, p.project_type
HAVING total_tasks > 10
ORDER BY completion_rate ASC, overdue DESC
LIMIT 10;
```

### 21. Cross-team collaboration (users commenting on other teams' projects)
```sql
SELECT 
    u.name as user,
    u.department as user_dept,
    tm.name as project_team,
    COUNT(DISTINCT c.comment_id) as comments
FROM comments c
JOIN users u ON c.user_id = u.user_id
JOIN tasks t ON c.task_id = t.task_id
JOIN projects p ON t.project_id = p.project_id
JOIN teams tm ON p.team_id = tm.team_id
WHERE u.department != tm.team_type
GROUP BY u.user_id, u.name, u.department, tm.name
ORDER BY comments DESC
LIMIT 10;
```

### 22. Attachment patterns by project type
```sql
SELECT 
    p.project_type,
    a.file_type,
    COUNT(*) as attachment_count,
    ROUND(AVG(a.size_bytes) / 1024.0, 2) as avg_size_kb
FROM attachments a
JOIN tasks t ON a.task_id = t.task_id
JOIN projects p ON t.project_id = p.project_id
GROUP BY p.project_type, a.file_type
ORDER BY p.project_type, attachment_count DESC;
```

---

## Running These Queries

Save any query to a file (e.g., `query.sql`) and run:

```bash
# Using Python
python -c "import sqlite3; conn = sqlite3.connect('output/asana_simulation.sqlite'); 
cursor = conn.cursor(); cursor.execute(open('query.sql').read()); 
for row in cursor.fetchall(): print(row)"

# Or create a helper script
python run_query.py query.sql
```

## Query Performance Tips

1. **Indexes are already created** on all foreign keys
2. **Use EXPLAIN QUERY PLAN** to analyze slow queries
3. **Filter early** in WHERE clauses before JOINs when possible
4. **Limit results** for exploratory analysis
5. **Aggregate** at the database level rather than in application code
"""

if __name__ == '__main__':
    print(SAMPLE_QUERIES)
