"""Task, comment, and related data generators."""
import sqlite3
from typing import List, Dict, Optional
import random
import asyncio

from src.models import Task, Comment, CustomFieldDefinition, CustomFieldValue, Tag, TaskTag, Attachment, User, Project, Section
from src.utils.helpers import generate_id, random_color, weighted_choice
from src.utils.date_helper import DateHelper
from src.utils.llm_helper import LLMHelper

class TaskGenerator:
    """Generate realistic task data."""
    
    def __init__(self, date_helper: DateHelper, llm_helper: LLMHelper):
        self.date_helper = date_helper
        self.llm_helper = llm_helper
    
    async def generate_tasks(
        self, 
        projects: List[Project], 
        sections: List[Section],
        users: List[User],
        team_memberships: List,
        num_tasks_range: tuple = (20, 100)
    ) -> List[Task]:
        """Generate realistic tasks for projects.
        
        Task distribution per project: 20-100 tasks
        Assignee distribution: 15% unassigned (per Asana benchmarks)
        """
        tasks = []
        
        # Build project to sections mapping
        project_sections = {}
        for section in sections:
            if section.project_id not in project_sections:
                project_sections[section.project_id] = []
            project_sections[section.project_id].append(section)
        
        # Build project to team to users mapping
        from collections import defaultdict
        team_users = defaultdict(list)
        for membership in team_memberships:
            team_users[membership.team_id].append(membership.user_id)
        
        project_users = {}
        for project in projects:
            user_ids = team_users.get(project.team_id, [])
            project_users[project.project_id] = [u for u in users if u.user_id in user_ids]
        
        print("Generating tasks with LLM...")
        
        for project in projects:
            num_tasks = random.randint(*num_tasks_range)
            project_secs = project_sections.get(project.project_id, [])
            available_users = project_users.get(project.project_id, users)
            
            if not project_secs:
                continue
            
            # Generate task names in batch
            prompts = []
            for _ in range(num_tasks):
                prompt = self._get_task_name_prompt(project)
                prompts.append(prompt)
            
            task_names = await self.llm_helper.generate_batch(prompts[:min(num_tasks, 50)], batch_size=5, delay=12.0)
            
            # Pad with fallback names if needed
            while len(task_names) < num_tasks:
                task_names.append(f"Task {len(task_names) + 1}")
            
            for i in range(num_tasks):
                task = await self._generate_single_task(
                    project, 
                    project_secs, 
                    available_users, 
                    task_names[i] if i < len(task_names) else f"Task {i+1}"
                )
                tasks.append(task)
        
        return tasks
    
    def _get_task_name_prompt(self, project: Project) -> str:
        """Get appropriate prompt for task name generation."""
        if 'Engineering' in project.project_type or 'sprint' in project.project_type:
            return f"Generate ONE realistic software engineering task name for project '{project.name}'. Follow pattern: [Component] - [Action] - [Detail]. Be specific and technical. Only return the task name."
        elif 'Marketing' in project.project_type or 'campaign' in project.project_type:
            return f"Generate ONE realistic marketing task name for project '{project.name}'. Follow pattern: [Campaign/Initiative] - [Deliverable]. Only return the task name."
        elif 'Product' in project.project_type:
            return f"Generate ONE realistic product management task name for project '{project.name}'. Only return the task name."
        else:
            return f"Generate ONE realistic business task name for project '{project.name}'. Only return the task name."
    
    async def _generate_single_task(
        self,
        project: Project,
        sections: List[Section],
        available_users: List[User],
        task_name: str
    ) -> Task:
        """Generate a single task with realistic attributes."""
        
        # Assign to section (distribute across sections)
        section = random.choice(sections)
        
        # Task creation date after project creation
        created_at = self.date_helper.random_datetime_in_range(
            max(project.created_at, self.date_helper.start_date),
            self.date_helper.end_date
        )
        
        # Assignee (15% unassigned per benchmarks)
        assignee_id = None
        if random.random() > 0.15 and available_users:
            assignee_id = random.choice(available_users).user_id
        
        # Creator
        created_by = random.choice(available_users).user_id if available_users else assignee_id
        
        # Due date with realistic distribution
        due_date = self.date_helper.random_date_in_future(created_at)
        
        # Completion status based on project type and age
        completed = self.date_helper.is_completed(created_at, project.project_type)
        completed_at = None
        completed_by = None
        
        if completed:
            completed_at = self.date_helper.completion_time(created_at)
            completed_by = assignee_id if assignee_id else created_by
        
        # Priority distribution: 10% high, 30% medium, 40% normal, 20% low/none
        priority_dist = [
            ('high', 0.10),
            ('medium', 0.30),
            ('normal', 0.40),
            (None, 0.20)
        ]
        priority = weighted_choice(priority_dist)
        
        task = Task(
            task_id=generate_id(),
            project_id=project.project_id,
            section_id=section.section_id,
            parent_task_id=None,
            name=task_name.strip(),
            description=None,  # Can be added later
            assignee_id=assignee_id,
            created_by=created_by,
            created_at=created_at,
            modified_at=created_at,
            due_date=due_date,
            start_date=None,
            completed=completed,
            completed_at=completed_at,
            completed_by=completed_by,
            priority=priority,
            num_hearts=random.randint(0, 5) if random.random() < 0.3 else 0,
            num_subtasks=0,
            num_subtasks_completed=0
        )
        
        return task
    
    def save_to_db(self, conn: sqlite3.Connection, tasks: List[Task]):
        """Save tasks to database."""
        cursor = conn.cursor()
        
        for task in tasks:
            cursor.execute("""
                INSERT INTO tasks (
                    task_id, project_id, section_id, parent_task_id, name, description,
                    assignee_id, created_by, created_at, modified_at, due_date, start_date,
                    completed, completed_at, completed_by, priority, num_hearts, 
                    num_subtasks, num_subtasks_completed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.task_id, task.project_id, task.section_id, task.parent_task_id,
                task.name, task.description, task.assignee_id, task.created_by,
                task.created_at.isoformat(), task.modified_at.isoformat(),
                task.due_date, task.start_date, task.completed,
                task.completed_at.isoformat() if task.completed_at else None,
                task.completed_by, task.priority, task.num_hearts,
                task.num_subtasks, task.num_subtasks_completed
            ))
        
        conn.commit()

class CommentGenerator:
    """Generate realistic comments/stories."""
    
    def __init__(self, date_helper: DateHelper, llm_helper: LLMHelper):
        self.date_helper = date_helper
        self.llm_helper = llm_helper
    
    async def generate_comments(self, tasks: List[Task], users: List[User], comments_per_task: float = 1.5) -> List[Comment]:
        """Generate comments for tasks.
        
        Not all tasks have comments. Average ~1.5 comments per task.
        """
        comments = []
        
        print("Generating comments...")
        
        for task in tasks:
            # Determine number of comments (0-5, weighted toward fewer)
            num_comments = weighted_choice([
                (0, 0.40),  # 40% have no comments
                (1, 0.30),  # 30% have 1 comment
                (2, 0.15),  # 15% have 2 comments
                (3, 0.10),  # 10% have 3 comments
                (4, 0.04),  # 4% have 4 comments
                (5, 0.01)   # 1% have 5+ comments
            ])
            
            for _ in range(num_comments):
                comment_types = ['update', 'question', 'answer', 'mention']
                comment_type = random.choice(comment_types)
                
                # Comment created after task
                comment_created = self.date_helper.random_datetime_in_range(
                    task.created_at,
                    task.completed_at if task.completed_at else self.date_helper.end_date
                )
                
                # Generate comment text
                comment_text = await self._generate_comment_text(task.name, comment_type)
                
                comment = Comment(
                    comment_id=generate_id(),
                    task_id=task.task_id,
                    user_id=random.choice(users).user_id,
                    text=comment_text,
                    comment_type='comment',
                    created_at=comment_created
                )
                comments.append(comment)
        
        return comments
    
    async def _generate_comment_text(self, task_name: str, comment_type: str) -> str:
        """Generate realistic comment text."""
        prompts = {
            'update': f"Write a brief status update comment (1-2 sentences) for a task named '{task_name}'. Only return the comment.",
            'question': f"Write a brief question (1 sentence) about a task named '{task_name}'. Only return the comment.",
            'answer': f"Write a brief answer (1-2 sentences) to a question about a task named '{task_name}'. Only return the comment.",
            'mention': f"Write a brief comment (1 sentence) mentioning someone about a task named '{task_name}'. Use @Name format. Only return the comment."
        }
        
        text = await self.llm_helper.generate_content(prompts.get(comment_type, prompts['update']))
        return text if text else "Updated status"
    
    def save_to_db(self, conn: sqlite3.Connection, comments: List[Comment]):
        """Save comments to database."""
        cursor = conn.cursor()
        
        for comment in comments:
            cursor.execute("""
                INSERT INTO comments (comment_id, task_id, user_id, text, comment_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                comment.comment_id, comment.task_id, comment.user_id,
                comment.text, comment.comment_type, comment.created_at.isoformat()
            ))
        
        conn.commit()

class CustomFieldGenerator:
    """Generate custom fields for projects."""
    
    def __init__(self, date_helper: DateHelper):
        self.date_helper = date_helper
    
    def generate_custom_fields(
        self, 
        projects: List[Project], 
        tasks: List[Task]
    ) -> tuple[List[CustomFieldDefinition], List[CustomFieldValue]]:
        """Generate custom fields and values."""
        definitions = []
        values = []
        
        # Common custom fields by project type
        field_templates = {
            'sprint': [
                ('Story Points', 'number', ['1', '2', '3', '5', '8', '13']),
                ('Priority', 'enum', ['P0', 'P1', 'P2', 'P3']),
                ('Sprint', 'text', None)
            ],
            'bug_tracking': [
                ('Severity', 'enum', ['Critical', 'High', 'Medium', 'Low']),
                ('Bug Type', 'enum', ['Frontend', 'Backend', 'Mobile', 'Infrastructure']),
                ('Found in Version', 'text', None)
            ],
            'campaign': [
                ('Status', 'enum', ['Planning', 'In Progress', 'Review', 'Launched']),
                ('Budget', 'number', None),
                ('Launch Date', 'date', None)
            ]
        }
        
        # Group tasks by project
        project_tasks = {}
        for task in tasks:
            if task.project_id not in project_tasks:
                project_tasks[task.project_id] = []
            project_tasks[task.project_id].append(task)
        
        for project in projects:
            templates = field_templates.get(project.project_type, [])
            
            for field_name, field_type, enum_opts in templates:
                field_def = CustomFieldDefinition(
                    field_id=generate_id(),
                    project_id=project.project_id,
                    name=field_name,
                    field_type=field_type,
                    description=None,
                    enum_options=','.join(enum_opts) if enum_opts else None,
                    precision=0 if field_type == 'number' else None,
                    created_at=project.created_at
                )
                definitions.append(field_def)
                
                # Generate values for 70% of tasks in this project
                proj_tasks = project_tasks.get(project.project_id, [])
                for task in proj_tasks:
                    if random.random() < 0.70:
                        if enum_opts:
                            value = random.choice(enum_opts)
                        elif field_type == 'number':
                            value = str(random.randint(1, 10))
                        else:
                            value = f"Value {random.randint(1, 100)}"
                        
                        field_value = CustomFieldValue(
                            value_id=generate_id(),
                            task_id=task.task_id,
                            field_id=field_def.field_id,
                            value=value,
                            created_at=task.created_at
                        )
                        values.append(field_value)
        
        return definitions, values
    
    def save_to_db(
        self, 
        conn: sqlite3.Connection, 
        definitions: List[CustomFieldDefinition], 
        values: List[CustomFieldValue]
    ):
        """Save custom fields to database."""
        cursor = conn.cursor()
        
        for field_def in definitions:
            cursor.execute("""
                INSERT INTO custom_field_definitions (
                    field_id, project_id, name, field_type, description, enum_options, precision, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                field_def.field_id, field_def.project_id, field_def.name, field_def.field_type,
                field_def.description, field_def.enum_options, field_def.precision,
                field_def.created_at.isoformat()
            ))
        
        for value in values:
            cursor.execute("""
                INSERT INTO custom_field_values (value_id, task_id, field_id, value, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (value.value_id, value.task_id, value.field_id, value.value, value.created_at.isoformat()))
        
        conn.commit()

class TagGenerator:
    """Generate tags and task-tag associations."""
    
    def __init__(self, date_helper: DateHelper):
        self.date_helper = date_helper
    
    def generate_tags(
        self, 
        org_id: str, 
        tasks: List[Task]
    ) -> tuple[List[Tag], List[TaskTag]]:
        """Generate organizational tags and associations."""
        tags = []
        task_tags = []
        
        # Common tags in project management
        tag_names = [
            'urgent', 'blocked', 'needs-review', 'bug', 'feature',
            'technical-debt', 'security', 'performance', 'design',
            'documentation', 'testing', 'research', 'customer-request'
        ]
        
        for tag_name in tag_names:
            tag = Tag(
                tag_id=generate_id(),
                org_id=org_id,
                name=tag_name,
                color=random_color(),
                created_at=self.date_helper.start_date
            )
            tags.append(tag)
        
        # 30% of tasks have tags (1-3 tags per task)
        for task in tasks:
            if random.random() < 0.30:
                num_tags = weighted_choice([(1, 0.6), (2, 0.3), (3, 0.1)])
                selected_tags = random.sample(tags, min(num_tags, len(tags)))
                
                for tag in selected_tags:
                    task_tag = TaskTag(
                        task_tag_id=generate_id(),
                        task_id=task.task_id,
                        tag_id=tag.tag_id,
                        created_at=task.created_at
                    )
                    task_tags.append(task_tag)
        
        return tags, task_tags
    
    def save_to_db(self, conn: sqlite3.Connection, tags: List[Tag], task_tags: List[TaskTag]):
        """Save tags to database."""
        cursor = conn.cursor()
        
        for tag in tags:
            cursor.execute("""
                INSERT INTO tags (tag_id, org_id, name, color, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (tag.tag_id, tag.org_id, tag.name, tag.color, tag.created_at.isoformat()))
        
        for task_tag in task_tags:
            cursor.execute("""
                INSERT INTO task_tags (task_tag_id, task_id, tag_id, created_at)
                VALUES (?, ?, ?, ?)
            """, (task_tag.task_tag_id, task_tag.task_id, task_tag.tag_id, task_tag.created_at.isoformat()))
        
        conn.commit()

class AttachmentGenerator:
    """Generate attachment metadata."""
    
    def __init__(self, date_helper: DateHelper):
        self.date_helper = date_helper
    
    def generate_attachments(self, tasks: List[Task], users: List[User]) -> List[Attachment]:
        """Generate realistic attachment metadata (not actual files)."""
        attachments = []
        
        file_types = ['pdf', 'docx', 'png', 'jpg', 'xlsx', 'txt', 'csv']
        file_name_templates = [
            'document_{}.{}', 'screenshot_{}.{}', 'report_{}.{}',
            'design_{}.{}', 'data_{}.{}', 'spec_{}.{}'
        ]
        
        # 20% of tasks have attachments
        for task in tasks:
            if random.random() < 0.20:
                num_attachments = weighted_choice([(1, 0.7), (2, 0.2), (3, 0.1)])
                
                for _ in range(num_attachments):
                    file_type = random.choice(file_types)
                    template = random.choice(file_name_templates)
                    file_name = template.format(random.randint(1, 999), file_type)
                    
                    # Realistic file sizes
                    if file_type in ['png', 'jpg']:
                        size_bytes = random.randint(50000, 5000000)  # 50KB - 5MB
                    elif file_type in ['pdf', 'docx']:
                        size_bytes = random.randint(10000, 2000000)  # 10KB - 2MB
                    else:
                        size_bytes = random.randint(1000, 500000)  # 1KB - 500KB
                    
                    uploaded_at = self.date_helper.random_datetime_in_range(
                        task.created_at,
                        task.completed_at if task.completed_at else self.date_helper.end_date
                    )
                    
                    attachment = Attachment(
                        attachment_id=generate_id(),
                        task_id=task.task_id,
                        name=file_name,
                        file_type=file_type,
                        size_bytes=size_bytes,
                        uploaded_by=random.choice(users).user_id,
                        uploaded_at=uploaded_at,
                        download_url=f"https://example-storage.com/files/{generate_id()}"
                    )
                    attachments.append(attachment)
        
        return attachments
    
    def save_to_db(self, conn: sqlite3.Connection, attachments: List[Attachment]):
        """Save attachments to database."""
        cursor = conn.cursor()
        
        for attachment in attachments:
            cursor.execute("""
                INSERT INTO attachments (
                    attachment_id, task_id, name, file_type, size_bytes, 
                    uploaded_by, uploaded_at, download_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                attachment.attachment_id, attachment.task_id, attachment.name,
                attachment.file_type, attachment.size_bytes, attachment.uploaded_by,
                attachment.uploaded_at.isoformat(), attachment.download_url
            ))
        
        conn.commit()
