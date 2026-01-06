# Asana Seed Data Generator

A comprehensive system for generating realistic, high-quality seed data for an Asana RL environment simulation. This project creates a SQLite database representing a B2B SaaS company (5000-10000 employees) using Asana for project management.

## 📋 Overview

This system generates realistic enterprise-grade data that faithfully simulates real-world Asana usage patterns, including:

- **Organizations & Users** with realistic demographic distributions
- **Teams & Projects** with appropriate team structures
- **Tasks & Subtasks** with LLM-generated content using **Groq (FREE & Fast)**
- **Comments & Discussions** on tasks
- **Custom Fields** for different project types
- **Tags & Attachments** with realistic patterns

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager
- **FREE Groq API Key** (get from https://console.groq.com/keys)

### Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set your **FREE Groq API key**:
   ```
   GROQ_API_KEY=your-groq-api-key-here
   ```
   
   Get your free key at: **https://console.groq.com/keys**

### Running the Generator

```bash
python src/main.py
```

The script will:
1. Initialize a SQLite database
2. Generate organization and users
3. Create teams and projects
4. Generate tasks with LLM-powered content
5. Add comments, custom fields, tags, and attachments
6. Save everything to `output/asana_simulation.sqlite`

**Generation time**: Approximately 10-20 minutes depending on configuration and API response times.

## 📁 Project Structure

```
.
├── README.md                    # This file
├── DOCUMENTATION.md             # Detailed schema and methodology documentation
├── requirements.txt             # Python dependencies
├── schema.sql                   # Complete SQLite DDL
├── .env                         # Configuration (not in git)
├── .env.example                 # Example configuration
├── src/
│   ├── main.py                  # Entry point / orchestration
│   ├── models/                  # Pydantic data models
│   │   └── __init__.py
│   ├── scrapers/                # External data fetching
│   │   ├── company_scraper.py   # B2B SaaS company data
│   │   └── demographic_scraper.py # Realistic user demographics
│   ├── generators/              # Data generation logic
│   │   ├── users.py             # Organization & user generation
│   │   ├── projects.py          # Team & project generation
│   │   └── tasks.py             # Task, comment, custom field generation
│   └── utils/                   # Helper functions
│       ├── llm_helper.py        # LLM integration for content
│       ├── date_helper.py       # Realistic date/time generation
│       └── helpers.py           # Utility functions
├── prompts/                     # LLM prompt templates
│   ├── task_names.txt
│   ├── task_descriptions.txt
│   └── project_prompts.txt
└── output/
    └── asana_simulation.sqlite  # Generated database
```

## ⚙️ Configuration

Edit `.env` to customize generation parameters:

```env
# LLM Configuration
EMERGENT_LLM_KEY=your-key-here

# Database Configuration
DB_PATH=output/asana_simulation.sqlite

# Generation Scale
ORG_SIZE=7500              # Number of employees (5000-10000 recommended)
NUM_TEAMS=50               # Number of teams
NUM_PROJECTS=200           # Number of projects

# Date Range (6 months of history)
START_DATE=2024-08-01
END_DATE=2025-01-31
```

## 📊 Data Generation Approach

This system uses a **three-pronged approach** for realism:

1. **Scraped/Real-World Data**: Company names, user demographics based on census data
2. **LLM-Generated Content**: Task names, descriptions, comments using Gemini/Claude
3. **Research-Backed Distributions**: Due dates, completion rates, team sizes based on industry research

For detailed methodology, see [DOCUMENTATION.md](DOCUMENTATION.md).

## 🎯 Key Features

### Realistic Data Distributions

- **Task completion rates** vary by project type (70-85% for sprints, 40-50% for ongoing)
- **Due dates** follow realistic patterns (25% within 1 week, 40% within 1 month)
- **Assignee distribution** with 15% unassigned tasks (per Asana benchmarks)
- **Temporal consistency** ensuring all dates are logically ordered

### LLM-Powered Content

- Task names follow domain-specific patterns (e.g., "API - Implement - User authentication endpoint")
- Descriptions vary in length and detail (20% empty, 50% brief, 30% detailed)
- Comments include updates, questions, and mentions

### Enterprise-Scale Simulation

- 5000-10000 users with realistic role distributions
- 50+ teams organized by department
- 200+ projects across Engineering, Product, Marketing, and Operations
- 4000-20000 tasks with full lifecycle data

## 📖 Database Schema

The database includes 14 tables representing all major Asana entities:

- `organizations` - Company/workspace data
- `users` - User profiles with roles
- `teams` - Team structures
- `team_memberships` - User-team associations
- `projects` - Project details
- `sections` - Project sections (columns)
- `tasks` - Task data (the core entity)
- `comments` - Task comments/stories
- `custom_field_definitions` - Project-specific fields
- `custom_field_values` - Field values for tasks
- `tags` - Organization-wide tags
- `task_tags` - Task-tag associations
- `attachments` - File metadata

See [DOCUMENTATION.md](DOCUMENTATION.md) for complete schema details and ER diagram description.

## 🔍 Data Quality Validation

The generated data ensures:

1. **Temporal Consistency**: Tasks created after projects, completions after creation
2. **Relational Integrity**: All foreign keys reference valid records
3. **Business Logic**: Assignees are team members, sections belong to correct projects
4. **Realistic Edge Cases**: Overdue tasks, unassigned items, archived projects

## 📝 Example Queries

```sql
-- Get tasks by project with assignee names
SELECT t.name, u.name as assignee, t.due_date, t.completed
FROM tasks t
LEFT JOIN users u ON t.assignee_id = u.user_id
WHERE t.project_id = 'project-id'
ORDER BY t.created_at DESC;

-- Calculate completion rate by project type
SELECT p.project_type, 
       COUNT(*) as total_tasks,
       SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) as completed_tasks,
       ROUND(100.0 * SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) / COUNT(*), 2) as completion_rate
FROM tasks t
JOIN projects p ON t.project_id = p.project_id
GROUP BY p.project_type;

-- Find overdue tasks
SELECT t.name, t.due_date, u.name as assignee, p.name as project
FROM tasks t
JOIN projects p ON t.project_id = p.project_id
LEFT JOIN users u ON t.assignee_id = u.user_id
WHERE t.due_date < date('now') AND t.completed = 0;
```

## 🛠️ Extending the Generator

### Adding New Project Types

1. Update `project_types_map` in `src/generators/projects.py`
2. Add corresponding section templates
3. Update LLM prompts in `prompts/` directory

### Customizing LLM Prompts

1. Edit prompt files in `prompts/` directory
2. Modify `_get_task_name_prompt()` in `src/generators/tasks.py`
3. Adjust temperature in `llm_helper.py` for more/less variety

### Changing Data Distributions

1. Modify weights in `date_helper.py` for due dates and completions
2. Update `weighted_choice` calls in generators for different distributions
3. Adjust team sizes, task counts in respective generator files

## 📚 Research Sources

The methodology is based on:

- **Asana's "Anatomy of Work" Reports** for task completion rates and planning horizons
- **US Census Data** for demographic distributions
- **GitHub public issue trackers** for engineering task patterns
- **Asana Community Templates** for project structures
- **Industry benchmarks** for team sizes and sprint durations

For complete source citations, see [DOCUMENTATION.md](DOCUMENTATION.md).

## 🐛 Troubleshooting

### "emergentintegrations not found"

Make sure to install with the extra index URL:
```bash
pip install -r requirements.txt --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

### "LLM generation error"

Check that your API key is correctly set in `.env`:
```bash
echo $EMERGENT_LLM_KEY  # or check .env file
```

### Slow generation

LLM API calls are batched but still take time. You can:
- Reduce `NUM_PROJECTS` in `.env`
- Reduce task range in `main.py` (change `num_tasks_range=(20, 100)` to lower values)
- Use faster LLM models (already using gemini-3-flash which is fast)

## 📄 License

This project is created for the Emergent Research Scientist Internship take-home assignment.

## 👤 Author

**Assignment Submission**
- Created for: Emergent AI
- Purpose: Research Scientist Internship Take-Home Assignment
- Date: January 2025

## 🙏 Acknowledgments

- Emergent AI for the Emergent LLM Key and `emergentintegrations` library
- Asana for the project management domain
- Open source community for Python ecosystem
