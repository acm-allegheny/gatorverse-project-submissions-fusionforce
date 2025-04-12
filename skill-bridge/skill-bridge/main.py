from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skillbridge.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Registration Form
class RegistrationForm(FlaskForm):
    """Form for user registration with validation."""
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    major = SelectField('Major', choices=[
        ('Computer Science', 'Computer Science'),
        ('Art', 'Art'),
        ('Business', 'Business'),
        ('Psychology', 'Psychology'),
        ('Biology', 'Biology'),
        ('Economics', 'Economics'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    skills = StringField('Skills (comma-separated)', validators=[DataRequired()])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    submit = SubmitField('Register')

# Login Form
class LoginForm(FlaskForm):
    """Form for user login with validation."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# User model with XP and review fields
class User(UserMixin, db.Model):
    """User model representing a student in the system."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    major = db.Column(db.String(100), default='')
    skills = db.Column(db.String(500), default='')
    bio = db.Column(db.Text, default='')
    profile_image = db.Column(db.String(200), default='https://i.pravatar.cc/150?img=0')
    experience_points = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0.0)
    projects = db.relationship('Project', backref='creator', lazy=True)
    reviews_received = db.relationship('Review', foreign_keys='Review.reviewee_id', backref='reviewee', lazy=True)
    reviews_given = db.relationship('Review', foreign_keys='Review.reviewer_id', backref='reviewer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_experience_points(self):
        completed_projects = Project.query.filter_by(creator_id=self.id, status='completed').count()
        positive_reviews = Review.query.filter_by(reviewee_id=self.id, rating__gte=4).count()
        self.experience_points = (completed_projects * 20) + (positive_reviews * 5)
        db.session.commit()

    def update_average_rating(self):
        reviews = Review.query.filter_by(reviewee_id=self.id).all()
        if reviews:
            self.average_rating = sum(review.rating for review in reviews) / len(reviews)
        else:
            self.average_rating = 0.0
        db.session.commit()

# Review model
class Review(db.Model):
    """Review model for user feedback and ratings."""
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text)
    feedback_tags = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# Project model with status field
class Project(db.Model):
    """Project model representing a collaborative project."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.String(500))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    reviews = db.relationship('Review', backref='project', lazy=True)

# Collaboration request model
class CollaborationRequest(db.Model):
    """Model for collaboration requests between users."""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('index.html', projects=projects)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            major=form.major.data,
            skills=form.skills.data,
            bio=form.bio.data,
            profile_image=None
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('Invalid email or password', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        required_skills = request.form['required_skills']
        status = request.form['status']
        
        project = Project(
            title=title,
            description=description,
            required_skills=required_skills,
            status=status,
            creator_id=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_project.html')

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project)

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    major = request.args.get('major', '')
    search_type = request.args.get('type', 'all')  # all, users, projects
    
    results = {
        'users': [],
        'projects': []
    }
    
    if search_type in ['all', 'users']:
        # Search users by skills and major
        user_query = User.query
        if query:
            user_query = user_query.filter(
                User.skills.ilike(f'%{query}%') |
                User.username.ilike(f'%{query}%') |
                User.bio.ilike(f'%{query}%')
            )
        if major:
            user_query = user_query.filter(User.major == major)
        results['users'] = user_query.all()
    
    if search_type in ['all', 'projects']:
        # Search projects by required skills and title
        project_query = Project.query
        if query:
            project_query = project_query.filter(
                Project.required_skills.ilike(f'%{query}%') |
                Project.title.ilike(f'%{query}%') |
                Project.description.ilike(f'%{query}%')
            )
        if major:
            project_query = project_query.join(User).filter(User.major == major)
        results['projects'] = project_query.all()
    
    # If it's an API request, return JSON
    if request.args.get('format') == 'json':
        return jsonify({
            'users': [{
                'id': user.id,
                'username': user.username,
                'major': user.major,
                'skills': user.skills,
                'bio': user.bio,
                'profile_image': user.profile_image
            } for user in results['users']],
            'projects': [{
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'required_skills': project.required_skills,
                'creator': {
                    'id': project.creator.id,
                    'username': project.creator.username
                }
            } for project in results['projects']]
        })
    
    return render_template('search.html', 
                         results=results,
                         query=query,
                         major=major,
                         search_type=search_type)

@app.route('/project/<int:project_id>/complete', methods=['POST'])
@login_required
def complete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.creator_id != current_user.id:
        flash('You are not authorized to complete this project.', 'danger')
        return redirect(url_for('project_detail', project_id=project_id))
    
    project.status = 'completed'
    current_user.update_experience_points()
    db.session.commit()
    flash('Project marked as completed!', 'success')
    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/project/<int:project_id>/review', methods=['POST'])
@login_required
def add_review(project_id):
    project = Project.query.get_or_404(project_id)
    if project.status != 'completed':
        flash('You can only review completed projects.', 'danger')
        return redirect(url_for('project_detail', project_id=project_id))
    
    rating = float(request.form.get('rating'))
    comment = request.form.get('comment')
    feedback_tags = request.form.get('feedback_tags', '')
    
    # Create review for each team member
    for member in project.collaborators:
        if member.id != current_user.id:  # Don't review yourself
            review = Review(
                reviewer_id=current_user.id,
                reviewee_id=member.id,
                project_id=project_id,
                rating=rating,
                comment=comment,
                feedback_tags=feedback_tags
            )
            db.session.add(review)
            member.update_experience_points()
            member.update_average_rating()
    
    db.session.commit()
    flash('Reviews submitted successfully!', 'success')
    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/recommendations')
@login_required
def get_recommendations():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_skills = set(skill.strip().lower() for skill in current_user.skills.split(','))
    
    # Find matching projects
    matching_projects = []
    for project in Project.query.filter(Project.status == 'active').all():
        project_skills = set(skill.strip().lower() for skill in project.required_skills.split(','))
        if user_skills.intersection(project_skills):
            matching_projects.append(project)
    
    # Find matching users
    matching_users = []
    for user in User.query.filter(User.id != current_user.id).all():
        user_skills2 = set(skill.strip().lower() for skill in user.skills.split(','))
        if user_skills.intersection(user_skills2):
            matching_users.append(user)
    
    # If it's an API request, return JSON
    if request.args.get('format') == 'json':
        return jsonify({
            'projects': [{
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'required_skills': project.required_skills,
                'creator': {
                    'id': project.creator.id,
                    'username': project.creator.username
                }
            } for project in matching_projects[:3]],  # Limit to 3 projects
            'users': [{
                'id': user.id,
                'username': user.username,
                'major': user.major,
                'skills': user.skills,
                'bio': user.bio
            } for user in matching_users[:3]]  # Limit to 3 users
        })
    
    return render_template('recommendations.html',
                         matching_projects=matching_projects[:3],
                         matching_users=matching_users[:3])

def create_sample_data():
    # Create sample users
    users = [
        User(
            username='alice_dev',
            email='alice@example.com',
            major='Computer Science',
            skills='Python, JavaScript, React, UI Design',
            bio='Passionate about web development and UI/UX design. Looking to collaborate on innovative projects.',
            profile_image='https://i.pravatar.cc/150?img=1'
        ),
        User(
            username='bob_artist',
            email='bob@example.com',
            major='Art',
            skills='Digital Art, UI Design, Photoshop, Illustration',
            bio='Digital artist specializing in UI/UX design and illustrations. Open to creative collaborations.',
            profile_image='https://i.pravatar.cc/150?img=2'
        ),
        User(
            username='charlie_biz',
            email='charlie@example.com',
            major='Business',
            skills='Marketing, Project Management, Data Analysis, Leadership',
            bio='Business student with a focus on digital marketing and project management.',
            profile_image='https://i.pravatar.cc/150?img=3'
        ),
        User(
            username='diana_psych',
            email='diana@example.com',
            major='Psychology',
            skills='Research, Data Analysis, UX Research, Human Behavior',
            bio='Psychology major interested in UX research and human-computer interaction.',
            profile_image='https://i.pravatar.cc/150?img=4'
        ),
        User(
            username='ethan_bio',
            email='ethan@example.com',
            major='Biology',
            skills='Data Analysis, Research, Python, Scientific Writing',
            bio='Biology student with programming skills, looking to apply data analysis to biological research.',
            profile_image='https://i.pravatar.cc/150?img=5'
        )
    ]

    # Add users to database
    for user in users:
        user.set_password('password123')  # Set a default password for all users
        db.session.add(user)
    db.session.commit()

    # Create sample projects
    projects = [
        Project(
            title='Eco-Friendly Shopping App',
            description='Develop a mobile app that helps users find and purchase eco-friendly products. Features include product scanning, carbon footprint tracking, and sustainable alternatives suggestions.',
            required_skills='UI Design, React Native, Python, Data Analysis',
            creator_id=users[0].id
        ),
        Project(
            title='Mental Health Chatbot',
            description='Create an AI-powered chatbot that provides mental health support and resources. The bot should be able to detect emotional states and suggest appropriate coping mechanisms.',
            required_skills='Python, Natural Language Processing, Psychology, UX Design',
            creator_id=users[3].id
        ),
        Project(
            title='Virtual Art Gallery',
            description='Build a web platform for artists to showcase their work in a virtual 3D gallery space. Users should be able to navigate through different exhibition rooms and interact with artwork.',
            required_skills='3D Modeling, WebGL, UI Design, Digital Art',
            creator_id=users[1].id
        ),
        Project(
            title='Campus Food Waste Tracker',
            description='Develop a system to track and reduce food waste in campus dining halls. Includes data collection, analysis, and visualization of waste patterns.',
            required_skills='Data Analysis, Python, UI Design, Environmental Science',
            creator_id=users[4].id
        ),
        Project(
            title='Student Budget Planner',
            description='Create a mobile app that helps students manage their finances, track expenses, and set savings goals. Includes features for splitting bills and finding student discounts.',
            required_skills='Mobile Development, UI Design, Data Analysis, Business',
            creator_id=users[2].id
        )
    ]

    # Add projects to database
    for project in projects:
        db.session.add(project)
    db.session.commit()

    return 'Sample data created successfully!'

def init_db():
    """Initialize the database with the correct schema"""
    # Drop all existing tables
    db.drop_all()
    # Create all tables with the current schema
    db.create_all()
    # Create sample data
    create_sample_data()
    return "Database initialized successfully!"

@app.route('/init-db')
def init_database():
    """Route to initialize the database"""
    try:
        return init_db()
    except Exception as e:
        return f"Error initializing database: {str(e)}"

if __name__ == '__main__':
    with app.app_context():
        # Always initialize the database to ensure correct schema
        init_db()
    app.run(debug=True) 