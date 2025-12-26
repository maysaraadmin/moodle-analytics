"""
Sample analysis data for Moodle Analytics
This file contains sample processed data for testing and demonstration.
"""

import pandas as pd
import numpy as np

# Sample student engagement data
def get_sample_engagement_data():
    """Generate sample student engagement data"""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', '2024-03-31', freq='D')
    
    data = []
    for date in dates:
        for student_id in range(1, 51):  # 50 students
            for course_id in ['MATH101', 'PHYS201', 'CHEM301']:
                if np.random.random() > 0.3:  # 70% activity probability
                    data.append({
                        'date': date,
                        'userid': student_id,
                        'courseid': course_id,
                        'total_actions': np.random.randint(1, 20),
                        'submissions': np.random.randint(0, 3),
                        'active_minutes': np.random.randint(5, 120),
                        'day_of_week': date.day_name(),
                        'hour': np.random.randint(8, 22)
                    })
    
    return pd.DataFrame(data)

# Sample quiz performance data
def get_sample_quiz_data():
    """Generate sample quiz performance data"""
    np.random.seed(42)
    
    data = []
    quiz_types = ['Quiz1', 'Quiz2', 'Quiz3', 'Quiz4', 'Midterm', 'Final']
    
    for student_id in range(1, 51):
        for quiz_id in quiz_types:
            for attempt in range(1, np.random.randint(1, 4)):  # 1-3 attempts
                data.append({
                    'userid': student_id,
                    'quiz': quiz_id,
                    'attempt_number': attempt,
                    'final_grade': np.clip(np.random.normal(75, 15), 0, 100),
                    'duration_minutes': np.random.exponential(30),
                    'timestart': pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(1, 90)),
                    'timefinish': pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(1, 90)),
                    'is_first_attempt': attempt == 1,
                    'is_last_attempt': attempt == np.random.randint(1, 4)
                })
    
    return pd.DataFrame(data)

# Sample forum interaction data
def get_sample_forum_data():
    """Generate sample forum interaction data"""
    np.random.seed(42)
    
    data = []
    post_id = 1
    
    for course_id in ['MATH101', 'PHYS201', 'CHEM301']:
        # Create discussion threads
        for discussion in range(1, 11):  # 10 discussions per course
            # Original post
            data.append({
                'id': post_id,
                'userid': np.random.randint(1, 51),
                'course': course_id,
                'discussion': discussion,
                'parent': 0,
                'created': pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(1, 60)),
                'modified': pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(1, 60)),
                'message': f"Discussion post {discussion} in {course_id}",
                'is_reply': False
            })
            post_id += 1
            
            # Add replies
            num_replies = np.random.randint(0, 8)
            for reply in range(num_replies):
                data.append({
                    'id': post_id,
                    'userid': np.random.randint(1, 51),
                    'course': course_id,
                    'discussion': discussion,
                    'parent': post_id - num_replies - 1,
                    'created': pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(1, 60)),
                    'modified': pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(1, 60)),
                    'message': f"Reply to discussion {discussion}",
                    'is_reply': True
                })
                post_id += 1
    
    return pd.DataFrame(data)

# Sample course completion data
def get_sample_completion_data():
    """Generate sample course completion data"""
    np.random.seed(42)
    
    data = []
    for student_id in range(1, 51):
        for course_id in ['MATH101', 'PHYS201', 'CHEM301']:
            if np.random.random() > 0.2:  # 80% enrollment rate
                data.append({
                    'userid': student_id,
                    'course': course_id,
                    'timeenrolled': pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(30, 120)),
                    'timestarted': pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(1, 90)),
                    'timecompleted': pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(1, 60)) if np.random.random() > 0.3 else None,
                    'completion_percentage': np.random.uniform(0, 100) if np.random.random() > 0.3 else np.random.uniform(0, 70)
                })
    
    return pd.DataFrame(data)

# Export sample data functions
__all__ = [
    'get_sample_engagement_data',
    'get_sample_quiz_data', 
    'get_sample_forum_data',
    'get_sample_completion_data'
]