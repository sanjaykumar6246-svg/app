"""Organization and user data generators."""
import sqlite3
from datetime import datetime
from typing import List
import random

from src.models import Organization, User
from src.scrapers.company_scraper import CompanyScraper
from src.scrapers.demographic_scraper import DemographicScraper
from src.utils.helpers import generate_id
from src.utils.date_helper import DateHelper

class OrganizationGenerator:
    """Generate realistic organization data."""
    
    def __init__(self, date_helper: DateHelper):
        self.date_helper = date_helper
        self.company_scraper = CompanyScraper()
    
    def generate(self, num_employees: int) -> Organization:
        """Generate a single organization."""
        company_name, domain = self.company_scraper.get_company_for_simulation(num_employees)
        
        org = Organization(
            org_id=generate_id(),
            name=company_name,
            domain=domain,
            is_organization=True,
            created_at=self.date_helper.start_date,
            num_employees=num_employees
        )
        
        return org
    
    def save_to_db(self, conn: sqlite3.Connection, org: Organization):
        """Save organization to database."""
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO organizations (org_id, name, domain, is_organization, created_at, num_employees)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            org.org_id, org.name, org.domain, org.is_organization,
            org.created_at.isoformat(), org.num_employees
        ))
        conn.commit()

class UserGenerator:
    """Generate realistic user data."""
    
    def __init__(self, date_helper: DateHelper):
        self.date_helper = date_helper
        self.demographic_scraper = DemographicScraper()
        self.generated_emails = set()
    
    def generate_users(self, org: Organization, num_users: int) -> List[User]:
        """Generate multiple users for an organization.
        
        Role distribution based on typical B2B SaaS company:
        - Engineers: 40-50%
        - Product: 10-15%
        - Marketing: 10-15%
        - Sales: 15-20%
        - Operations/Support: 10-15%
        - Leadership: 5%
        """
        users = []
        
        # Define role distribution
        roles_dist = [
            ('Engineer', 0.45),
            ('Product Manager', 0.12),
            ('Marketing Manager', 0.12),
            ('Sales Representative', 0.17),
            ('Customer Success', 0.08),
            ('Designer', 0.06),
        ]
        
        departments = {
            'Engineer': 'Engineering',
            'Product Manager': 'Product',
            'Marketing Manager': 'Marketing',
            'Sales Representative': 'Sales',
            'Customer Success': 'Operations',
            'Designer': 'Design'
        }
        
        for i in range(num_users):
            # Select role based on distribution
            rand = random.random()
            cumulative = 0
            role = 'Engineer'
            
            for r, prob in roles_dist:
                cumulative += prob
                if rand < cumulative:
                    role = r
                    break
            
            name = self.demographic_scraper.generate_name()
            email = self.demographic_scraper.generate_email(name, org.domain)
            
            # Ensure unique emails
            counter = 1
            original_email = email
            while email in self.generated_emails:
                email = original_email.replace('@', f'{counter}@')
                counter += 1
            
            self.generated_emails.add(email)
            
            # Stagger user creation dates over first month
            created_at = self.date_helper.start_date
            if i > 0:
                days_offset = random.randint(0, 30)
                created_at = self.date_helper.random_datetime_in_range(
                    self.date_helper.start_date,
                    self.date_helper.start_date + timedelta(days=30)
                )
            
            user = User(
                user_id=generate_id(),
                org_id=org.org_id,
                email=email,
                name=name,
                role=role,
                department=departments.get(role),
                photo_url=None,
                created_at=created_at,
                is_active=random.random() < 0.95  # 95% active users
            )
            
            users.append(user)
        
        return users
    
    def save_to_db(self, conn: sqlite3.Connection, users: List[User]):
        """Save users to database."""
        cursor = conn.cursor()
        for user in users:
            cursor.execute("""
                INSERT INTO users (user_id, org_id, email, name, role, department, photo_url, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user.user_id, user.org_id, user.email, user.name, user.role,
                user.department, user.photo_url, user.created_at.isoformat(), user.is_active
            ))
        conn.commit()

from datetime import timedelta
