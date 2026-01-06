"""Main orchestration script for Asana seed data generation."""
import os
import sqlite3
import asyncio
from dotenv import load_dotenv
from pathlib import Path

from src.generators.users import OrganizationGenerator, UserGenerator
from src.generators.projects import TeamGenerator, ProjectGenerator
from src.generators.tasks import (
    TaskGenerator, CommentGenerator, CustomFieldGenerator,
    TagGenerator, AttachmentGenerator
)
from src.utils.date_helper import DateHelper
from src.utils.llm_helper import LLMHelper

load_dotenv()

class AsanaSimulationGenerator:
    """Main class to orchestrate Asana simulation data generation."""
    
    def __init__(self):
        self.db_path = os.getenv('DB_PATH', 'output/asana_simulation.sqlite')
        self.org_size = int(os.getenv('ORG_SIZE', 7500))
        self.num_teams = int(os.getenv('NUM_TEAMS', 50))
        self.num_projects = int(os.getenv('NUM_PROJECTS', 200))
        
        start_date = os.getenv('START_DATE', '2024-08-01')
        end_date = os.getenv('END_DATE', '2025-01-31')
        
        self.date_helper = DateHelper(start_date, end_date)
        self.llm_helper = LLMHelper(provider='gemini', model='gemini-3-flash-preview')
        
        # Ensure output directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def init_database(self):
        """Initialize database with schema."""
        print(f"Initializing database: {self.db_path}")
        
        # Remove existing database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        
        conn = sqlite3.connect(self.db_path)
        
        # Load and execute schema
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
            conn.executescript(schema_sql)
        
        conn.commit()
        return conn
    
    async def generate(self):
        """Generate all data."""
        print("=" * 60)
        print("ASANA SIMULATION DATA GENERATION")
        print("=" * 60)
        print(f"Organization size: {self.org_size} employees")
        print(f"Number of teams: {self.num_teams}")
        print(f"Number of projects: {self.num_projects}")
        print("=" * 60)
        
        # Initialize database
        conn = self.init_database()
        
        # Step 1: Generate Organization
        print("\n[1/9] Generating organization...")
        org_gen = OrganizationGenerator(self.date_helper)
        org = org_gen.generate(self.org_size)
        org_gen.save_to_db(conn, org)
        print(f"  ✓ Created organization: {org.name}")
        
        # Step 2: Generate Users
        print(f"\n[2/9] Generating {self.org_size} users...")
        user_gen = UserGenerator(self.date_helper)
        users = user_gen.generate_users(org, self.org_size)
        user_gen.save_to_db(conn, users)
        print(f"  ✓ Created {len(users)} users")
        
        # Step 3: Generate Teams
        print(f"\n[3/9] Generating {self.num_teams} teams...")
        team_gen = TeamGenerator(self.date_helper)
        teams, memberships = team_gen.generate_teams(org.org_id, self.num_teams, users)
        team_gen.save_to_db(conn, teams, memberships)
        print(f"  ✓ Created {len(teams)} teams with {len(memberships)} memberships")
        
        # Step 4: Generate Projects
        print(f"\n[4/9] Generating {self.num_projects} projects...")
        project_gen = ProjectGenerator(self.date_helper, self.llm_helper)
        projects, sections = await project_gen.generate_projects(teams, users, self.num_projects)
        project_gen.save_to_db(conn, projects, sections)
        print(f"  ✓ Created {len(projects)} projects with {len(sections)} sections")
        
        # Step 5: Generate Tasks
        print(f"\n[5/9] Generating tasks (20-100 per project)...")
        task_gen = TaskGenerator(self.date_helper, self.llm_helper)
        tasks = await task_gen.generate_tasks(projects, sections, users, memberships, num_tasks_range=(20, 100))
        task_gen.save_to_db(conn, tasks)
        print(f"  ✓ Created {len(tasks)} tasks")
        
        # Step 6: Generate Comments
        print(f"\n[6/9] Generating comments...")
        comment_gen = CommentGenerator(self.date_helper, self.llm_helper)
        comments = await comment_gen.generate_comments(tasks, users)
        comment_gen.save_to_db(conn, comments)
        print(f"  ✓ Created {len(comments)} comments")
        
        # Step 7: Generate Custom Fields
        print(f"\n[7/9] Generating custom fields...")
        custom_field_gen = CustomFieldGenerator(self.date_helper)
        field_defs, field_values = custom_field_gen.generate_custom_fields(projects, tasks)
        custom_field_gen.save_to_db(conn, field_defs, field_values)
        print(f"  ✓ Created {len(field_defs)} custom field definitions with {len(field_values)} values")
        
        # Step 8: Generate Tags
        print(f"\n[8/9] Generating tags...")
        tag_gen = TagGenerator(self.date_helper)
        tags, task_tags = tag_gen.generate_tags(org.org_id, tasks)
        tag_gen.save_to_db(conn, tags, task_tags)
        print(f"  ✓ Created {len(tags)} tags with {len(task_tags)} task associations")
        
        # Step 9: Generate Attachments
        print(f"\n[9/9] Generating attachments...")
        attachment_gen = AttachmentGenerator(self.date_helper)
        attachments = attachment_gen.generate_attachments(tasks, users)
        attachment_gen.save_to_db(conn, attachments)
        print(f"  ✓ Created {len(attachments)} attachment records")
        
        # Close connection
        conn.close()
        
        print("\n" + "=" * 60)
        print("GENERATION COMPLETE!")
        print("=" * 60)
        print(f"Database saved to: {self.db_path}")
        print(f"Total records:")
        print(f"  - Organizations: 1")
        print(f"  - Users: {len(users)}")
        print(f"  - Teams: {len(teams)}")
        print(f"  - Team Memberships: {len(memberships)}")
        print(f"  - Projects: {len(projects)}")
        print(f"  - Sections: {len(sections)}")
        print(f"  - Tasks: {len(tasks)}")
        print(f"  - Comments: {len(comments)}")
        print(f"  - Custom Fields: {len(field_defs)} definitions, {len(field_values)} values")
        print(f"  - Tags: {len(tags)} tags, {len(task_tags)} associations")
        print(f"  - Attachments: {len(attachments)}")
        print("=" * 60)

async def main():
    """Entry point."""
    generator = AsanaSimulationGenerator()
    await generator.generate()

if __name__ == '__main__':
    asyncio.run(main())
