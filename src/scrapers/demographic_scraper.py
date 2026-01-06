"""Scraper for realistic user demographic data."""
import random
from typing import List, Dict
import json

class DemographicScraper:
    """Generate realistic user demographics based on census data patterns."""
    
    def __init__(self):
        # Based on US Census data and common naming patterns
        self.first_names_male = [
            "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
            "Thomas", "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald",
            "Steven", "Andrew", "Paul", "Joshua", "Kevin", "Brian", "George", "Timothy",
            "Ronald", "Jason", "Edward", "Jeffrey", "Ryan", "Jacob", "Gary", "Nicholas",
            "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin",
            "Samuel", "Raymond", "Gregory", "Alexander", "Patrick", "Jack", "Dennis", "Jerry"
        ]
        
        self.first_names_female = [
            "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan",
            "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
            "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Carol", "Amanda", "Dorothy",
            "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia",
            "Kathleen", "Amy", "Angela", "Shirley", "Anna", "Brenda", "Pamela", "Emma",
            "Nicole", "Helen", "Samantha", "Katherine", "Christine", "Debra", "Rachel"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
            "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
            "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
            "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
            "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
            "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
            "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
            "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
            "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson",
            "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
            "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster",
            "Jimenez", "Powell", "Jenkins", "Perry", "Russell", "Sullivan", "Bell", "Coleman"
        ]
    
    def generate_name(self) -> str:
        """Generate a realistic name based on demographic distributions."""
        # 50/50 gender distribution
        if random.random() < 0.5:
            first = random.choice(self.first_names_male)
        else:
            first = random.choice(self.first_names_female)
        
        last = random.choice(self.last_names)
        return f"{first} {last}"
    
    def generate_email(self, name: str, domain: str) -> str:
        """Generate email from name and company domain."""
        # Various email patterns used in companies
        parts = name.lower().split()
        patterns = [
            f"{parts[0]}.{parts[1]}@{domain}",  # john.doe@company.com (most common)
            f"{parts[0][0]}{parts[1]}@{domain}",  # jdoe@company.com
            f"{parts[0]}@{domain}",  # john@company.com
        ]
        return random.choice(patterns)
