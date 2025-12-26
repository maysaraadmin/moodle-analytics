import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

class MoodleDataLoader:
    def __init__(self, config_path='config.env'):
        load_dotenv(config_path)
        self.db_connection = None
        
    def connect_to_moodle_db(self):
        """Connect to Moodle MySQL database"""
        db_config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
            'port': int(os.getenv('DB_PORT', 3306))
        }
        
        connection_str = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        self.db_connection = create_engine(connection_str)
        return self.db_connection
    
    def load_log_data(self, limit=None):
        """Load Moodle log data"""
        query = """
        SELECT 
            l.*,
            u.username,
            u.firstname,
            u.lastname,
            c.fullname as course_name
        FROM mdl_logstore_standard_log l
        JOIN mdl_user u ON l.userid = u.id
        JOIN mdl_course c ON l.courseid = c.id
        """
        
        if limit:
            query += f" LIMIT {limit}"
            
        return pd.read_sql(query, self.db_connection)
    
    def load_quiz_data(self):
        """Load quiz attempts and grades"""
        query = """
        SELECT 
            qa.*,
            q.name as quiz_name,
            u.username,
            c.fullname as course_name,
            qg.grade as final_grade
        FROM mdl_quiz_attempts qa
        JOIN mdl_quiz q ON qa.quiz = q.id
        JOIN mdl_user u ON qa.userid = u.id
        JOIN mdl_course c ON q.course = c.id
        LEFT JOIN mdl_quiz_grades qg ON qa.quiz = qg.quiz AND qa.userid = qg.userid
        """
        return pd.read_sql(query, self.db_connection)
    
    def load_forum_data(self):
        """Load forum discussions and posts"""
        query = """
        SELECT 
            fp.*,
            fd.name as discussion_name,
            f.name as forum_name,
            u.username,
            u.firstname,
            u.lastname,
            c.fullname as course_name
        FROM mdl_forum_posts fp
        JOIN mdl_forum_discussions fd ON fp.discussion = fd.id
        JOIN mdl_forum f ON fd.forum = f.id
        JOIN mdl_user u ON fp.userid = u.id
        JOIN mdl_course c ON f.course = c.id
        """
        return pd.read_sql(query, self.db_connection)
    
    def load_course_completion(self):
        """Load course completion data"""
        query = """
        SELECT 
            cc.*,
            c.fullname as course_name,
            u.username,
            u.firstname,
            u.lastname
        FROM mdl_course_completions cc
        JOIN mdl_course c ON cc.course = c.id
        JOIN mdl_user u ON cc.userid = u.id
        """
        return pd.read_sql(query, self.db_connection)
    
    def load_from_csv(self, filepath, **kwargs):
        """Load data from CSV files (for exported Moodle logs)"""
        return pd.read_csv(filepath, **kwargs)

    def load_completion_data(self):
        """Load course completion data with additional context"""
        query = """
        SELECT 
            cc.*,
            c.fullname as course_name,
            u.username,
            u.firstname,
            u.lastname,
            u.email
        FROM mdl_course_completions cc
        JOIN mdl_course c ON cc.course = c.id
        JOIN mdl_user u ON cc.userid = u.id
        WHERE cc.userid > 1  # Skip guest user
        """
        return pd.read_sql(query, self.db_connection)
    
    def load_course_data(self):
        """Load course data"""
        query = """
        SELECT 
            c.*,
            COUNT(DISTINCT u.id) as enrolled_users,
            COUNT(DISTINCT cc.id) as completions
        FROM mdl_course c
        LEFT JOIN mdl_user_enrolments ue ON c.id = ue.enrolid
        LEFT JOIN mdl_enrol e ON ue.enrolid = e.id
        LEFT JOIN mdl_user u ON ue.userid = u.id
        LEFT JOIN mdl_course_completions cc ON c.id = cc.course
        WHERE c.visible = 1
        GROUP BY c.id
        """
        return pd.read_sql(query, self.db_connection)
    
    def load_user_data(self):
        """Load user data"""
        query = """
        SELECT 
            u.id,
            u.username,
            u.firstname,
            u.lastname,
            u.email,
            u.city,
            u.country,
            u.lastaccess,
            u.currentlogin,
            u.timecreated
        FROM mdl_user u
        WHERE u.deleted = 0 AND u.id > 1  # Skip guest and deleted users
        """
        return pd.read_sql(query, self.db_connection)