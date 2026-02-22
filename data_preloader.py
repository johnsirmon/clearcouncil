#!/usr/bin/env python3
"""
Data Preloader for ClearCouncil Chat

This script extracts voting data from the existing database and prepares it
for use in the chat interface to provide real council information.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
import re

class ClearCouncilDataPreloader:
    """Preloads voting data from the database for chat interface."""
    
    def __init__(self, db_path: str = "clearcouncil.db"):
        self.db_path = db_path
        self.conn = None
        self.data = {
            "representatives": {},
            "voting_records": [],
            "voting_summary": {},
            "case_categories": {},
            "districts": {},
            "recent_activity": [],
            "statistics": {}
        }
    
    def connect(self):
        """Connect to the database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
    
    def disconnect(self):
        """Disconnect from the database."""
        if self.conn:
            self.conn.close()
    
    def load_all_data(self):
        """Load all voting data from the database."""
        self.connect()
        
        print("🔄 Loading representatives data...")
        self.load_representatives()
        
        print("🔄 Loading voting records...")
        self.load_voting_records()
        
        print("🔄 Analyzing voting patterns...")
        self.analyze_voting_patterns()
        
        print("🔄 Generating statistics...")
        self.generate_statistics()
        
        self.disconnect()
        print("✅ Data loading complete!")
    
    def load_representatives(self):
        """Load representatives data."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT name, district, total_votes, motions_made, seconds_given
            FROM representatives 
            WHERE name IS NOT NULL
            ORDER BY total_votes DESC
        ''')
        
        for row in cursor.fetchall():
            name = row['name']
            district = row['district'] or 'Unknown'
            
            # Clean up district information
            if district == 'None':
                district = 'Unknown'
            
            self.data["representatives"][name] = {
                "name": name,
                "district": district,
                "total_votes": row['total_votes'] or 0,
                "motions_made": row['motions_made'] or 0,
                "seconds_given": row['seconds_given'] or 0,
                "voting_record": []
            }
    
    def load_voting_records(self):
        """Load voting records data."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT representative_name, district, case_number, vote_type, 
                   case_category, location, owner, applicant, zoning_request,
                   staff_recommendation, movant, second, ayes, nays, vote_result
            FROM voting_records 
            WHERE representative_name IS NOT NULL
            ORDER BY case_number
        ''')
        
        for row in cursor.fetchall():
            rep_name = row['representative_name']
            
            # Parse case information
            case_info = self.parse_case_number(row['case_number'])
            
            record = {
                "representative": rep_name,
                "district": row['district'] or 'Unknown',
                "case_number": row['case_number'],
                "vote_type": row['vote_type'],
                "case_category": row['case_category'] or 'other',
                "location": row['location'],
                "owner": row['owner'],
                "applicant": row['applicant'],
                "zoning_request": row['zoning_request'],
                "staff_recommendation": row['staff_recommendation'],
                "result": case_info['result'],
                "vote_result": row['vote_result'],
                "movant": row['movant'],
                "second": row['second'],
                "ayes": row['ayes'],
                "nays": row['nays']
            }
            
            self.data["voting_records"].append(record)
            
            # Add to representative's voting record
            if rep_name in self.data["representatives"]:
                self.data["representatives"][rep_name]["voting_record"].append(record)
    
    def parse_case_number(self, case_number: str) -> Dict[str, Any]:
        """Parse case number to extract result and other information."""
        if not case_number:
            return {"result": "unknown", "case_id": ""}
        
        # Extract result from case number (e.g., "vote_Name_APPROVED_123")
        if "_APPROVED" in case_number:
            result = "APPROVED"
        elif "_DENIED" in case_number:
            result = "DENIED"
        elif "_PASSED" in case_number:
            result = "PASSED"
        elif "_FAILED" in case_number:
            result = "FAILED"
        else:
            result = "unknown"
        
        # Extract case ID (usually the number at the end)
        case_id_match = re.search(r'_(\d+)$', case_number)
        case_id = case_id_match.group(1) if case_id_match else ""
        
        return {
            "result": result,
            "case_id": case_id,
            "is_unanimous": "[UNANIMOUS]" in case_number
        }
    
    def analyze_voting_patterns(self):
        """Analyze voting patterns and create summaries."""
        # Group by representative
        for rep_name, rep_data in self.data["representatives"].items():
            voting_record = rep_data["voting_record"]
            
            # Count vote types
            vote_counts = {
                "movant": 0,
                "second": 0,
                "for": 0,
                "against": 0,
                "abstain": 0
            }
            
            case_categories = defaultdict(int)
            results = defaultdict(int)
            
            for vote in voting_record:
                vote_type = vote["vote_type"]
                if vote_type in vote_counts:
                    vote_counts[vote_type] += 1
                
                case_categories[vote["case_category"]] += 1
                results[vote["result"]] += 1
            
            # Update representative data
            rep_data["vote_breakdown"] = vote_counts
            rep_data["case_categories"] = dict(case_categories)
            rep_data["results_participated"] = dict(results)
            
            # Calculate percentages
            total_votes = len(voting_record)
            if total_votes > 0:
                rep_data["activity_rate"] = {
                    "motions_percentage": (vote_counts["movant"] / total_votes) * 100,
                    "seconds_percentage": (vote_counts["second"] / total_votes) * 100,
                    "total_participation": total_votes
                }
        
        # Group by case category
        for record in self.data["voting_records"]:
            category = record["case_category"]
            if category not in self.data["case_categories"]:
                self.data["case_categories"][category] = {
                    "count": 0,
                    "representatives": set(),
                    "results": defaultdict(int)
                }
            
            self.data["case_categories"][category]["count"] += 1
            self.data["case_categories"][category]["representatives"].add(record["representative"])
            self.data["case_categories"][category]["results"][record["result"]] += 1
        
        # Convert sets to lists for JSON serialization
        for category_data in self.data["case_categories"].values():
            category_data["representatives"] = list(category_data["representatives"])
            category_data["results"] = dict(category_data["results"])
    
    def generate_statistics(self):
        """Generate overall statistics."""
        total_records = len(self.data["voting_records"])
        total_representatives = len(self.data["representatives"])
        
        # Most active representatives
        most_active = sorted(
            self.data["representatives"].items(),
            key=lambda x: x[1]["total_votes"],
            reverse=True
        )[:5]
        
        # Most common case categories
        most_common_categories = sorted(
            self.data["case_categories"].items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:5]
        
        # Overall results distribution
        results_distribution = defaultdict(int)
        for record in self.data["voting_records"]:
            results_distribution[record["result"]] += 1
        
        self.data["statistics"] = {
            "total_voting_records": total_records,
            "total_representatives": total_representatives,
            "most_active_representatives": [(name, data["total_votes"]) for name, data in most_active],
            "most_common_categories": [(cat, data["count"]) for cat, data in most_common_categories],
            "results_distribution": dict(results_distribution),
            "average_votes_per_representative": total_records / total_representatives if total_representatives > 0 else 0
        }
    
    def save_to_file(self, output_path: str = "clearcouncil_data.json"):
        """Save preloaded data to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)
        print(f"💾 Data saved to {output_path}")
    
    def get_representative_summary(self, name: str) -> Dict[str, Any]:
        """Get summary for a specific representative."""
        if name not in self.data["representatives"]:
            # Try fuzzy matching
            matches = []
            for rep_name in self.data["representatives"].keys():
                if name.lower() in rep_name.lower() or rep_name.lower() in name.lower():
                    matches.append(rep_name)
            
            if matches:
                name = matches[0]
            else:
                return {"error": f"Representative '{name}' not found"}
        
        return self.data["representatives"][name]
    
    def get_voting_summary(self) -> Dict[str, Any]:
        """Get overall voting summary."""
        return {
            "statistics": self.data["statistics"],
            "top_representatives": [(name, data["total_votes"]) 
                                   for name, data in sorted(self.data["representatives"].items(), 
                                                           key=lambda x: x[1]["total_votes"], 
                                                           reverse=True)[:10]],
            "case_categories": list(self.data["case_categories"].keys()),
            "total_records": len(self.data["voting_records"])
        }
    
    def search_voting_records(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search voting records by query."""
        query_lower = query.lower()
        matches = []
        
        for record in self.data["voting_records"]:
            # Search in representative name, case category, location, etc.
            searchable_fields = [
                record["representative"],
                record["case_category"],
                record["location"] or "",
                record["owner"] or "",
                record["applicant"] or "",
                record["zoning_request"] or ""
            ]
            
            if any(query_lower in field.lower() for field in searchable_fields if field):
                matches.append(record)
                
                if len(matches) >= limit:
                    break
        
        return matches

def main():
    """Main function to run the data preloader."""
    print("🏛️ ClearCouncil Data Preloader")
    print("=" * 50)
    
    preloader = ClearCouncilDataPreloader()
    preloader.load_all_data()
    
    # Print summary
    stats = preloader.data["statistics"]
    print(f"\n📊 Data Summary:")
    print(f"   Total voting records: {stats['total_voting_records']}")
    print(f"   Total representatives: {stats['total_representatives']}")
    print(f"   Average votes per rep: {stats['average_votes_per_representative']:.1f}")
    
    print(f"\n🏆 Most Active Representatives:")
    for name, votes in stats['most_active_representatives']:
        print(f"   {name}: {votes} votes")
    
    print(f"\n📋 Most Common Case Categories:")
    for category, count in stats['most_common_categories']:
        print(f"   {category}: {count} cases")
    
    # Save data
    preloader.save_to_file()
    
    print(f"\n✅ Data preloaded successfully!")
    print(f"   Use this data in the chat interface for real council information.")

if __name__ == "__main__":
    main()