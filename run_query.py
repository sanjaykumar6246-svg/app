#!/usr/bin/env python
"""Run SQL queries against the Asana simulation database."""
import sqlite3
import sys
from pathlib import Path
import argparse

def run_query(db_path, query_file=None, query_string=None):
    """Execute SQL query and display results."""
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return 1
    
    # Get query
    if query_file:
        with open(query_file, 'r') as f:
            query = f.read()
    elif query_string:
        query = query_string
    else:
        print("❌ No query provided. Use -f <file> or -q <query>")
        return 1
    
    # Execute
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Fetch results
        results = cursor.fetchall()
        
        if not results:
            print("✓ Query executed successfully (no results)")
            return 0
        
        # Get column names
        col_names = [desc[0] for desc in cursor.description]
        
        # Calculate column widths
        col_widths = [len(name) for name in col_names]
        for row in results:
            for i, val in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(val)))
        
        # Print header
        header = " | ".join(name.ljust(width) for name, width in zip(col_names, col_widths))
        print(header)
        print("-" * len(header))
        
        # Print rows
        for row in results:
            print(" | ".join(str(val).ljust(width) for val, width in zip(row, col_widths)))
        
        print(f"\n({len(results)} rows)")
        
        conn.close()
        return 0
        
    except Exception as e:
        print(f"❌ Query error: {e}")
        return 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run SQL queries against Asana simulation database')
    parser.add_argument('database', nargs='?', default='output/asana_simulation.sqlite', 
                       help='Path to SQLite database (default: output/asana_simulation.sqlite)')
    parser.add_argument('-f', '--file', help='SQL file to execute')
    parser.add_argument('-q', '--query', help='SQL query string to execute')
    parser.add_argument('-s', '--samples', action='store_true', help='Show sample queries')
    
    args = parser.parse_args()
    
    if args.samples:
        from sample_queries import SAMPLE_QUERIES
        print(SAMPLE_QUERIES)
        sys.exit(0)
    
    sys.exit(run_query(args.database, args.file, args.query))
