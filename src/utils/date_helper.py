from datetime import datetime, timedelta, date
import random
import numpy as np

class DateHelper:
    """Helper class for generating realistic dates and timestamps."""
    
    def __init__(self, start_date: str, end_date: str):
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.total_days = (self.end_date - self.start_date).days
    
    def random_datetime_in_range(self, start: datetime = None, end: datetime = None, business_hours: bool = True) -> datetime:
        """Generate random datetime within range."""
        if start is None:
            start = self.start_date
        if end is None:
            end = self.end_date
        
        delta = (end - start).total_seconds()
        random_seconds = random.uniform(0, delta)
        dt = start + timedelta(seconds=random_seconds)
        
        if business_hours:
            # Adjust to business hours (9 AM - 6 PM)
            dt = dt.replace(hour=random.randint(9, 18), minute=random.randint(0, 59))
        
        return dt
    
    def random_date_in_future(self, from_date: datetime, distribution: str = 'normal') -> Optional[date]:
        """Generate realistic due dates based on research.
        
        Distribution based on Asana benchmarks:
        - 25% within 1 week
        - 40% within 1 month
        - 20% 1-3 months out
        - 10% no due date
        - 5% overdue
        """
        rand = random.random()
        
        if rand < 0.10:  # 10% no due date
            return None
        elif rand < 0.15:  # 5% overdue
            days_overdue = random.randint(1, 30)
            return (from_date - timedelta(days=days_overdue)).date()
        elif rand < 0.40:  # 25% within 1 week
            days = random.randint(1, 7)
            due = from_date + timedelta(days=days)
        elif rand < 0.80:  # 40% within 1 month
            days = random.randint(8, 30)
            due = from_date + timedelta(days=days)
        else:  # 20% 1-3 months
            days = random.randint(31, 90)
            due = from_date + timedelta(days=days)
        
        # Avoid weekends for 85% of tasks
        if random.random() < 0.85:
            while due.weekday() >= 5:  # Saturday or Sunday
                due += timedelta(days=1)
        
        return due.date()
    
    def is_completed(self, created_at: datetime, project_type: str) -> bool:
        """Determine if task should be completed based on project type and age.
        
        Completion rates vary by project type:
        - Sprint projects: 70-85%
        - Bug tracking: 60-70%
        - Ongoing projects: 40-50%
        """
        days_old = (self.end_date - created_at).days
        
        # Older tasks more likely to be completed
        age_factor = min(days_old / 30, 1.5)
        
        if project_type == 'sprint':
            base_rate = random.uniform(0.70, 0.85)
        elif project_type == 'bug_tracking':
            base_rate = random.uniform(0.60, 0.70)
        else:
            base_rate = random.uniform(0.40, 0.50)
        
        completion_probability = min(base_rate * age_factor, 0.95)
        return random.random() < completion_probability
    
    def completion_time(self, created_at: datetime) -> datetime:
        """Generate realistic completion time (1-14 days after creation, log-normal distribution)."""
        # Log-normal distribution based on cycle time benchmarks
        days = int(np.random.lognormal(mean=1.5, sigma=0.8))
        days = max(1, min(days, 14))  # Clamp between 1-14 days
        
        hours = random.randint(1, 8)
        completion = created_at + timedelta(days=days, hours=hours)
        
        # Ensure it's in business hours
        completion = completion.replace(hour=random.randint(9, 18))
        
        return completion
    
    def weighted_creation_date(self) -> datetime:
        """Generate creation date with realistic distribution.
        
        Higher creation rates Mon-Wed, lower Thu-Fri.
        """
        dt = self.random_datetime_in_range(business_hours=True)
        
        # Adjust based on day of week
        weekday = dt.weekday()
        if weekday in [0, 1, 2]:  # Mon-Wed: higher activity
            pass
        elif weekday in [3, 4]:  # Thu-Fri: lower activity
            if random.random() < 0.3:  # 30% chance to skip
                dt = dt + timedelta(days=random.randint(1, 3))
        else:  # Weekend: very low activity
            if random.random() < 0.8:  # 80% chance to move to Monday
                days_to_monday = (7 - weekday) % 7
                dt = dt + timedelta(days=days_to_monday)
        
        return dt
