from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

class Organization(BaseModel):
    org_id: str
    name: str
    domain: str
    is_organization: bool = True
    created_at: datetime
    num_employees: int

class User(BaseModel):
    user_id: str
    org_id: str
    email: str
    name: str
    role: str
    department: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime
    is_active: bool = True

class Team(BaseModel):
    team_id: str
    org_id: str
    name: str
    description: Optional[str] = None
    team_type: str
    created_at: datetime

class TeamMembership(BaseModel):
    membership_id: str
    team_id: str
    user_id: str
    role: str = 'member'
    joined_at: datetime

class Project(BaseModel):
    project_id: str
    team_id: str
    name: str
    description: Optional[str] = None
    project_type: str
    owner_id: Optional[str] = None
    status: str = 'active'
    privacy: str = 'team'
    created_at: datetime
    due_date: Optional[date] = None
    archived: bool = False
    color: Optional[str] = None

class Section(BaseModel):
    section_id: str
    project_id: str
    name: str
    position: int
    created_at: datetime

class Task(BaseModel):
    task_id: str
    project_id: str
    section_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    created_by: str
    created_at: datetime
    modified_at: datetime
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    completed_by: Optional[str] = None
    priority: Optional[str] = None
    num_hearts: int = 0
    num_subtasks: int = 0
    num_subtasks_completed: int = 0

class Comment(BaseModel):
    comment_id: str
    task_id: str
    user_id: str
    text: str
    comment_type: str = 'comment'
    created_at: datetime

class CustomFieldDefinition(BaseModel):
    field_id: str
    project_id: str
    name: str
    field_type: str
    description: Optional[str] = None
    enum_options: Optional[str] = None
    precision: Optional[int] = None
    created_at: datetime

class CustomFieldValue(BaseModel):
    value_id: str
    task_id: str
    field_id: str
    value: str
    created_at: datetime

class Tag(BaseModel):
    tag_id: str
    org_id: str
    name: str
    color: Optional[str] = None
    created_at: datetime

class TaskTag(BaseModel):
    task_tag_id: str
    task_id: str
    tag_id: str
    created_at: datetime

class Attachment(BaseModel):
    attachment_id: str
    task_id: str
    name: str
    file_type: str
    size_bytes: int
    uploaded_by: str
    uploaded_at: datetime
    download_url: Optional[str] = None
