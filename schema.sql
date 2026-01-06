-- Asana Simulation Database Schema
-- Designed for realistic enterprise project management data

-- Organizations/Workspaces
CREATE TABLE IF NOT EXISTS organizations (
    org_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT NOT NULL UNIQUE,
    is_organization BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL,
    num_employees INTEGER NOT NULL
);

-- Users
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    department TEXT,
    photo_url TEXT,
    created_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);

-- Teams
CREATE TABLE IF NOT EXISTS teams (
    team_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    team_type TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);

-- Team Memberships
CREATE TABLE IF NOT EXISTS team_memberships (
    membership_id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT DEFAULT 'member',
    joined_at TIMESTAMP NOT NULL,
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE(team_id, user_id)
);

-- Projects
CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    project_type TEXT NOT NULL,
    owner_id TEXT,
    status TEXT DEFAULT 'active',
    privacy TEXT DEFAULT 'team',
    created_at TIMESTAMP NOT NULL,
    due_date DATE,
    archived BOOLEAN DEFAULT FALSE,
    color TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (owner_id) REFERENCES users(user_id)
);

-- Sections
CREATE TABLE IF NOT EXISTS sections (
    section_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    position INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- Tasks
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    section_id TEXT,
    parent_task_id TEXT,
    name TEXT NOT NULL,
    description TEXT,
    assignee_id TEXT,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    modified_at TIMESTAMP NOT NULL,
    due_date DATE,
    start_date DATE,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    completed_by TEXT,
    priority TEXT,
    num_hearts INTEGER DEFAULT 0,
    num_subtasks INTEGER DEFAULT 0,
    num_subtasks_completed INTEGER DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (section_id) REFERENCES sections(section_id),
    FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (assignee_id) REFERENCES users(user_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (completed_by) REFERENCES users(user_id)
);

-- Comments/Stories
CREATE TABLE IF NOT EXISTS comments (
    comment_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    text TEXT NOT NULL,
    comment_type TEXT DEFAULT 'comment',
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Custom Field Definitions
CREATE TABLE IF NOT EXISTS custom_field_definitions (
    field_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    field_type TEXT NOT NULL,
    description TEXT,
    enum_options TEXT,
    precision INTEGER,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- Custom Field Values
CREATE TABLE IF NOT EXISTS custom_field_values (
    value_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    field_id TEXT NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (field_id) REFERENCES custom_field_definitions(field_id),
    UNIQUE(task_id, field_id)
);

-- Tags
CREATE TABLE IF NOT EXISTS tags (
    tag_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    name TEXT NOT NULL,
    color TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id),
    UNIQUE(org_id, name)
);

-- Task-Tag Associations
CREATE TABLE IF NOT EXISTS task_tags (
    task_tag_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id),
    UNIQUE(task_id, tag_id)
);

-- Attachments (metadata only)
CREATE TABLE IF NOT EXISTS attachments (
    attachment_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    uploaded_by TEXT NOT NULL,
    uploaded_at TIMESTAMP NOT NULL,
    download_url TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (uploaded_by) REFERENCES users(user_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_org ON users(org_id);
CREATE INDEX IF NOT EXISTS idx_teams_org ON teams(org_id);
CREATE INDEX IF NOT EXISTS idx_team_memberships_team ON team_memberships(team_id);
CREATE INDEX IF NOT EXISTS idx_team_memberships_user ON team_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_team ON projects(team_id);
CREATE INDEX IF NOT EXISTS idx_sections_project ON sections(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_section ON tasks(section_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_comments_task ON comments(task_id);
CREATE INDEX IF NOT EXISTS idx_custom_fields_project ON custom_field_definitions(project_id);
CREATE INDEX IF NOT EXISTS idx_custom_values_task ON custom_field_values(task_id);
CREATE INDEX IF NOT EXISTS idx_task_tags_task ON task_tags(task_id);
CREATE INDEX IF NOT EXISTS idx_task_tags_tag ON task_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_attachments_task ON attachments(task_id);
