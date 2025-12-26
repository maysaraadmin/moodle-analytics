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
        """Load Moodle log data with user and course information"""
        query = """
        SELECT 
            l.id, l.userid, l.courseid, l.action, l.target, l.objecttable,
            l.objectid, l.crud, l.edulevel, l.contextinstanceid, l.contextlevel,
            l.contextid, l.userid, l.courseid, l.relateduserid, l.anonymous,
            l.other, l.timecreated, l.origin, l.ip, l.realuserid,
            u.username, u.firstname, u.lastname, u.email,
            c.fullname as course_name, c.shortname as course_shortname
        FROM mdl_logstore_standard_log l
        LEFT JOIN mdl_user u ON l.userid = u.id
        LEFT JOIN mdl_course c ON l.courseid = c.id
        WHERE l.userid > 1  # Skip guest user
        ORDER BY l.timecreated DESC
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
            q.course as course_id,
            c.fullname as course_name,
            u.firstname, u.lastname, u.email
        FROM mdl_quiz_attempts qa
        JOIN mdl_quiz q ON qa.quiz = q.id
        JOIN mdl_course c ON q.course = c.id
        JOIN mdl_user u ON qa.userid = u.id
        WHERE qa.preview = 0  # Skip preview attempts
        """
        return pd.read_sql(query, self.db_connection)
    
    def load_forum_data(self):
        """Load forum posts and discussions"""
        query = """
        SELECT 
            fp.*,
            fd.name as discussion_name,
            f.name as forum_name,
            c.id as course_id,
            c.fullname as course_name,
            u.firstname, u.lastname, u.email
        FROM mdl_forum_posts fp
        JOIN mdl_forum_discussions fd ON fp.discussion = fd.id
        JOIN mdl_forum f ON fd.forum = f.id
        JOIN mdl_course c ON f.course = c.id
        JOIN mdl_user u ON fp.userid = u.id
        WHERE fp.parent > 0  # Skip initial discussion posts
        """
        return pd.read_sql(query, self.db_connection)
    
    def load_completion_data(self):
        """Load course completion data"""
        query = """
        SELECT 
            cc.*,
            c.fullname as course_name,
            u.firstname, u.lastname, u.email,
            c2.completionstartonenrol as completion_enabled
        FROM mdl_course_completions cc
        JOIN mdl_course c ON cc.course = c.id
        JOIN mdl_user u ON cc.userid = u.id
        JOIN mdl_course_completion_criteria ccc ON cc.course = ccc.course
        JOIN mdl_course_completion_criteria c2 ON ccc.course = c2.course
        WHERE cc.userid > 1  # Skip guest user
        GROUP BY cc.id, c.fullname, u.firstname, u.lastname, u.email, c2.completionstartonenrol
        """
        return pd.read_sql(query, self.db_connection)
    
    def load_course_data(self):
        """Load basic course information"""
        query = """
        SELECT 
            c.*,
            COUNT(DISTINCT e.userid) as enrolled_users,
            COUNT(DISTINCT cc.id) as completions
        FROM mdl_course c
        LEFT JOIN mdl_enrol e ON c.id = e.courseid
        LEFT JOIN mdl_user_enrolments ue ON e.id = ue.enrolid
        LEFT JOIN mdl_course_completions cc ON c.id = cc.course
        WHERE c.id > 1  # Skip front page
        GROUP BY c.id, c.fullname, c.shortname, c.summary, c.format, c.showgrades, 
                 c.newsitems, c.startdate, c.enddate, c.marker, c.maxbytes, 
                 c.legacyfiles, c.showreports, c.visible, c.visibleold, 
                 c.groupmode, c.groupmodeforce, c.defaultgroupingid, c.lang, 
                 c.calendartype, c.theme, c.timecreated, c.timemodified, 
                 c.requested, c.enablecompletion, c.completionnotify, c.cacherev
        """
        return pd.read_sql(query, self.db_connection)
    
    def load_user_data(self):
        """Load user information"""
        query = """
        SELECT 
            u.*,
            GROUP_CONCAT(DISTINCT c.shortname) as enrolled_courses
        FROM mdl_user u
        LEFT JOIN mdl_user_enrolments ue ON u.id = ue.userid
        LEFT JOIN mdl_enrol e ON ue.enrolid = e.id
        LEFT JOIN mdl_course c ON e.courseid = c.id
        WHERE u.deleted = 0 AND u.suspended = 0
        GROUP BY u.id, u.auth, u.confirmed, u.policyagreed, u.deleted, 
                 u.suspended, u.mnethostid, u.username, u.password, 
                 u.idnumber, u.firstname, u.lastname, u.email, u.emailstop, 
                 u.icq, u.skype, u.yahoo, u.aim, u.msn, u.phone1, u.phone2, 
                 u.institution, u.department, u.address, u.city, u.country, 
                 u.lang, u.calendartype, u.theme, u.timezone, u.firstaccess, 
                 u.lastaccess, u.lastlogin, u.currentlogin, u.lastip, 
                 u.secret, u.picture, u.url, u.description, u.descriptionformat, 
                 u.mailformat, u.maildigest, u.maildisplay, u.autosubscribe, 
                 u.trackforums, u.timecreated, u.timemodified, u.trustbitmask, 
                 u.imagealt, u.lastnamephonetic, u.firstnamephonetic, 
                 u.middlename, u.alternatename, u.moodlenetprofile
        """
        return pd.read_sql(query, self.db_connection)