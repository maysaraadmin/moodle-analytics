import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class MoodleAnalytics:
    def __init__(self):
        self.scaler = StandardScaler()
        
    def calculate_student_engagement_scores(self, engagement_data):
        """Calculate comprehensive engagement scores"""
        scores = engagement_data.groupby(['userid', 'courseid']).agg({
            'total_actions': ['sum', 'mean', 'std'],
            'submissions': 'sum',
            'active_minutes': 'sum'
        }).reset_index()
        
        scores.columns = ['userid', 'courseid', 'total_actions', 'avg_actions', 
                         'std_actions', 'total_submissions', 'total_active_minutes']
        
        # Calculate engagement score (weighted formula)
        scores['engagement_score'] = (
            scores['total_actions'] * 0.3 +
            scores['total_submissions'] * 0.4 +
            scores['total_active_minutes'] * 0.3
        )
        
        # Normalize scores 0-100
        scores['engagement_score_normalized'] = (
            (scores['engagement_score'] - scores['engagement_score'].min()) /
            (scores['engagement_score'].max() - scores['engagement_score'].min())
        ) * 100
        
        return scores
    
    def identify_at_risk_students(self, engagement_scores, quiz_grades=None, threshold=30):
        """Identify students at risk based on engagement and grades"""
        at_risk = engagement_scores[
            engagement_scores['engagement_score_normalized'] < threshold
        ].copy()
        
        at_risk['risk_level'] = pd.cut(
            at_risk['engagement_score_normalized'],
            bins=[0, 15, 30, 100],
            labels=['High Risk', 'Medium Risk', 'Low Risk']
        )
        
        if quiz_grades is not None:
            at_risk = at_risk.merge(
                quiz_grades[['userid', 'courseid', 'final_grade']],
                on=['userid', 'courseid'],
                how='left'
            )
            at_risk['grade_based_risk'] = at_risk['final_grade'].apply(
                lambda x: 'High Risk' if x < 50 else ('Medium Risk' if x < 70 else 'Low Risk')
            )
        
        return at_risk
    
    def analyze_course_activity_patterns(self, log_data):
        """Analyze temporal patterns in course activity"""
        patterns = {}
        
        # Daily patterns
        patterns['hourly_activity'] = log_data.groupby('hour').size()
        patterns['daily_activity'] = log_data.groupby('day_of_week').size()
        
        # Weekly patterns (if data spans multiple weeks)
        log_data['week_number'] = log_data['time_created'].dt.isocalendar().week
        patterns['weekly_activity'] = log_data.groupby('week_number').size()
        
        # Activity by course component
        patterns['component_activity'] = log_data.groupby('component').size().sort_values(ascending=False)
        
        return patterns
    
    def cluster_students_by_behavior(self, engagement_data, n_clusters=4):
        """Cluster students based on their engagement patterns"""
        features = engagement_data.pivot_table(
            index='userid',
            columns='day_of_week',
            values='total_actions',
            aggfunc='sum',
            fill_value=0
        )
        
        # Add additional features
        features_scaled = self.scaler.fit_transform(features)
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        features['cluster'] = kmeans.fit_predict(features_scaled)
        
        # Analyze cluster characteristics
        cluster_profiles = features.groupby('cluster').mean()
        
        return {
            'clusters': features['cluster'],
            'profiles': cluster_profiles,
            'model': kmeans
        }
    
    def analyze_forum_interaction_network(self, forum_data):
        """Build and analyze forum interaction network"""
        import networkx as nx
        
        G = nx.DiGraph()
        
        # Add nodes (users)
        users = forum_data[['userid', 'username']].drop_duplicates()
        for _, row in users.iterrows():
            G.add_node(row['userid'], username=row['username'])
        
        # Add edges (replies)
        for _, row in forum_data.iterrows():
            if row['is_reply'] and row['parent'] > 0:
                parent_post = forum_data[forum_data['id'] == row['parent']]
                if not parent_post.empty:
                    parent_user = parent_post.iloc[0]['userid']
                    G.add_edge(row['userid'], parent_user)
        
        # Calculate network metrics
        metrics = {
            'num_nodes': G.number_of_nodes(),
            'num_edges': G.number_of_edges(),
            'density': nx.density(G),
            'average_clustering': nx.average_clustering(G.to_undirected()),
            'degree_centrality': nx.degree_centrality(G),
            'betweenness_centrality': nx.betweenness_centrality(G)
        }
        
        return {'graph': G, 'metrics': metrics}
    
    def predict_course_completion(self, features, target):
        """Predict course completion using machine learning"""
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import classification_report, accuracy_score
        
        X = features.drop('userid', axis=1) if 'userid' in features.columns else features
        y = target
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        
        results = {
            'model': model,
            'accuracy': accuracy_score(y_test, y_pred),
            'report': classification_report(y_test, y_pred, output_dict=True),
            'feature_importance': dict(zip(X.columns, model.feature_importances_))
        }
        
        return results