import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import networkx as nx

class MoodleVisualizer:
    def __init__(self, theme='plotly_white'):
        self.theme = theme
        self.color_palette = px.colors.qualitative.Set3
    
    def create_engagement_dashboard(self, engagement_data):
        """Create comprehensive engagement dashboard"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Weekly Activity Pattern', 'Daily Activity Heatmap',
                          'Engagement Score Distribution', 'Top Active Courses'),
            specs=[[{'type': 'scatter'}, {'type': 'heatmap'}],
                   [{'type': 'histogram'}, {'type': 'bar'}]]
        )
        
        # Weekly pattern
        weekly_data = engagement_data.groupby('day_of_week').size().reindex([
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        ])
        
        fig.add_trace(
            go.Scatter(x=weekly_data.index, y=weekly_data.values,
                      mode='lines+markers', name='Weekly Activity'),
            row=1, col=1
        )
        
        # Daily heatmap
        hourly_data = engagement_data.groupby(['day_of_week', 'hour']).size().unstack()
        fig.add_trace(
            go.Heatmap(z=hourly_data.values,
                      x=hourly_data.columns,
                      y=hourly_data.index,
                      colorscale='Viridis'),
            row=1, col=2
        )
        
        # Engagement distribution
        fig.add_trace(
            go.Histogram(x=engagement_data['total_actions'],
                        nbinsx=50, name='Actions Distribution'),
            row=2, col=1
        )
        
        # Top courses
        top_courses = engagement_data.groupby('course_name')['total_actions'].sum().nlargest(10)
        fig.add_trace(
            go.Bar(x=top_courses.index, y=top_courses.values, name='Top Courses'),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=False, template=self.theme)
        return fig
    
    def create_student_cluster_visualization(self, cluster_results):
        """Visualize student clusters"""
        profiles = cluster_results['profiles']
        
        fig = go.Figure()
        
        for cluster_idx in profiles.index:
            fig.add_trace(go.Scatterpolar(
                r=profiles.loc[cluster_idx].values,
                theta=profiles.columns,
                fill='toself',
                name=f'Cluster {cluster_idx}'
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            showlegend=True,
            title="Student Behavior Clusters",
            template=self.theme
        )
        
        return fig
    
    def create_risk_analysis_chart(self, at_risk_data):
        """Create risk analysis visualization"""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Students at Risk by Course', 'Risk Level Distribution'),
            specs=[[{'type': 'bar'}, {'type': 'pie'}]]
        )
        
        # Risk by course
        risk_by_course = at_risk_data.groupby(['course_name', 'risk_level']).size().unstack()
        for risk_level in risk_by_course.columns:
            fig.add_trace(
                go.Bar(x=risk_by_course.index, y=risk_by_course[risk_level],
                      name=risk_level),
                row=1, col=1
            )
        
        # Risk distribution
        risk_dist = at_risk_data['risk_level'].value_counts()
        fig.add_trace(
            go.Pie(labels=risk_dist.index, values=risk_dist.values,
                  hole=0.4, name='Risk Distribution'),
            row=1, col=2
        )
        
        fig.update_layout(height=500, template=self.theme)
        return fig
    
    def create_forum_network_graph(self, network_results):
        """Visualize forum interaction network"""
        G = network_results['graph']
        
        # Create network graph
        pos = nx.spring_layout(G, seed=42)
        
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"User: {G.nodes[node].get('username', node)}")
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                )
            )
        )
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='Forum Interaction Network',
                           showlegend=False,
                           hovermode='closest',
                           template=self.theme
                       ))
        
        return fig
    
    def create_quiz_performance_chart(self, quiz_data):
        """Visualize quiz performance"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Score Distribution', 'Attempts vs Scores',
                          'Time Spent Distribution', 'Score Improvement by Attempt'),
            specs=[[{'type': 'histogram'}, {'type': 'scatter'}],
                   [{'type': 'box'}, {'type': 'line'}]]
        )
        
        # Score distribution
        fig.add_trace(
            go.Histogram(x=quiz_data['final_grade'], nbinsx=30, name='Scores'),
            row=1, col=1
        )
        
        # Attempts vs scores
        fig.add_trace(
            go.Scatter(x=quiz_data['attempt_number'], y=quiz_data['final_grade'],
                      mode='markers', name='Attempts vs Scores'),
            row=1, col=2
        )
        
        # Time spent
        fig.add_trace(
            go.Box(y=quiz_data['duration_minutes'], name='Time Spent'),
            row=2, col=1
        )
        
        # Score improvement
        if 'is_first_attempt' in quiz_data.columns and 'is_last_attempt' in quiz_data.columns:
            improvement_data = quiz_data.groupby('userid').apply(
                lambda x: x[x['is_last_attempt']]['final_grade'].values[0] - 
                         x[x['is_first_attempt']]['final_grade'].values[0] 
                if not x[x['is_last_attempt']].empty and not x[x['is_first_attempt']].empty else 0
            )
            fig.add_trace(
                go.Histogram(x=improvement_data, name='Score Improvement'),
                row=2, col=2
            )
        
        fig.update_layout(height=700, showlegend=False, template=self.theme)
        return fig