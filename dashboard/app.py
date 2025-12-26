import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from datetime import datetime, timedelta
import warnings

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from src
from src.data_loader import MoodleDataLoader
from src.preprocessing import MoodleDataPreprocessor
from src.analysis import MoodleAnalytics
from src.visualization import MoodleVisualizer

# Suppress warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Moodle Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton button {
        width: 100%;
        background-color: #3B82F6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

class MoodleDashboard:
    def __init__(self):
        self.loader = MoodleDataLoader()
        self.db_connection = None
        self.processor = MoodleDataPreprocessor()
        self.analytics = MoodleAnalytics()
        self.visualizer = MoodleVisualizer()
        self.current_data_source = "Database"
        
    def load_data(self):
        """Load data from the database"""
        try:
            # Connect to database
            self.db_connection = self.loader.connect_to_moodle_db()
            
            # Load real data
            with st.spinner("Loading data from Moodle database..."):
                self.log_data = self.loader.load_log_data(limit=1000)  # Limit for performance
                self.quiz_data = self.loader.load_quiz_data()
                self.forum_data = self.loader.load_forum_data()
                self.completion_data = self.loader.load_completion_data()
                self.course_data = self.loader.load_course_data()
                self.user_data = self.loader.load_user_data()
                
                # Store in session state
                st.session_state['data_loaded'] = True
                st.session_state['data_source'] = 'database'
                st.session_state['log_data'] = self.log_data
                st.session_state['quiz_data'] = self.quiz_data
                st.session_state['forum_data'] = self.forum_data
                st.session_state['completion_data'] = self.completion_data
                st.session_state['course_data'] = self.course_data
                st.session_state['user_data'] = self.user_data
                
            return True
            
        except Exception as e:
            st.error(f"Failed to load data from database: {str(e)}")
            return False
    
    def show_sidebar(self):
        """Show the sidebar controls"""
        with st.sidebar:
            st.title("📊 Dashboard Controls")
            
            # Data source info
            st.markdown("### Data Source")
            st.info("Connected to Moodle Database")
            
            # Add a refresh button
            if st.button("🔄 Refresh Data", type="primary"):
                with st.spinner("Refreshing data..."):
                    self.load_data()
                    st.rerun()
            
            # Analysis type selection
            self.analysis_type = st.selectbox(
                "Analysis Type",
                ["Overview", "Student Engagement", "Course Analytics", 
                 "Forum Analysis", "Quiz Performance", "Predictive Analytics"]
            )
            
            # Date range filter
            self.time_range = st.date_input(
                "Date Range",
                value=(
                    datetime.now() - timedelta(days=30),
                    datetime.now()
                )
            )
    
    def show_overview(self):
        """Display overview dashboard with real data"""
        if 'data_loaded' not in st.session_state:
            if not self.load_data():
                return
                
        # Get data from session state
        log_data = st.session_state.get('log_data', pd.DataFrame())
        course_data = st.session_state.get('course_data', pd.DataFrame())
        user_data = st.session_state.get('user_data', pd.DataFrame())
        
        # Calculate metrics
        total_students = len(user_data) if not user_data.empty else 0
        active_courses = len(course_data) if not course_data.empty else 0
        
        # Calculate engagement (logins in last 30 days)
        if not log_data.empty and 'timecreated' in log_data.columns:
            recent_logs = log_data[log_data['timecreated'] > (pd.Timestamp.now() - pd.Timedelta(days=30)).timestamp()]
            active_students = recent_logs['userid'].nunique()
            engagement_rate = (active_students / total_students * 100) if total_students > 0 else 0
        else:
            engagement_rate = 0
        
        # Display metrics
        st.markdown('<h1 class="main-header">📚 Moodle Learning Analytics Dashboard</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total Students", total_students)
        
        with col2:
            st.metric("📚 Active Courses", active_courses)
        
        with col3:
            st.metric("📊 Engagement (30d)", f"{engagement_rate:.1f}%")
        
        with col4:
            st.metric("📅 Last Updated", pd.Timestamp.now().strftime("%Y-%m-%d"))
        
        # Course statistics
        st.subheader("Course Statistics")
        if not course_data.empty:
            st.dataframe(
                course_data[['fullname', 'shortname', 'enrolled_users', 'completions']]
                .rename(columns={
                    'fullname': 'Course Name',
                    'shortname': 'Code',
                    'enrolled_users': 'Enrolled',
                    'completions': 'Completions'
                }),
                width='stretch'
            )
        else:
            st.warning("No course data available")
        
        # Activity over time
        st.subheader("Activity Over Time")
        if not log_data.empty and 'timecreated' in log_data.columns:
            log_data['date'] = pd.to_datetime(log_data['timecreated'], unit='s')
            daily_activity = log_data.resample('D', on='date').size()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_activity.index,
                y=daily_activity.values,
                mode='lines',
                name='Daily Activity'
            ))
            fig.update_layout(
                template="plotly_white",
                height=400,
                xaxis_title="Date",
                yaxis_title="Number of Activities"
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.warning("No activity data available")
    
    def show_engagement_analysis(self):
        """Display engagement analysis with real data"""
        if 'data_loaded' not in st.session_state:
            if not self.load_data():
                return
                
        st.header("Student Engagement Analysis")
        
        # Get data from session state
        log_data = st.session_state.get('log_data', pd.DataFrame())
        user_data = st.session_state.get('user_data', pd.DataFrame())
        
        if log_data.empty or user_data.empty:
            st.warning("No engagement data available")
            return
        
        # Add more engagement analysis visualizations here
        st.subheader("User Activity")
        
        # Convert timestamp to datetime
        log_data['datetime'] = pd.to_datetime(log_data['timecreated'], unit='s')
        
        # Activity by hour of day
        log_data['hour'] = log_data['datetime'].dt.hour
        hourly_activity = log_data['hour'].value_counts().sort_index()
        
        fig = px.bar(
            x=hourly_activity.index,
            y=hourly_activity.values,
            labels={'x': 'Hour of Day', 'y': 'Number of Activities'},
            title='Activity by Hour of Day'
        )
        st.plotly_chart(fig, width='stretch')
    
    def show_course_analytics(self):
        """Display course analytics with real data"""
        if 'data_loaded' not in st.session_state:
            if not self.load_data():
                return
                
        st.header("Course Analytics")
        
        # Get data from session state
        course_data = st.session_state.get('course_data', pd.DataFrame())
        
        if course_data.empty:
            st.warning("No course data available")
            return
            
        # Display course metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Courses", len(course_data))
        with col2:
            avg_enrollment = course_data['enrolled_users'].mean() if not course_data.empty else 0
            st.metric("Avg. Enrollment", f"{avg_enrollment:.1f}")
        with col3:
            completion_rate = (course_data['completions'] / course_data['enrolled_users'].replace(0, np.nan)).mean() * 100 if not course_data.empty else 0
            completion_rate = completion_rate if not np.isnan(completion_rate) else 0
            st.metric("Avg. Completion Rate", f"{completion_rate:.1f}%")
        
        # Course enrollment distribution
        st.subheader("Course Enrollment Distribution")
        if not course_data.empty:
            fig = px.histogram(
                course_data,
                x='enrolled_users',
                nbins=20,
                labels={'enrolled_users': 'Number of Students'},
                title='Distribution of Course Enrollments'
            )
            st.plotly_chart(fig, width='stretch')
            
            # Top courses by enrollment
            st.subheader("Top Courses by Enrollment")
            top_courses = course_data.nlargest(10, 'enrolled_users')[['fullname', 'enrolled_users', 'completions']]
            top_courses['completion_rate'] = (top_courses['completions'] / top_courses['enrolled_users'] * 100).round(1)
            st.dataframe(
                top_courses.rename(columns={
                    'fullname': 'Course',
                    'enrolled_users': 'Enrolled',
                    'completions': 'Completions',
                    'completion_rate': 'Completion Rate (%)'
                }),
                width='stretch'
            )
    
    def show_forum_analysis(self):
        """Display forum analysis with real data"""
        if 'data_loaded' not in st.session_state:
            if not self.load_data():
                return
                
        st.header("Forum Analysis")
        
        # Get data from session state
        forum_data = st.session_state.get('forum_data', pd.DataFrame())
        user_data = st.session_state.get('user_data', pd.DataFrame())
        
        if forum_data.empty:
            st.warning("No forum data available")
            return
        
        # Forum activity metrics
        st.subheader("Forum Activity Overview")
        
        # Posts per user
        posts_per_user = forum_data['userid'].value_counts().head(10)
        fig = px.bar(
            x=posts_per_user.index,
            y=posts_per_user.values,
            labels={'x': 'User ID', 'y': 'Number of Posts'},
            title='Top 10 Most Active Users'
        )
        st.plotly_chart(fig, width='stretch')
        
        # Posts over time
        if 'created' in forum_data.columns:
            forum_data['datetime'] = pd.to_datetime(forum_data['created'], unit='s')
            daily_posts = forum_data.resample('D', on='datetime').size()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_posts.index,
                y=daily_posts.values,
                mode='lines',
                name='Daily Posts'
            ))
            fig.update_layout(
                title='Forum Activity Over Time',
                xaxis_title='Date',
                yaxis_title='Number of Posts'
            )
            st.plotly_chart(fig, width='stretch')
    
    def show_quiz_performance(self):
        """Display quiz performance analysis with real data"""
        if 'data_loaded' not in st.session_state:
            if not self.load_data():
                return
                
        st.header("Quiz Performance Analysis")
        
        # Get data from session state
        quiz_data = st.session_state.get('quiz_data', pd.DataFrame())
        
        if quiz_data.empty:
            st.warning("No quiz data available")
            return
        
        # Quiz performance metrics
        st.subheader("Quiz Performance Overview")
        
        # Average quiz scores
        if 'final_grade' in quiz_data.columns:
            avg_scores = quiz_data.groupby('quiz_name')['final_grade'].mean().sort_values(ascending=False)
            
            fig = px.bar(
                x=avg_scores.index,
                y=avg_scores.values,
                labels={'x': 'Quiz', 'y': 'Average Score'},
                title='Average Scores by Quiz'
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, width='stretch')
        
        # Quiz attempts distribution
        attempts_per_quiz = quiz_data['quiz_name'].value_counts()
        
        fig = px.pie(
            values=attempts_per_quiz.values,
            names=attempts_per_quiz.index,
            title='Quiz Attempts Distribution'
        )
        st.plotly_chart(fig, width='stretch')
    
    def show_predictive_analytics(self):
        """Display predictive analytics with real data"""
        if 'data_loaded' not in st.session_state:
            if not self.load_data():
                return
                
        st.header("Predictive Analytics")
        
        # Get data from session state
        log_data = st.session_state.get('log_data', pd.DataFrame())
        user_data = st.session_state.get('user_data', pd.DataFrame())
        completion_data = st.session_state.get('completion_data', pd.DataFrame())
        
        if log_data.empty or user_data.empty:
            st.warning("Insufficient data for predictive analytics")
            return
        
        st.subheader("Student Engagement Prediction")
        
        # Calculate engagement metrics
        if 'timecreated' in log_data.columns:
            # Activity frequency per user
            user_activity = log_data.groupby('userid').size().reset_index(name='activity_count')
            user_activity = user_activity.merge(user_data[['id', 'firstname', 'lastname']], 
                                              left_on='userid', right_on='id', how='left')
            
            # Define engagement levels based on activity
            def categorize_engagement(activity_count):
                if activity_count > 100:
                    return 'High'
                elif activity_count > 50:
                    return 'Medium'
                else:
                    return 'Low'
            
            user_activity['engagement_level'] = user_activity['activity_count'].apply(categorize_engagement)
            
            # Display engagement distribution
            engagement_counts = user_activity['engagement_level'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(
                    values=engagement_counts.values,
                    names=engagement_counts.index,
                    title='Student Engagement Distribution'
                )
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                fig = px.bar(
                    x=engagement_counts.index,
                    y=engagement_counts.values,
                    labels={'x': 'Engagement Level', 'y': 'Number of Students'},
                    title='Students by Engagement Level'
                )
                st.plotly_chart(fig, width='stretch')
            
            # Show top engaged students
            st.subheader("Most Engaged Students")
            top_students = user_activity.nlargest(10, 'activity_count')
            st.dataframe(
                top_students[['firstname', 'lastname', 'activity_count', 'engagement_level']],
                width='stretch'
            )
        
        # Course completion prediction
        if not completion_data.empty:
            st.subheader("Course Completion Analysis")
            
            # Completion rates by course
            completion_rates = completion_data.groupby('course_name').size()
            
            fig = px.bar(
                x=completion_rates.index,
                y=completion_rates.values,
                labels={'x': 'Course', 'y': 'Number of Completions'},
                title='Course Completions'
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, width='stretch')
    
    def run(self):
        """Run the dashboard"""
        # Show sidebar
        self.show_sidebar()
        
        # Show the selected analysis
        if self.analysis_type == "Overview":
            self.show_overview()
        elif self.analysis_type == "Student Engagement":
            self.show_engagement_analysis()
        elif self.analysis_type == "Course Analytics":
            self.show_course_analytics()
        elif self.analysis_type == "Forum Analysis":
            self.show_forum_analysis()
        elif self.analysis_type == "Quiz Performance":
            self.show_quiz_performance()
        elif self.analysis_type == "Predictive Analytics":
            self.show_predictive_analytics()

# Main execution
if __name__ == "__main__":
    # Initialize the dashboard
    dashboard = MoodleDashboard()
    
    # Try to load data immediately
    if 'data_loaded' not in st.session_state:
        with st.spinner("Loading data from database..."):
            if not dashboard.load_data():
                st.error("Failed to load data from database. Please check your connection settings.")
                st.stop()
    
    # Run the dashboard
    dashboard.run()