"""
Sample visualization utilities for Moodle Analytics
Provides visualization functions for sample datasets.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from typing import Dict, List, Optional, Tuple

class SampleVisualizer:
    """Sample data visualizer for demonstration purposes"""
    
    def __init__(self, theme='plotly_white'):
        self.theme = theme
        self.color_palette = px.colors.qualitative.Set3
        
    def create_sample_engagement_dashboard(self, engagement_df):
        """Create sample engagement dashboard visualizations"""
        # Engagement trends over time
        fig_trends = px.line(
            engagement_df.groupby('date')['engagement_score'].mean().reset_index(),
            x='date', 
            y='engagement_score',
            title='Average Engagement Score Over Time',
            template=self.theme
        )
        fig_trends.update_traces(line_color=self.color_palette[0])
        
        # Engagement distribution
        fig_dist = px.histogram(
            engagement_df,
            x='engagement_score',
            title='Engagement Score Distribution',
            nbins=30,
            template=self.theme
        )
        fig_dist.update_traces(marker_color=self.color_palette[1])
        
        # Course comparison
        course_engagement = engagement_df.groupby('courseid')['engagement_score'].mean().reset_index()
        fig_course = px.bar(
            course_engagement,
            x='courseid',
            y='engagement_score',
            title='Average Engagement by Course',
            template=self.theme
        )
        fig_course.update_traces(marker_color=self.color_palette[2])
        
        return {
            'engagement_trends': fig_trends,
            'engagement_distribution': fig_dist,
            'course_engagement': fig_course
        }
    
    def create_sample_student_clusters(self, student_profiles_df):
        """Create sample student clustering visualization"""
        if student_profiles_df.empty:
            return None
            
        # Create synthetic clusters based on activity and performance
        df = student_profiles_df.copy()
        
        # Fill missing values with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df[col].fillna(df[col].median(), inplace=True)
        
        # Create synthetic clusters (k-means like grouping)
        if 'total_actions' in df.columns and 'avg_quiz_score' in df.columns:
            # Normalize features
            df['actions_norm'] = (df['total_actions'] - df['total_actions'].min()) / (df['total_actions'].max() - df['total_actions'].min())
            df['score_norm'] = (df['avg_quiz_score'] - df['avg_quiz_score'].min()) / (df['avg_quiz_score'].max() - df['avg_quiz_score'].min())
            
            # Create 4 synthetic clusters
            df['cluster'] = 0
            df.loc[(df['actions_norm'] > 0.5) & (df['score_norm'] > 0.5), 'cluster'] = 0  # High activity, high score
            df.loc[(df['actions_norm'] > 0.5) & (df['score_norm'] <= 0.5), 'cluster'] = 1  # High activity, low score
            df.loc[(df['actions_norm'] <= 0.5) & (df['score_norm'] > 0.5), 'cluster'] = 2  # Low activity, high score
            df.loc[(df['actions_norm'] <= 0.5) & (df['score_norm'] <= 0.5), 'cluster'] = 3  # Low activity, low score
            
            cluster_labels = {
                0: 'High Achievers',
                1: 'Struggling Engagers',
                2: 'Quiet Achievers', 
                3: 'At Risk Students'
            }
            
            fig = px.scatter(
                df,
                x='actions_norm',
                y='score_norm',
                color='cluster',
                hover_data=['userid'] if 'userid' in df.columns else None,
                title='Student Clusters Based on Activity and Performance',
                template=self.theme,
                color_discrete_sequence=self.color_palette
            )
            
            fig.update_traces(marker_size=10)
            fig.update_layout(
                xaxis_title='Normalized Activity Level',
                yaxis_title='Normalized Quiz Score',
                coloraxis_colorbar=dict(title='Cluster Type')
            )
            
            return fig, cluster_labels
        
        return None
    
    def create_sample_risk_analysis_chart(self, risk_df):
        """Create sample risk analysis visualizations"""
        if risk_df.empty:
            return None
            
        # Risk level distribution
        risk_counts = risk_df['risk_level'].value_counts().reset_index()
        fig_pie = px.pie(
            risk_counts,
            values='count',
            names='risk_level',
            title='Student Risk Level Distribution',
            template=self.theme,
            color_discrete_sequence=self.color_palette
        )
        
        # Engagement vs Risk scatter plot
        fig_scatter = px.scatter(
            risk_df,
            x='engagement_score',
            y='engagement_percentile',
            color='risk_level',
            title='Engagement Score vs Percentile by Risk Level',
            template=self.theme,
            color_discrete_sequence=self.color_palette
        )
        
        # Risk by course
        course_risk = risk_df.groupby(['courseid', 'risk_level']).size().reset_index(name='count')
        fig_bar = px.bar(
            course_risk,
            x='courseid',
            y='count',
            color='risk_level',
            title='Risk Distribution by Course',
            template=self.theme,
            color_discrete_sequence=self.color_palette
        )
        
        return {
            'risk_distribution': fig_pie,
            'engagement_risk_scatter': fig_scatter,
            'course_risk': fig_bar
        }
    
    def create_sample_forum_network_graph(self, forum_df):
        """Create sample forum interaction network graph"""
        if forum_df.empty:
            return None
            
        # Create network graph
        G = nx.Graph()
        
        # Add nodes (users)
        users = forum_df['userid'].unique()
        for user in users:
            G.add_node(user, label=f"User {user}")
        
        # Add edges based on replies
        for _, row in forum_df.iterrows():
            if row['is_reply'] and row['parent'] > 0:
                # Find parent post author
                parent_post = forum_df[forum_df['id'] == row['parent']]
                if not parent_post.empty:
                    parent_user = parent_post.iloc[0]['userid']
                    if parent_user != row['userid']:  # Don't connect user to themselves
                        G.add_edge(row['userid'], parent_user)
        
        # Calculate layout
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_sizes = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"User {node}")
            node_sizes.append(G.degree(node) * 3 + 5)  # Size based on connections
        
        # Create edge trace
        edge_x = []
        edge_y = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Create figure
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines',
            name='Connections'
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                size=node_sizes,
                color=node_sizes,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Connections")
            ),
            name='Users'
        ))
        
        fig.update_layout(
            title='Forum Interaction Network',
            titlefont_size=16,
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Node size represents number of connections",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color="#888", size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            template=self.theme
        )
        
        return fig
    
    def create_sample_quiz_performance_chart(self, quiz_df):
        """Create sample quiz performance visualizations"""
        if quiz_df.empty:
            return None
            
        # Score distribution
        fig_hist = px.histogram(
            quiz_df,
            x='final_grade',
            title='Quiz Score Distribution',
            nbins=20,
            template=self.theme
        )
        fig_hist.update_traces(marker_color=self.color_palette[0])
        
        # Performance by quiz
        quiz_performance = quiz_df.groupby('quiz')['final_grade'].agg(['mean', 'std']).reset_index()
        fig_box = px.box(
            quiz_df,
            x='quiz',
            y='final_grade',
            title='Quiz Performance by Quiz Type',
            template=self.theme
        )
        fig_box.update_traces(marker_color=self.color_palette[1])
        
        # Attempt patterns
        attempt_stats = quiz_df.groupby('attempt_number')['final_grade'].mean().reset_index()
        fig_attempts = px.line(
            attempt_stats,
            x='attempt_number',
            y='final_grade',
            title='Average Score by Attempt Number',
            markers=True,
            template=self.theme
        )
        fig_attempts.update_traces(line_color=self.color_palette[2], marker=dict(size=8))
        
        return {
            'score_distribution': fig_hist,
            'quiz_performance': fig_box,
            'attempt_patterns': fig_attempts
        }
    
    def create_sample_activity_heatmap(self, logs_df):
        """Create sample activity heatmap"""
        if logs_df.empty:
            return None
            
        # Create hour vs day of week heatmap
        activity_by_hour_day = logs_df.groupby(['day_of_week', 'hour']).size().reset_index(name='activity_count')
        
        # Sort days properly
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        activity_by_hour_day['day_of_week'] = pd.Categorical(
            activity_by_hour_day['day_of_week'], 
            categories=day_order, 
            ordered=True
        )
        
        # Pivot for heatmap
        heatmap_data = activity_by_hour_day.pivot(
            index='day_of_week', 
            columns='hour', 
            values='activity_count'
        ).fillna(0)
        
        fig = px.imshow(
            heatmap_data,
            labels=dict(x="Hour of Day", y="Day of Week", color="Activity Count"),
            x=heatmap_data.columns,
            y=heatmap_data.index,
            title='Activity Heatmap by Day and Hour',
            template=self.theme,
            color_continuous_scale='Viridis'
        )
        
        return fig
    
    def create_sample_course_comparison(self, course_analytics_df):
        """Create sample course comparison visualization"""
        if course_analytics_df.empty:
            return None
            
        # Create subplots for multiple metrics
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Unique Students', 'Total Actions', 'Submissions', 'Activity Span'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Add traces
        fig.add_trace(
            go.Bar(x=course_analytics_df.index, y=course_analytics_df['unique_students'],
                  marker_color=self.color_palette[0], name='Students'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=course_analytics_df.index, y=course_analytics_df['total_actions'],
                  marker_color=self.color_palette[1], name='Actions'),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Bar(x=course_analytics_df.index, y=course_analytics_df['total_submissions'],
                  marker_color=self.color_palette[2], name='Submissions'),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Bar(x=course_analytics_df.index, y=course_analytics_df['activity_span_days'],
                  marker_color=self.color_palette[3], name='Days'),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text='Course Comparison Dashboard',
            showlegend=False,
            template=self.theme
        )
        
        return fig

# Export the sample visualizer
__all__ = ['SampleVisualizer']