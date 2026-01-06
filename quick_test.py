"""Quick test generation without LLM calls for faster validation."""
import os
os.environ['ORG_SIZE'] = '100'
os.environ['NUM_TEAMS'] = '5'
os.environ['NUM_PROJECTS'] = '10'

import sqlite3
import asyncio
from datetime import datetime
from pathlib import Path

from src.generators.users import OrganizationGenerator, UserGenerator
from src.generators.projects import TeamGenerator
from src.utils.date_helper import DateHelper
from src.utils.helpers import generate_id
from src.models import Project, Section

# Simple test without LLM
async def quick_test():
    db_path = 'output/test_asana.sqlite'
    
    # Remove existing
    if Path(db_path).exists():
        os.remove(db_path)
    
    Path('output').mkdir(exist_ok=True)
    
    # Initialize DB
    conn = sqlite3.connect(db_path)
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    date_helper = DateHelper('2024-08-01', '2025-01-31')
    
    print("Generating test data...")
    
    # Org
    org_gen = OrganizationGenerator(date_helper)
    org = org_gen.generate(100)
    org_gen.save_to_db(conn, org)
    print(f"✓ Organization: {org.name}")
    
    # Users
    user_gen = UserGenerator(date_helper)
    users = user_gen.generate_users(org, 100)
    user_gen.save_to_db(conn, users)
    print(f"✓ Users: {len(users)}")
    
    # Teams
    team_gen = TeamGenerator(date_helper)
    teams, memberships = team_gen.generate_teams(org.org_id, 5, users)
    team_gen.save_to_db(conn, teams, memberships)
    print(f"✓ Teams: {len(teams)}, Memberships: {len(memberships)}")
    
    # Simple projects without LLM
    projects = []
    sections = []
    
    project_names = [
        "Backend Infrastructure Sprint",
        "Mobile App Development",
        "Q4 Marketing Campaign",
        "Product Roadmap Planning",
        "Bug Bash - Payment System"
    ]
    
    for i, team in enumerate(teams):
        name = project_names[i] if i < len(project_names) else f"Project {i+1}"
        project = Project(
            project_id=generate_id(),
            team_id=team.team_id,
            name=name,
            description=None,
            project_type='sprint',
            owner_id=users[0].user_id,
            status='active',
            privacy='team',
            created_at=date_helper.start_date,
            due_date=None,
            archived=False,
            color='blue'
        )
        projects.append(project)
        
        # Sections
        for pos, sec_name in enumerate(['To Do', 'In Progress', 'Done']):
            section = Section(
                section_id=generate_id(),
                project_id=project.project_id,
                name=sec_name,
                position=pos,
                created_at=date_helper.start_date
            )
            sections.append(section)
    
    # Save projects
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
    conn.close()
    
    print(f"✓ Projects: {len(projects)}, Sections: {len(sections)}")
    print(f"\n✅ Test database created: {db_path}")
    print("Run: python validate_db.py output/test_asana.sqlite")

if __name__ == '__main__':
    asyncio.run(quick_test())
