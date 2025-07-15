"""Interactive chart generation using Plotly for web interface."""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import logging

from .database import DatabaseManager

logger = logging.getLogger(__name__)


class InteractiveChartGenerator:
    """Generates interactive charts using Plotly for the web interface."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize chart generator."""
        self.db = db_manager
        
        # Color schemes for different chart types
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff9500',
            'info': '#17a2b8',
            'categories': px.colors.qualitative.Set3,
            'representatives': px.colors.qualitative.Plotly
        }
    
    def create_representative_dashboard(self, rep_id: int, council_id: str, 
                                     start_date: datetime = None, 
                                     end_date: datetime = None) -> Dict[str, Any]:
        """Create a complete dashboard for a representative."""
        stats = self.db.get_representative_stats(rep_id, start_date, end_date)
        voting_records = self.db.get_voting_records(
            council_id, rep_id, start_date, end_date
        )
        
        # Get representative info
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM representatives WHERE id = ?', (rep_id,))
            rep_info = dict(cursor.fetchone())
        
        dashboard = {
            'representative': rep_info,
            'stats': stats,
            'charts': {
                'voting_overview': self.create_voting_overview_chart(stats),
                'category_breakdown': self.create_category_breakdown_chart(stats),
                'monthly_activity': self.create_monthly_activity_chart(stats['monthly_activity']),
                'voting_timeline': self.create_voting_timeline_chart(voting_records),
                'case_details': self.create_case_details_chart(voting_records)
            }
        }
        
        return dashboard
    
    def create_voting_overview_chart(self, stats: Dict) -> str:
        """Create an overview chart showing key voting metrics."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Total Votes', 'Motions Made', 'Seconds Given', 'Participation'),
            specs=[[{"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "pie"}]]
        )
        
        # Total votes indicator
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=stats.get('total_votes', 0),
                title={"text": "Total Votes"},
                number={'font': {'size': 24}},
                delta={'reference': 50, 'relative': True},
                domain={'row': 0, 'column': 0}
            ),
            row=1, col=1
        )
        
        # Motions made indicator
        fig.add_trace(
            go.Indicator(
                mode="number+gauge",
                value=stats.get('motions_made', 0),
                title={"text": "Motions Made"},
                gauge={'axis': {'range': [None, 20]},
                       'bar': {'color': self.color_scheme['success']},
                       'steps': [{'range': [0, 10], 'color': 'lightgray'},
                                {'range': [10, 20], 'color': 'gray'}]},
                domain={'row': 0, 'column': 1}
            ),
            row=1, col=2
        )
        
        # Seconds given indicator
        fig.add_trace(
            go.Indicator(
                mode="number+gauge",
                value=stats.get('seconds_given', 0),
                title={"text": "Seconds Given"},
                gauge={'axis': {'range': [None, 15]},
                       'bar': {'color': self.color_scheme['info']},
                       'steps': [{'range': [0, 7], 'color': 'lightgray'},
                                {'range': [7, 15], 'color': 'gray'}]},
                domain={'row': 1, 'column': 0}
            ),
            row=2, col=1
        )
        
        # Participation breakdown pie chart
        participation_data = {
            'Motions Made': stats.get('motions_made', 0),
            'Seconds Given': stats.get('seconds_given', 0),
            'Other Votes': stats.get('total_votes', 0) - stats.get('motions_made', 0) - stats.get('seconds_given', 0)
        }
        
        fig.add_trace(
            go.Pie(
                labels=list(participation_data.keys()),
                values=list(participation_data.values()),
                name="Participation",
                marker_colors=self.color_scheme['categories'][:3]
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=500,
            title_text="Representative Voting Overview",
            title_x=0.5,
            showlegend=True
        )
        
        return fig.to_json()
    
    def create_category_breakdown_chart(self, stats: Dict) -> str:
        """Create a breakdown chart by case category."""
        categories = {
            'Residential': stats.get('residential_votes', 0),
            'Commercial': stats.get('commercial_votes', 0),
            'Industrial': stats.get('industrial_votes', 0),
            'Other': stats.get('total_votes', 0) - sum([
                stats.get('residential_votes', 0),
                stats.get('commercial_votes', 0),
                stats.get('industrial_votes', 0)
            ])
        }
        
        # Filter out zero values
        categories = {k: v for k, v in categories.items() if v > 0}
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(categories.keys()),
                y=list(categories.values()),
                text=list(categories.values()),
                textposition='auto',
                marker_color=self.color_scheme['categories'][:len(categories)],
                hovertemplate='<b>%{x}</b><br>Votes: %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title='Votes by Category',
            xaxis_title='Category',
            yaxis_title='Number of Votes',
            height=400,
            showlegend=False
        )
        
        return fig.to_json()
    
    def create_monthly_activity_chart(self, monthly_data: Dict) -> str:
        """Create a monthly activity timeline chart."""
        if not monthly_data:
            # Create empty chart
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for the selected period",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title='Monthly Voting Activity',
                height=300,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            return fig.to_json()
        
        months = list(monthly_data.keys())
        votes = list(monthly_data.values())
        
        fig = go.Figure()
        
        # Add line chart
        fig.add_trace(
            go.Scatter(
                x=months,
                y=votes,
                mode='lines+markers',
                name='Votes',
                line=dict(color=self.color_scheme['primary'], width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>Votes: %{y}<extra></extra>'
            )
        )
        
        # Add area fill
        fig.add_trace(
            go.Scatter(
                x=months,
                y=votes,
                fill='tozeroy',
                mode='none',
                name='Area',
                fillcolor=f"rgba{tuple(list(px.colors.hex_to_rgb(self.color_scheme['primary'])) + [0.2])}",
                showlegend=False,
                hoverinfo='skip'
            )
        )
        
        fig.update_layout(
            title='Monthly Voting Activity',
            xaxis_title='Month',
            yaxis_title='Number of Votes',
            height=400,
            showlegend=False
        )
        
        return fig.to_json()
    
    def create_voting_timeline_chart(self, voting_records: List[Dict]) -> str:
        """Create a timeline chart showing voting activity over time."""
        if not voting_records:
            return self._create_empty_chart("No voting records available")
        
        # Process data
        df = pd.DataFrame(voting_records)
        df['meeting_date'] = pd.to_datetime(df['meeting_date'])
        df['month'] = df['meeting_date'].dt.to_period('M')
        
        # Group by month and category
        monthly_category = df.groupby(['month', 'case_category']).size().reset_index(name='count')
        
        fig = go.Figure()
        
        # Add traces for each category
        categories = monthly_category['case_category'].unique()
        for i, category in enumerate(categories):
            category_data = monthly_category[monthly_category['case_category'] == category]
            
            fig.add_trace(
                go.Scatter(
                    x=[str(month) for month in category_data['month']],
                    y=category_data['count'],
                    mode='lines+markers',
                    name=category,
                    line=dict(color=self.color_scheme['categories'][i % len(self.color_scheme['categories'])]),
                    stackgroup='one',
                    hovertemplate=f'<b>{category}</b><br>Month: %{{x}}<br>Votes: %{{y}}<extra></extra>'
                )
            )
        
        fig.update_layout(
            title='Voting Activity Timeline by Category',
            xaxis_title='Month',
            yaxis_title='Number of Votes',
            height=400,
            hovermode='x unified'
        )
        
        return fig.to_json()
    
    def create_case_details_chart(self, voting_records: List[Dict]) -> str:
        """Create a detailed chart showing case information."""
        if not voting_records:
            return self._create_empty_chart("No voting records available")
        
        # Process data for scatter plot
        df = pd.DataFrame(voting_records)
        df['meeting_date'] = pd.to_datetime(df['meeting_date'])
        df['acres'] = pd.to_numeric(df['acres'], errors='coerce')
        
        # Filter out records without acres data
        df_with_acres = df[df['acres'].notna() & (df['acres'] > 0)]
        
        if df_with_acres.empty:
            return self._create_empty_chart("No case details with area data available")
        
        fig = px.scatter(
            df_with_acres,
            x='meeting_date',
            y='acres',
            color='case_category',
            size='acres',
            hover_data=['case_number', 'location', 'applicant'],
            title='Case Details: Area vs Time',
            labels={'acres': 'Area (acres)', 'meeting_date': 'Meeting Date'}
        )
        
        fig.update_layout(
            height=400,
            hovermode='closest'
        )
        
        return fig.to_json()
    
    def create_comparison_chart(self, rep_ids: List[int], council_id: str,
                              start_date: datetime = None, end_date: datetime = None) -> str:
        """Create a comparison chart between multiple representatives."""
        comparison_data = []
        
        for rep_id in rep_ids:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT name, district FROM representatives WHERE id = ?', (rep_id,))
                rep_info = dict(cursor.fetchone())
            
            stats = self.db.get_representative_stats(rep_id, start_date, end_date)
            
            comparison_data.append({
                'name': rep_info['name'],
                'district': rep_info['district'],
                'total_votes': stats.get('total_votes', 0),
                'motions_made': stats.get('motions_made', 0),
                'seconds_given': stats.get('seconds_given', 0),
                'residential_votes': stats.get('residential_votes', 0),
                'commercial_votes': stats.get('commercial_votes', 0),
                'industrial_votes': stats.get('industrial_votes', 0)
            })
        
        df = pd.DataFrame(comparison_data)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Total Votes', 'Motions Made', 'Seconds Given', 'Vote Categories'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Total votes comparison
        fig.add_trace(
            go.Bar(
                x=df['name'],
                y=df['total_votes'],
                name='Total Votes',
                marker_color=self.color_scheme['primary'],
                text=df['total_votes'],
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # Motions made comparison
        fig.add_trace(
            go.Bar(
                x=df['name'],
                y=df['motions_made'],
                name='Motions Made',
                marker_color=self.color_scheme['success'],
                text=df['motions_made'],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        # Seconds given comparison
        fig.add_trace(
            go.Bar(
                x=df['name'],
                y=df['seconds_given'],
                name='Seconds Given',
                marker_color=self.color_scheme['info'],
                text=df['seconds_given'],
                textposition='auto'
            ),
            row=2, col=1
        )
        
        # Stacked bar for vote categories
        fig.add_trace(
            go.Bar(
                x=df['name'],
                y=df['residential_votes'],
                name='Residential',
                marker_color=self.color_scheme['categories'][0]
            ),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Bar(
                x=df['name'],
                y=df['commercial_votes'],
                name='Commercial',
                marker_color=self.color_scheme['categories'][1]
            ),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Bar(
                x=df['name'],
                y=df['industrial_votes'],
                name='Industrial',
                marker_color=self.color_scheme['categories'][2]
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            title_text="Representative Comparison",
            title_x=0.5,
            showlegend=True,
            barmode='stack'
        )
        
        return fig.to_json()
    
    def create_council_overview_chart(self, council_id: str) -> str:
        """Create an overview chart for the entire council."""
        representatives = self.db.get_representatives(council_id)
        
        if not representatives:
            return self._create_empty_chart("No representatives found")
        
        # Get stats for each representative
        rep_data = []
        for rep in representatives:
            stats = self.db.get_representative_stats(rep['id'])
            rep_data.append({
                'name': rep['name'],
                'district': rep['district'],
                'total_votes': stats.get('total_votes', 0),
                'motions_made': stats.get('motions_made', 0),
                'seconds_given': stats.get('seconds_given', 0)
            })
        
        df = pd.DataFrame(rep_data)
        
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Total Votes', 'Motions Made', 'Seconds Given'),
            specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
        )
        
        # Total votes
        fig.add_trace(
            go.Bar(
                x=df['name'],
                y=df['total_votes'],
                name='Total Votes',
                marker_color=self.color_scheme['primary'],
                text=df['total_votes'],
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # Motions made
        fig.add_trace(
            go.Bar(
                x=df['name'],
                y=df['motions_made'],
                name='Motions Made',
                marker_color=self.color_scheme['success'],
                text=df['motions_made'],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        # Seconds given
        fig.add_trace(
            go.Bar(
                x=df['name'],
                y=df['seconds_given'],
                name='Seconds Given',
                marker_color=self.color_scheme['info'],
                text=df['seconds_given'],
                textposition='auto'
            ),
            row=1, col=3
        )
        
        fig.update_layout(
            height=400,
            title_text="Council Overview",
            title_x=0.5,
            showlegend=False
        )
        
        # Update x-axis labels to show district info
        for i in range(1, 4):
            fig.update_xaxes(
                tickangle=45,
                ticktext=[f"{name}<br>({district})" for name, district in zip(df['name'], df['district'])],
                tickvals=df['name'],
                row=1, col=i
            )
        
        return fig.to_json()
    
    def _create_empty_chart(self, message: str) -> str:
        """Create an empty chart with a message."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            height=300,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig.to_json()