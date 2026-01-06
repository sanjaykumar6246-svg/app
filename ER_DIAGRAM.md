# ER Diagram for Asana Simulation Database

This file contains a detailed Entity-Relationship diagram description.

## ASCII ER Diagram

```
┌─────────────────┐
│  organizations  │
│  (Workspaces)   │
└────────┬────────┘
         │
         ├──── 1:N ────┐
         │            │
         │       ┌────▼────┐
         │       │  users  │
         │       └────┬────┘
         │            │
         │            │ M:N
         │            │
    ┌────▼────┐  ┌───▼────────────┐
    │  teams  ├──┤ team_members │
    └────┬────┘  └────────────────┘
         │
         │ 1:N
         │
    ┌────▼────────┐
    │  projects   │
    └────┬────────┘
         │
         ├──── 1:N ───┬───────────────────┬────────────────┐
         │            │                   │                │
    ┌────▼────┐  ┌────▼──────────────┐  ┌──▼───┐      ┌────▼──────────────┐
    │sections │  │ custom_field_   │  │ tags │      │   attachments   │
    └────┬────┘  │  definitions    │  └──┬───┘      └─────────────────┘
         │       └────┬────────────┘     │
         │            │                  │
         │ 1:N        │ 1:N              │ M:N
         │            │                  │
    ┌────▼────────────▼──────────────────▼──┐
    │            tasks                      │
    │  (self-referencing for subtasks)      │
    └────┬──────────────┬───────────────────┘
         │              │
         │ 1:N          │ 1:N
         │              │
    ┌────▼────┐    ┌────▼─────────────────┐
    │comments │    │ custom_field_     │
    └─────────┘    │   values          │
                   └───────────────────────┘
```

## Core Relationships

### 1. Organization → Users (1:N)
- One organization has many users
- FK: users.org_id → organizations.org_id

### 2. Organization → Teams (1:N)
- One organization has many teams
- FK: teams.org_id → organizations.org_id

### 3. Users ↔ Teams (M:N via team_memberships)
- Many users belong to many teams
- Junction table: team_memberships
- FKs: team_memberships.user_id → users.user_id
       team_memberships.team_id → teams.team_id

### 4. Teams → Projects (1:N)
- One team has many projects
- FK: projects.team_id → teams.team_id

### 5. Projects → Sections (1:N)
- One project has many sections
- FK: sections.project_id → projects.project_id

### 6. Projects → Tasks (1:N)
- One project has many tasks
- FK: tasks.project_id → projects.project_id

### 7. Sections → Tasks (1:N)
- One section contains many tasks
- FK: tasks.section_id → sections.section_id

### 8. Tasks → Tasks (Self-referencing)
- Tasks can have subtasks
- FK: tasks.parent_task_id → tasks.task_id
- NULL parent_task_id = top-level task

### 9. Tasks → Comments (1:N)
- One task has many comments
- FK: comments.task_id → tasks.task_id

### 10. Projects → Custom Field Definitions (1:N)
- Projects define custom fields
- FK: custom_field_definitions.project_id → projects.project_id

### 11. Tasks → Custom Field Values (1:N)
- Tasks have custom field values
- FK: custom_field_values.task_id → tasks.task_id
       custom_field_values.field_id → custom_field_definitions.field_id

### 12. Tags ↔ Tasks (M:N via task_tags)
- Many tags can be on many tasks
- Junction table: task_tags
- FKs: task_tags.task_id → tasks.task_id
       task_tags.tag_id → tags.tag_id

### 13. Tasks → Attachments (1:N)
- One task can have many attachments
- FK: attachments.task_id → tasks.task_id

## Cardinality Summary

| Relationship | Type | Description |
|-------------|------|-------------|
| Organization → Users | 1:N | One org, many users |
| Organization → Teams | 1:N | One org, many teams |
| Organization → Tags | 1:N | One org, many tags |
| Teams ↔ Users | M:N | Users can be in multiple teams |
| Teams → Projects | 1:N | One team, many projects |
| Projects → Sections | 1:N | One project, many sections |
| Projects → Custom Fields | 1:N | Projects define custom fields |
| Projects → Tasks | 1:N | One project, many tasks |
| Sections → Tasks | 1:N | One section, many tasks |
| Tasks → Tasks | 1:N | Parent-child (subtasks) |
| Tasks → Comments | 1:N | One task, many comments |
| Tasks → Custom Values | 1:N | Tasks have field values |
| Tasks ↔ Tags | M:N | Tasks can have multiple tags |
| Tasks → Attachments | 1:N | One task, many attachments |
| Users → Tasks (assignee) | 1:N | One user, many assigned tasks |
| Users → Tasks (creator) | 1:N | One user, many created tasks |
| Users → Comments | 1:N | One user, many comments |

## Key Constraints

### Primary Keys
All tables use UUID-based TEXT primary keys:
- `*_id` columns (e.g., user_id, task_id, project_id)

### Foreign Keys
All relationships enforced with foreign key constraints:
- ON DELETE CASCADE for most relationships
- Ensures referential integrity

### Unique Constraints
1. `organizations.domain` - One domain per organization
2. `users.email` - Unique email addresses
3. `team_memberships(team_id, user_id)` - User can't join same team twice
4. `tags(org_id, name)` - Tag names unique within organization
5. `custom_field_values(task_id, field_id)` - One value per field per task
6. `task_tags(task_id, tag_id)` - Task can't have same tag twice

## Indexes

Performance indexes on all foreign keys:
- `idx_users_org` on users(org_id)
- `idx_teams_org` on teams(org_id)
- `idx_team_memberships_team` on team_memberships(team_id)
- `idx_team_memberships_user` on team_memberships(user_id)
- `idx_projects_team` on projects(team_id)
- `idx_sections_project` on sections(project_id)
- `idx_tasks_project` on tasks(project_id)
- `idx_tasks_section` on tasks(section_id)
- `idx_tasks_assignee` on tasks(assignee_id)
- `idx_tasks_parent` on tasks(parent_task_id)
- `idx_comments_task` on comments(task_id)
- `idx_custom_fields_project` on custom_field_definitions(project_id)
- `idx_custom_values_task` on custom_field_values(task_id)
- `idx_task_tags_task` on task_tags(task_id)
- `idx_task_tags_tag` on task_tags(tag_id)
- `idx_attachments_task` on attachments(task_id)

## Data Flow

1. **Setup Phase**
   - Organization created
   - Users created and added to organization
   - Teams created within organization
   - Users assigned to teams (team_memberships)

2. **Project Phase**
   - Projects created for teams
   - Sections added to projects
   - Custom fields defined for projects
   - Tags created at org level

3. **Work Phase**
   - Tasks created in projects/sections
   - Tasks assigned to users
   - Custom field values set on tasks
   - Tags applied to tasks
   - Comments added to tasks
   - Attachments uploaded to tasks

4. **Completion Phase**
   - Tasks marked as completed
   - Completion timestamps recorded
   - Projects may be archived

---

For detailed column descriptions and methodology, see DOCUMENTATION.md
