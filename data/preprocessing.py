"""
Sample preprocessing utilities for Moodle Analytics
Provides data preprocessing functions for sample datasets.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class SampleDataPreprocessor:
    """Sample data preprocessor for demonstration purposes"""
    
    def __init__(self):
        self.processed_data = {}
        
    def preprocess_sample_logs(self, logs_df):
        """Preprocess sample log data"""
        df = logs_df.copy()
        
        # Convert timestamp to datetime if not already
        if 'time_created' not in df.columns:
            df['time_created'] = pd.to_datetime(df['timecreated'], unit='s')
        
        # Extract time features
        df['hour'] = df['time_created'].dt.hour
        df['day_of_week'] = df['time_created'].dt.day_name()
        df['date'] = df['time_created'].dt.date
        df['week'] = df['time_created'].dt.isocalendar().week
        
        # Extract action type from eventname
        df['action_type'] = df['eventname'].apply(
            lambda x: x.split('\\')[-1] if '\\' in str(x) else x
        )
        
        # Categorize actions
        def categorize_action(action):
            if 'viewed' in str(action).lower():
                return 'view'
            elif 'submitted' in str(action).lower() or 'created' in str(action).lower():
                return 'submit'
            elif 'updated' in str(action).lower():
                return 'update'
            else:
                return 'other'
        
        df['action_category'] = df['action_type'].apply(categorize_action)
        
        return df
    
    def preprocess_sample_quizzes(self, quizzes_df, attempts_df):
        """Preprocess sample quiz data and merge with attempts"""
        # Process attempts
        attempts = attempts_df.copy()
        attempts['timestart'] = pd.to_datetime(attempts['timestart'], unit='s')
        attempts['timefinish'] = pd.to_datetime(attempts['timefinish'], unit='s')
        
        # Calculate duration
        attempts['duration_minutes'] = (attempts['timefinish'] - attempts['timestart']).dt.total_seconds() / 60
        
        # Calculate final grade as percentage
        attempts['final_grade'] = attempts['sumgrades'] * 100
        
        # Flag first and last attempts
        attempts['is_first_attempt'] = attempts.groupby(['userid', 'quiz'])['attempt'].transform('min') == attempts['attempt']
        attempts['is_last_attempt'] = attempts.groupby(['userid', 'quiz'])['attempt'].transform('max') == attempts['attempt']
        
        # Merge with quiz info
        quizzes = quizzes_df.copy()
        merged = attempts.merge(quizzes, left_on='quiz', right_on='id', how='left')
        
        return merged
    
    def create_sample_engagement_metrics(self, logs_df, time_period='D'):
        """Create engagement metrics from processed log data"""
        # Group by user, course, and time period
        engagement = logs_df.groupby(['userid', 'courseid', pd.Grouper(key='time_created', freq=time_period)]).agg({
            'id': 'count',  # Number of actions
            'action_category': lambda x: (x == 'submit').sum(),  # Number of submissions
            'time_created': 'nunique'  # Number of active days
        }).rename(columns={
            'id': 'total_actions', 
            'action_category': 'submissions',
            'time_created': 'active_days'
        })
        
        engagement.reset_index(inplace=True)
        
        # Calculate estimated active minutes (2 minutes per action baseline)
        engagement['active_minutes'] = engagement['total_actions'] * 2
        
        # Add engagement score
        engagement['engagement_score'] = (
            engagement['total_actions'] * 0.4 +
            engagement['submissions'] * 0.4 +
            engagement['active_minutes'] * 0.2
        )
        
        return engagement
    
    def create_sample_course_analytics(self, logs_df, users_df, courses_df):
        """Create course-level analytics"""
        # Merge logs with course and user info
        course_logs = logs_df.merge(courses_df, left_on='courseid', right_on='id', how='left')
        
        # Course activity patterns
        course_patterns = course_logs.groupby('courseid').agg({
            'userid': 'nunique',  # Unique students
            'id': 'count',  # Total actions
            'action_category': lambda x: (x == 'submit').sum(),  # Submissions
            'time_created': ['min', 'max']  # Activity period
        }).round(2)
        
        course_patterns.columns = ['unique_students', 'total_actions', 'total_submissions', 'first_activity', 'last_activity']
        
        # Calculate activity span
        course_patterns['activity_span_days'] = (
            course_patterns['last_activity'] - course_patterns['first_activity']
        ).dt.days + 1
        
        return course_patterns
    
    def create_sample_student_profiles(self, logs_df, quizzes_df, users_df):
        """Create comprehensive student profiles"""
        # Student activity from logs
        student_activity = logs_df.groupby('userid').agg({
            'courseid': 'nunique',  # Number of courses
            'id': 'count',  # Total actions
            'action_category': lambda x: (x == 'submit').sum(),  # Submissions
            'time_created': 'nunique'  # Active days
        }).rename(columns={
            'courseid': 'courses_accessed',
            'id': 'total_actions',
            'action_category': 'total_submissions',
            'time_created': 'active_days'
        })
        
        # Student quiz performance
        if not quizzes_df.empty:
            quiz_stats = quizzes_df.groupby('userid').agg({
                'final_grade': ['mean', 'max', 'min', 'count'],
                'duration_minutes': 'mean',
                'attempt': 'max'
            }).round(2)
            
            quiz_stats.columns = ['avg_quiz_score', 'max_quiz_score', 'min_quiz_score', 'quiz_attempts', 'avg_quiz_duration', 'max_attempts']
            
            # Merge with activity data
            profiles = student_activity.merge(quiz_stats, left_index=True, right_index=True, how='left')
        else:
            profiles = student_activity
        
        # Add user demographics
        if not users_df.empty:
            user_info = users_df.set_index('id')[['firstname', 'lastname', 'email', 'city']]
            profiles = profiles.merge(user_info, left_index=True, right_index=True, how='left')
        
        return profiles
    
    def generate_sample_risk_analysis(self, engagement_df, quiz_df=None):
        """Generate sample risk analysis data"""
        # Calculate risk based on engagement
        risk_data = engagement_df.groupby(['userid', 'courseid']).agg({
            'engagement_score': 'mean',
            'total_actions': 'sum',
            'submissions': 'sum',
            'active_minutes': 'sum'
        }).reset_index()
        
        # Normalize engagement score
        risk_data['engagement_percentile'] = risk_data['engagement_score'].rank(pct=True) * 100
        
        # Determine risk levels
        risk_data['risk_level'] = pd.cut(
            risk_data['engagement_percentile'],
            bins=[0, 25, 50, 75, 100],
            labels=['High Risk', 'Medium Risk', 'Low Risk', 'Very Low Risk'],
            include_lowest=True
        )
        
        # Add quiz performance risk if available
        if quiz_df is not None and not quiz_df.empty:
            quiz_risk = quiz_df.groupby(['userid', 'quiz'])['final_grade'].mean().reset_index()
            quiz_risk.columns = ['userid', 'courseid', 'avg_quiz_score']
            
            risk_data = risk_data.merge(quiz_risk, on=['userid', 'courseid'], how='left')
            
            # Grade-based risk
            risk_data['grade_risk'] = pd.cut(
                risk_data['avg_quiz_score'],
                bins=[0, 50, 70, 85, 100],
                labels=['High Risk', 'Medium Risk', 'Low Risk', 'Very Low Risk'],
                include_lowest=True
            )
        
        return risk_data
    
    def save_processed_data(self, output_dir='processed'):
        """Save all processed data to files"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for name, df in self.processed_data.items():
            filepath = os.path.join(output_dir, f'{name}.csv')
            df.to_csv(filepath, index=False)
            print(f"Saved processed {name} to {filepath}")
        
        return self.processed_data

# Export the sample preprocessor
__all__ = ['SampleDataPreprocessor']