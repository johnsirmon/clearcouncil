"""Chart generation for voting analysis visualizations."""

import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import logging

from ..config.settings import CouncilConfig

logger = logging.getLogger(__name__)

# Set a clean style for charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class VotingChartGenerator:
    """Generates various charts for voting analysis."""
    
    def __init__(self, config: CouncilConfig):
        self.config = config
        self.output_dir = config.get_data_path("results") / "charts"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_representative_summary_chart(self, analysis_data: Dict, save_path: Optional[Path] = None) -> Path:
        """Create a summary chart for a representative's voting activity."""
        rep_data = analysis_data['representative']
        voting_breakdown = analysis_data['voting_breakdown']
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f"Voting Summary: {rep_data['name']} ({rep_data['district']})", fontsize=16, fontweight='bold')
        
        # 1. Vote Type Breakdown (Pie Chart)
        vote_types = ['motions_made', 'seconds_given', 'votes_for', 'votes_against', 'abstentions']
        vote_counts = [voting_breakdown.get(vt, 0) for vt in vote_types]
        vote_labels = ['Motions Made', 'Seconds Given', 'Votes For', 'Votes Against', 'Abstentions']
        
        # Only show non-zero values
        non_zero_data = [(label, count) for label, count in zip(vote_labels, vote_counts) if count > 0]
        if non_zero_data:
            labels, counts = zip(*non_zero_data)
            ax1.pie(counts, labels=labels, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Vote Type Distribution')
        
        # 2. Category Breakdown (Bar Chart)
        categories = analysis_data.get('case_categories', {})
        if categories:
            cat_names = list(categories.keys())
            cat_counts = list(categories.values())
            
            bars = ax2.bar(cat_names, cat_counts)
            ax2.set_title('Votes by Category')
            ax2.set_ylabel('Number of Votes')
            ax2.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom')
        
        # 3. Activity Over Time (if we have detailed votes with dates)
        detailed_votes = analysis_data.get('detailed_votes', [])
        if detailed_votes:
            # Group votes by month
            vote_dates = [vote['date'] for vote in detailed_votes if vote['date'] != 'Unknown']
            if vote_dates:
                df = pd.DataFrame({'date': pd.to_datetime(vote_dates)})
                monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
                
                monthly_counts.plot(kind='line', ax=ax3, marker='o')
                ax3.set_title('Voting Activity Over Time')
                ax3.set_ylabel('Number of Votes')
                ax3.tick_params(axis='x', rotation=45)
        
        # 4. Participation Metrics
        metrics = {
            'Total Votes': rep_data['total_votes_in_period'],
            'Motions Made': rep_data['motions_made'],
            'Seconds Given': rep_data['seconds_given'],
            'Participation Rate': f"{rep_data.get('participation_rate', 0)*100:.1f}%"
        }
        
        ax4.axis('off')
        metrics_text = '\n'.join([f"{key}: {value}" for key, value in metrics.items()])
        ax4.text(0.1, 0.9, metrics_text, transform=ax4.transAxes, fontsize=12,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        ax4.set_title('Key Metrics')
        
        plt.tight_layout()
        
        # Save chart
        if save_path is None:
            save_path = self.output_dir / f"{rep_data['name'].replace(' ', '_')}_summary.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Created representative summary chart: {save_path}")
        return save_path
    
    def create_comparison_chart(self, analysis_data: Dict, save_path: Optional[Path] = None) -> Path:
        """Create a comparison chart between representatives."""
        target_rep = analysis_data['representative']
        comparison_data = analysis_data.get('comparison', {})
        
        if not comparison_data or not comparison_data.get('compared_with'):
            raise ValueError("No comparison data available")
        
        # Prepare data for comparison
        rep_names = [target_rep['name']]
        rep_votes = [target_rep['total_votes_in_period']]
        rep_motions = [target_rep['motions_made']]
        rep_seconds = [target_rep['seconds_given']]
        
        for comp_rep in comparison_data['compared_with']:
            rep_names.append(comp_rep['name'])
            rep_votes.append(comp_rep['votes_in_period'])
            rep_motions.append(comp_rep['motions_made'])
            rep_seconds.append(comp_rep.get('seconds_given', 0))
        
        # Create comparison chart
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Representative Comparison', fontsize=16, fontweight='bold')
        
        x_pos = np.arange(len(rep_names))
        
        # Total votes comparison
        bars1 = ax1.bar(x_pos, rep_votes, color=['red'] + ['blue'] * (len(rep_names) - 1))
        ax1.set_title('Total Votes in Period')
        ax1.set_ylabel('Number of Votes')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(rep_names, rotation=45, ha='right')
        
        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        # Motions made comparison
        bars2 = ax2.bar(x_pos, rep_motions, color=['red'] + ['blue'] * (len(rep_names) - 1))
        ax2.set_title('Motions Made')
        ax2.set_ylabel('Number of Motions')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(rep_names, rotation=45, ha='right')
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        # Seconds given comparison
        bars3 = ax3.bar(x_pos, rep_seconds, color=['red'] + ['blue'] * (len(rep_names) - 1))
        ax3.set_title('Seconds Given')
        ax3.set_ylabel('Number of Seconds')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(rep_names, rotation=45, ha='right')
        
        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Save chart
        if save_path is None:
            save_path = self.output_dir / f"comparison_{target_rep['name'].replace(' ', '_')}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Created comparison chart: {save_path}")
        return save_path
    
    def create_district_overview_chart(self, district_data: Dict, save_path: Optional[Path] = None) -> Path:
        """Create an overview chart for all representatives in a district."""
        district = district_data['district']
        representatives = district_data['representatives']
        
        if not representatives:
            raise ValueError("No representative data available")
        
        # Prepare data
        rep_names = [rep['name'] for rep in representatives]
        vote_counts = [rep['votes_in_period'] for rep in representatives]
        motion_counts = [rep['motions_made'] for rep in representatives]
        
        # Create chart
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle(f'District {district} Overview', fontsize=16, fontweight='bold')
        
        x_pos = np.arange(len(rep_names))
        
        # Votes comparison
        bars1 = ax1.bar(x_pos, vote_counts)
        ax1.set_title('Total Votes by Representative')
        ax1.set_ylabel('Number of Votes')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(rep_names, rotation=45, ha='right')
        
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        # Motions comparison
        bars2 = ax2.bar(x_pos, motion_counts)
        ax2.set_title('Motions Made by Representative')
        ax2.set_ylabel('Number of Motions')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(rep_names, rotation=45, ha='right')
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Save chart
        if save_path is None:
            save_path = self.output_dir / f"district_{district}_overview.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Created district overview chart: {save_path}")
        return save_path
    
    def create_timeline_chart(self, detailed_votes: List[Dict], save_path: Optional[Path] = None) -> Path:
        """Create a timeline chart showing voting activity over time."""
        if not detailed_votes:
            raise ValueError("No detailed vote data available")
        
        # Filter out votes without dates and convert to datetime
        votes_with_dates = [
            vote for vote in detailed_votes 
            if vote['date'] != 'Unknown'
        ]
        
        if not votes_with_dates:
            raise ValueError("No votes with valid dates found")
        
        # Create DataFrame for easier manipulation
        df = pd.DataFrame(votes_with_dates)
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')
        
        # Group by month and category
        monthly_activity = df.groupby(['month', 'category']).size().unstack(fill_value=0)
        
        # Create chart
        fig, ax = plt.subplots(figsize=(14, 8))
        
        monthly_activity.plot(kind='bar', stacked=True, ax=ax, width=0.8)
        
        ax.set_title('Voting Activity Timeline by Category')
        ax.set_xlabel('Month')
        ax.set_ylabel('Number of Votes')
        ax.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save chart
        if save_path is None:
            save_path = self.output_dir / "voting_timeline.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Created timeline chart: {save_path}")
        return save_path