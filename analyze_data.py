#!/usr/bin/env python3
import sqlite3
import json

def analyze_database():
    conn = sqlite3.connect('clearcouncil.db')
    cursor = conn.cursor()
    
    print("=== DATABASE ANALYSIS ===")
    
    print("\n0. Table Structures:")
    cursor.execute('PRAGMA table_info(voting_records)')
    print("  voting_records columns:")
    for row in cursor.fetchall():
        print(f"    {row[1]} ({row[2]})")
    
    print("\n1. Top 5 Representatives by Vote Count:")
    cursor.execute('SELECT name, district, total_votes FROM representatives ORDER BY total_votes DESC LIMIT 5')
    for row in cursor.fetchall():
        print(f"  {row[0]} ({row[1]}): {row[2]} votes")
    
    print("\n2. Available Case Categories:")
    cursor.execute('SELECT DISTINCT case_category FROM voting_records WHERE case_category IS NOT NULL LIMIT 10')
    for row in cursor.fetchall():
        print(f"  - {row[0]}")
    
    print("\n3. Vote Types:")
    cursor.execute('SELECT DISTINCT vote_type FROM voting_records WHERE vote_type IS NOT NULL LIMIT 10')
    for row in cursor.fetchall():
        print(f"  - {row[0]}")
    
    print("\n4. Recent Voting Records (sample):")
    cursor.execute('SELECT * FROM voting_records LIMIT 3')
    columns = [desc[0] for desc in cursor.description]
    print(f"  Columns: {', '.join(columns)}")
    for row in cursor.fetchall():
        print(f"  {dict(zip(columns, row))}")
    
    print("\n5. Districts:")
    cursor.execute('SELECT DISTINCT district FROM representatives WHERE district IS NOT NULL')
    for row in cursor.fetchall():
        print(f"  - {row[0]}")
    
    conn.close()

if __name__ == "__main__":
    analyze_database()