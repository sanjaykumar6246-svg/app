"""Team and project generators."""
import sqlite3
from typing import List, Dict
import random
import asyncio

from src.models import Team, TeamMembership, Project, Section, User
from src.utils.helpers import generate_id, random_color, weighted_choice
from src.utils.date_helper import DateHelper
from src.utils.llm_helper import LLMHelper

class TeamGenerator:
    """Generate realistic team data."""
    
    def __init__(self, date_helper: DateHelper):
        self.date_helper = date_helper
    
    def generate_teams(self, org_id: str, num_teams: int, users: List[User]) -> tuple[List[Team], List[TeamMembership]]:
        """Generate teams with realistic composition.
        
        Team types based on typical B2B SaaS structure:
        - Engineering teams (50-60%)
        - Product teams (15-20%)
        - Marketing teams (10-15%)
        - Operations teams (10-15%)
        """
        teams = []
        memberships = []
        
        team_types_dist = [
            ('Engineering', 0.55),
            ('Product', 0.17),
            ('Marketing', 0.13),
            ('Operations', 0.15)
        ]
        
        # Group users by department
        users_by_dept = {}
        for user in users:
            dept = user.department or 'Other'
            if dept not in users_by_dept:
                users_by_dept[dept] = []
            users_by_dept[dept].append(user)
        
        for i in range(num_teams):
            team_type = weighted_choice(team_types_dist)
            
            # Generate team name
            if team_type == 'Engineering':
                names = ['Backend', 'Frontend', 'Mobile', 'Infrastructure', 'Platform', 'API', 'Data']
                team_name = f"{random.choice(names)} Team"
            elif team_type == 'Product':
                names = ['Core Product', 'Growth', 'Platform', 'Analytics', 'Enterprise']
                team_name = f"{random.choice(names)} Team"
            elif team_type == 'Marketing':
                names = ['Content', 'Growth Marketing', 'Product Marketing', 'Brand', 'Demand Gen']
                team_name = f"{random.choice(names)} Team"
            else:
                names = ['Customer Success', 'Support', 'Operations', 'People Ops']
                team_name = random.choice(names)
            
            team = Team(
                team_id=generate_id(),
                org_id=org_id,
                name=team_name,
                description=None,
                team_type=team_type,
                created_at=self.date_helper.start_date
            )
            teams.append(team)
            
            # Assign users to team (5-20 members per team)
            team_size = random.randint(5, 20)
            
            # Get relevant users for this team type
            relevant_dept = team_type if team_type in users_by_dept else None
            if relevant_dept:
                available_users = users_by_dept[relevant_dept].copy()
            else:
                available_users = users.copy()
            
            random.shuffle(available_users)
            team_members = available_users[:min(team_size, len(available_users))]
            
            for user in team_members:
                # 10% chance of being a team lead
                role = 'lead' if random.random() < 0.1 else 'member'
                
                membership = TeamMembership(
                    membership_id=generate_id(),
                    team_id=team.team_id,
                    user_id=user.user_id,
                    role=role,
                    joined_at=self.date_helper.start_date
                )
                memberships.append(membership)
        
        return teams, memberships
    
    def save_to_db(self, conn: sqlite3.Connection, teams: List[Team], memberships: List[TeamMembership]):
        """Save teams and memberships to database."""
        cursor = conn.cursor()
        
        for team in teams:
            cursor.execute("""
                INSERT INTO teams (team_id, org_id, name, description, team_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (team.team_id, team.org_id, team.name, team.description, team.team_type, team.created_at.isoformat()))
        
        for membership in memberships:
            cursor.execute("""
                INSERT INTO team_memberships (membership_id, team_id, user_id, role, joined_at)
                VALUES (?, ?, ?, ?, ?)
            """, (membership.membership_id, membership.team_id, membership.user_id, membership.role, membership.joined_at.isoformat()))
        
        conn.commit()

class ProjectGenerator:
    """Generate realistic project data."""
    
    def __init__(self, date_helper: DateHelper, llm_helper: LLMHelper):
        self.date_helper = date_helper
        self.llm_helper = llm_helper
    
    async def generate_projects(self, teams: List[Team], users: List[User], num_projects: int) -> tuple[List[Project], List[Section]]:
        """Generate projects with sections."""
        projects = []
        sections = []
        
        # Map teams to users
        team_owners = {}
        for team in teams:
            # Pick a random user from this team as potential owner
            team_owners[team.team_id] = random.choice(users).user_id
        
        # Project type distribution
        project_types_map = {
            'Engineering': ['sprint', 'bug_tracking', 'infrastructure', 'feature_dev'],
            'Product': ['roadmap', 'research', 'planning'],
            'Marketing': ['campaign', 'content', 'events'],
            'Operations': ['process', 'planning', 'ops']
        }
        
        # Generate project names using LLM
        print("Generating project names with LLM (in batches)...")
        prompts = []
        project_metadata = []
        
        # Fallback project name templates
        fallback_names = {
            'sprint': ['Sprint {}', 'Development Sprint {}', 'Iteration {}', 'Sprint Planning {}'],
            'bug_tracking': ['Bug Fixes {}', 'Issues Tracker {}', 'Bug Management {}'],
            'infrastructure': ['Infrastructure {}', 'DevOps {}', 'Platform Work {}'],
            'feature_dev': ['Feature Development {}', 'New Features {}', 'Product Features {}'],
            'roadmap': ['Product Roadmap {}', 'Roadmap Planning {}', 'Strategy {}'],
            'research': ['User Research {}', 'Product Research {}', 'Market Research {}'],
            'planning': ['Planning {}', 'Strategic Planning {}', 'Quarterly Planning {}'],
            'campaign': ['Marketing Campaign {}', 'Campaign {}', 'Launch Campaign {}'],
            'content': ['Content Creation {}', 'Content Strategy {}', 'Content Planning {}'],
            'events': ['Event Planning {}', 'Events {}', 'Conference {}'],
            'process': ['Process Improvement {}', 'Ops Process {}', 'Workflow {}'],
            'ops': ['Operations {}', 'Ops Work {}', 'Operational Planning {}'],
            'general': ['Project {}', 'Initiative {}', 'Workstream {}']
        }
        
        for i in range(num_projects):
            team = random.choice(teams)
            project_types = project_types_map.get(team.team_type, ['general'])
            project_type = random.choice(project_types)
            
            project_metadata.append((team, project_type))
            
            prompt = f"Generate ONE realistic Asana project name for a {project_type} project in a {team.team_type} team at a B2B SaaS company. Only return the project name, nothing else."
            prompts.append(prompt)
        
        # Batch generate project names with smaller batch size and delays
        project_names = await self.llm_helper.generate_batch(prompts[:num_projects], batch_size=20, delay=2.0)
        
        for i, (team, project_type) in enumerate(project_metadata):
            # Use LLM-generated name if available, otherwise use fallback
            if i < len(project_names) and project_names[i]:
                project_name = project_names[i]
            else:
                # Use fallback template
                templates = fallback_names.get(project_type, fallback_names['general'])
                template = random.choice(templates)
                project_name = f"{team.name} - {template.format(i+1)}"
            
            created_at = self.date_helper.weighted_creation_date()
            
            # 30% of projects have due dates
            due_date = None
            if random.random() < 0.3:
                due_date = self.date_helper.random_date_in_future(created_at)
            
            project = Project(
                project_id=generate_id(),
                team_id=team.team_id,
                name=project_name.strip(),
                description=None,  # Can be added later
                project_type=project_type,
                owner_id=team_owners.get(team.team_id),
                status='active' if random.random() < 0.9 else 'archived',
                privacy='team',
                created_at=created_at,
                due_date=due_date,
                archived=random.random() < 0.1,  # 10% archived
                color=random_color()
            )
            projects.append(project)
            
            # Generate sections for project
            section_templates = {
                'sprint': ['To Do', 'In Progress', 'In Review', 'Done'],
                'bug_tracking': ['New', 'Triaged', 'In Progress', 'Fixed', 'Closed'],
                'campaign': ['Planning', 'In Progress', 'Review', 'Launched'],
                'roadmap': ['Planned', 'In Progress', 'Shipped'],
                'default': ['To Do', 'In Progress', 'Done']
            }
            
            section_names = section_templates.get(project_type, section_templates['default'])
            
            for pos, section_name in enumerate(section_names):
                section = Section(
                    section_id=generate_id(),
                    project_id=project.project_id,
                    name=section_name,
                    position=pos,
                    created_at=created_at
                )
                sections.append(section)
        
        return projects, sections
    
    def save_to_db(self, conn: sqlite3.Connection, projects: List[Project], sections: List[Section]):
        """Save projects and sections to database."""
        cursor = conn.cursor()
        
        for project in projects:
            cursor.execute("""
                INSERT INTO projects (project_id, team_id, name, description, project_type, owner_id, 
                                     status, privacy, created_at, due_date, archived, color)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project.project_id, project.team_id, project.name, project.description,
                project.project_type, project.owner_id, project.status, project.privacy,
                project.created_at.isoformat(), project.due_date, project.archived, project.color
            ))
        
        for section in sections:
            cursor.execute("""
                INSERT INTO sections (section_id, project_id, name, position, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (section.section_id, section.project_id, section.name, section.position, section.created_at.isoformat()))
        
        conn.commit()
