import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

class MoodleDataPreprocessor:
    def __init__(self):
        self.processed_data = {}
        
    def clean_log_data(self, df):
        """Clean and enrich log data"""
        df_clean = df.copy()
        
        # Convert timestamp to datetime
        df_clean['time_created'] = pd.to_datetime(df_clean['timecreated'], unit='s')
        df_clean['hour'] = df_clean['time_created'].dt.hour
        df_clean['day_of_week'] = df_clean['time_created'].dt.day_name()
        df_clean['date'] = df_clean['time_created'].dt.date
        
        # Extract action type from eventname
        df_clean['action_type'] = df_clean['eventname'].apply(
            lambda x: x.split('\\')[-1] if '\\' in str(x) else x
        )
        
        # Categorize actions
        def categorize_action(action):
            if 'viewed' in str(action).lower():
                return 'view'
            elif 'submitted' in str(action).lower():
                return 'submit'
            elif 'created' in str(action).lower():
                return 'create'
            elif 'updated' in str(action).lower():
                return 'update'
            else:
                return 'other'
        
        df_clean['action_category'] = df_clean['action_type'].apply(categorize_action)
        
        return df_clean
    
    def process_quiz_data(self, df):
        """Process quiz data for analysis"""
        df_quiz = df.copy()
        
        # Convert timestamps
        df_quiz['timestart'] = pd.to_datetime(df_quiz['timestart'], unit='s')
        df_quiz['timefinish'] = pd.to_datetime(df_quiz['timefinish'], unit='s')
        
        # Calculate quiz duration in minutes
        df_quiz['duration_minutes'] = (df_quiz['timefinish'] - df_quiz['timestart']).dt.total_seconds() / 60
        
        # Calculate attempt number per user per quiz
        df_quiz['attempt_number'] = df_quiz.groupby(['userid', 'quiz']).cumcount() + 1
        
        # Flag first and last attempts
        df_quiz['is_first_attempt'] = df_quiz['attempt_number'] == 1
        df_quiz['is_last_attempt'] = df_quiz.groupby(['userid', 'quiz'])['attempt_number'].transform('max') == df_quiz['attempt_number']
        
        return df_quiz
    
    def process_forum_data(self, df):
        """Process forum data for analysis"""
        df_forum = df.copy()
        
        # Convert timestamps
        df_forum['created'] = pd.to_datetime(df_forum['created'], unit='s')
        df_forum['modified'] = pd.to_datetime(df_forum['modified'], unit='s')
        
        # Calculate post length
        df_forum['post_length'] = df_forum['message'].str.len()
        
        # Extract reply information
        df_forum['is_reply'] = df_forum['parent'] > 0
        
        # Calculate time to first reply
        df_forum['hours_to_first_reply'] = self._calculate_reply_times(df_forum)
        
        return df_forum
    
    def _calculate_reply_times(self, df):
        """Calculate time to first reply for each post"""
        reply_times = []
        
        for idx, row in df.iterrows():
            if row['parent'] > 0:
                parent_post = df[df['id'] == row['parent']]
                if not parent_post.empty:
                    time_diff = (row['created'] - parent_post.iloc[0]['created']).total_seconds() / 3600
                    reply_times.append(time_diff)
                else:
                    reply_times.append(np.nan)
            else:
                replies = df[df['parent'] == row['id']]
                if not replies.empty:
                    first_reply = replies.nsmallest(1, 'created').iloc[0]
                    time_diff = (first_reply['created'] - row['created']).total_seconds() / 3600
                    reply_times.append(time_diff)
                else:
                    reply_times.append(np.nan)
        
        return reply_times
    
    def create_engagement_metrics(self, log_data, time_period='D'):
        """Create engagement metrics from log data"""
        engagement = log_data.groupby(['userid', 'courseid', pd.Grouper(key='time_created', freq=time_period)]).agg({
            'id': 'count',  # Number of actions
            'action_category': lambda x: (x == 'submit').sum(),  # Number of submissions
        }).rename(columns={'id': 'total_actions', 'action_category': 'submissions'})
        
        engagement.reset_index(inplace=True)
        
        # Calculate daily active minutes (simplified)
        engagement['active_minutes'] = engagement['total_actions'] * 2  # Assuming 2 minutes per action
        
        return engagement