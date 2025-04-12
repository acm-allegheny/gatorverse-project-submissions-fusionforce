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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    interests = db.Column(db.String(500), default='')
    bio = db.Column(db.Text, default='')
    profile_image = db.Column(db.String(200), default='https://i.pravatar.cc/150?img=0')
    experience_points = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0.0)
    github = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    projects = db.relationship('Project', backref='creator', lazy=True)
    academic_projects = db.relationship('AcademicProject', backref='creator', lazy=True)
    reviews_received = db.relationship('Review', foreign_keys='Review.reviewee_id', backref='reviewee', lazy=True)
    reviews_given = db.relationship('Review', foreign_keys='Review.reviewer_id', backref='reviewer', lazy=True)
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)
    sent_collaboration_requests = db.relationship('CollaborationRequest', foreign_keys='CollaborationRequest.sender_id', backref='sender', lazy=True)

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
    tags = db.Column(db.String(200))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    collaborators = db.Column(db.String(500))  # Store user IDs of collaborators
    max_collaborators = db.Column(db.Integer, default=5)
    reviews = db.relationship('Review', backref='project', lazy=True)
    collaboration_requests = db.relationship('CollaborationRequest', backref='project', lazy=True)

# Academic Project model
class AcademicProject(db.Model):
    """Model for academic projects."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    project_type = db.Column(db.String(20), nullable=False)  # 'comps' or 'gateway'
    department = db.Column(db.String(50), nullable=False)
    advisor = db.Column(db.String(100))
    deadline = db.Column(db.Date)
    requirements = db.Column(db.Text)
    max_collaborators = db.Column(db.Integer)
    current_collaborators = db.Column(db.Integer, default=0)
    tags = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Message model
class Message(db.Model):
    """Model for user messages."""
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_read = db.Column(db.Boolean, default=False)

# Collaboration request model
class CollaborationRequest(db.Model):
    """Model for collaboration requests between users."""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def calculate_skill_match(user_skills, project_skills):
    if not user_skills or not project_skills:
        return 0
    
    # Convert comma-separated strings to sets of cleaned skills
    user_skill_set = {skill.strip().lower() for skill in user_skills.split(',')}
    project_skill_set = {skill.strip().lower() for skill in project_skills.split(',')}
    
    # Calculate intersection and union
    matching_skills = user_skill_set.intersection(project_skill_set)
    total_project_skills = len(project_skill_set)
    
    # Calculate match percentage based on project requirements met
    if total_project_skills == 0:
        return 0
    
    match_percentage = (len(matching_skills) / total_project_skills) * 100
    return round(match_percentage)

# Initialize database
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    search_query = request.args.get('search', '')
    tag_filter = request.args.get('tag', '')
    skill_filter = request.args.get('skill', '')
    sort_by = request.args.get('sort', 'newest')
    
    query = Project.query
    
    if search_query:
        query = query.filter(
            db.or_(
                Project.title.ilike(f'%{search_query}%'),
                Project.description.ilike(f'%{search_query}%')
            )
        )
    
    if tag_filter:
        query = query.filter(Project.tags.ilike(f'%{tag_filter}%'))
    
    if skill_filter:
        query = query.filter(Project.required_skills.ilike(f'%{skill_filter}%'))
    
    if sort_by == 'newest':
        query = query.order_by(Project.created_at.desc())
    elif sort_by == 'oldest':
        query = query.order_by(Project.created_at.asc())
    elif sort_by == 'active':
        query = query.filter(Project.status == 'active').order_by(Project.created_at.desc())
    elif sort_by == 'completed':
        query = query.filter(Project.status == 'completed').order_by(Project.created_at.desc())
    elif sort_by == 'match' and current_user.is_authenticated:
        # Get all projects and sort by match percentage
        projects = query.all()
        projects = sorted(
            projects,
            key=lambda p: calculate_skill_match(current_user.skills, p.required_skills),
            reverse=True
        )
        
        # Get matching users for the current user
        matching_users = []
        if current_user.is_authenticated:
            user_skills = set(skill.strip().lower() for skill in current_user.skills.split(','))
            all_users = User.query.filter(User.id != current_user.id).all()
            matching_users = []
            for user in all_users:
                user_skills2 = set(skill.strip().lower() for skill in user.skills.split(','))
                if user_skills.intersection(user_skills2):
                    matching_users.append(user)
            matching_users = sorted(matching_users, key=lambda u: len(set(skill.strip().lower() for skill in u.skills.split(',')).intersection(user_skills)), reverse=True)
        
        return render_template('index.html',
                            projects=projects,
                            matching_projects=projects[:3],
                            matching_users=matching_users[:3],
                            search_query=search_query,
                            tag_filter=tag_filter,
                            skill_filter=skill_filter,
                            sort_by=sort_by,
                            calculate_match=calculate_skill_match)
    
    projects = query.all()
    
    # Get unique tags and skills for filter dropdowns
    all_projects = Project.query.all()
    unique_tags = set()
    unique_skills = set()
    
    for project in all_projects:
        if project.tags:
            unique_tags.update(tag.strip() for tag in project.tags.split(','))
        if project.required_skills:
            unique_skills.update(skill.strip() for skill in project.required_skills.split(','))
    
    # Get matching projects and users for the current user if authenticated
    matching_projects = []
    matching_users = []
    if current_user.is_authenticated:
        # Get matching projects
        matching_projects = sorted(
            projects,
            key=lambda p: calculate_skill_match(current_user.skills, p.required_skills),
            reverse=True
        )[:3]
        
        # Get matching users
        user_skills = set(skill.strip().lower() for skill in current_user.skills.split(','))
        all_users = User.query.filter(User.id != current_user.id).all()
        for user in all_users:
            user_skills2 = set(skill.strip().lower() for skill in user.skills.split(','))
            if user_skills.intersection(user_skills2):
                matching_users.append(user)
        matching_users = sorted(matching_users, key=lambda u: len(set(skill.strip().lower() for skill in u.skills.split(',')).intersection(user_skills)), reverse=True)[:3]
    
    return render_template('index.html',
                         projects=projects,
                         matching_projects=matching_projects,
                         matching_users=matching_users,
                         search_query=search_query,
                         tag_filter=tag_filter,
                         skill_filter=skill_filter,
                         sort_by=sort_by,
                         unique_tags=sorted(unique_tags),
                         unique_skills=sorted(unique_skills),
                         calculate_match=calculate_skill_match)

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
        project = Project(
            title=request.form['title'],
            description=request.form['description'],
            tags=request.form['tags'],
            required_skills=request.form['required_skills'],
            creator_id=current_user.id,
            max_collaborators=int(request.form.get('max_collaborators', 5))
        )
        db.session.add(project)
        db.session.commit()
        flash('Project created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('create_project.html')

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project, calculate_match=calculate_skill_match)

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.username = request.form['username']
        current_user.major = request.form['major']
        current_user.skills = request.form['skills']
        current_user.interests = request.form['interests']
        current_user.bio = request.form['bio']
        current_user.github = request.form['github']
        current_user.linkedin = request.form['linkedin']
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile', username=current_user.username))
    
    return render_template('edit_profile.html')

@app.route('/messages')
@login_required
def messages():
    received_messages = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.created_at.desc()).all()
    sent_messages = Message.query.filter_by(sender_id=current_user.id).order_by(Message.created_at.desc()).all()
    return render_template('messages.html', 
                         received_messages=received_messages,
                         sent_messages=sent_messages)

@app.route('/send_message/<int:receiver_id>', methods=['GET', 'POST'])
@login_required
def send_message(receiver_id):
    receiver = User.query.get_or_404(receiver_id)
    
    if request.method == 'POST':
        message = Message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            content=request.form['message']
        )
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('messages'))
    
    return render_template('send_message.html', receiver=receiver)

@app.route('/send_new_message', methods=['GET', 'POST'])
@login_required
def send_new_message():
    users = User.query.filter(User.id != current_user.id).all()
    
    if request.method == 'POST':
        receiver_id = request.form.get('receiver_id')
        content = request.form.get('message')
        
        message = Message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            content=content
        )
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('messages'))
    
    return render_template('send_message.html', users=users)

@app.route('/user_messages/<int:user_id>', methods=['GET'])
@login_required
def user_messages(user_id):
    other_user = User.query.get_or_404(user_id)
    
    # Get all messages between current user and other user
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at).all()
    
    # Mark unread messages as read
    unread_messages = Message.query.filter_by(
        sender_id=user_id,
        receiver_id=current_user.id,
        is_read=False
    ).all()
    
    for message in unread_messages:
        message.is_read = True
    
    db.session.commit()
    
    return render_template('user_messages.html', messages=messages, other_user=other_user)

@app.route('/send_direct_message/<int:receiver_id>', methods=['POST'])
@login_required
def send_direct_message(receiver_id):
    content = request.form.get('message')
    
    message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=content
    )
    
    db.session.add(message)
    db.session.commit()
    
    return redirect(url_for('user_messages', user_id=receiver_id))

@app.route('/project/<int:project_id>/join', methods=['POST'])
@login_required
def join_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if project.creator_id == current_user.id:
        flash("You can't join your own project!", 'warning')
        return redirect(url_for('project_detail', project_id=project_id))
    
    collaborators = project.collaborators.split(',') if project.collaborators else []
    if str(current_user.id) in collaborators:
        flash("You're already a collaborator on this project!", 'warning')
        return redirect(url_for('project_detail', project_id=project_id))
    
    collaborators.append(str(current_user.id))
    project.collaborators = ','.join(collaborators)
    db.session.commit()
    
    flash('Successfully joined the project!', 'success')
    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check if user is the owner
    if project.creator_id != current_user.id:
        flash('You can only edit your own projects!', 'danger')
        return redirect(url_for('project_detail', project_id=project_id))
    
    if request.method == 'POST':
        project.title = request.form['title']
        project.description = request.form['description']
        project.tags = request.form['tags']
        project.required_skills = request.form['required_skills']
        project.status = request.form['status']
        project.max_collaborators = int(request.form.get('max_collaborators', 5))
        
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))
    
    return render_template('edit_project.html', project=project)

@app.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check if user is the owner
    if project.creator_id != current_user.id:
        flash('You can only delete your own projects!', 'danger')
        return redirect(url_for('project_detail', project_id=project_id))
    
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/project/<int:project_id>/collaborators')
@login_required
def project_collaborators(project_id):
    project = Project.query.get_or_404(project_id)
    collaborators = []
    
    if project.collaborators:
        collaborator_ids = project.collaborators.split(',')
        collaborators = User.query.filter(User.id.in_(collaborator_ids)).all()
    
    return render_template('project_collaborators.html', 
                         project=project,
                         collaborators=collaborators)

@app.route('/academic_projects')
def academic_projects():
    project_type = request.args.get('type', 'all')
    department = request.args.get('department', 'all')
    
    query = AcademicProject.query
    
    if project_type != 'all':
        query = query.filter_by(project_type=project_type)
    if department != 'all':
        query = query.filter_by(department=department)
        
    projects = query.order_by(AcademicProject.created_at.desc()).all()
    departments = db.session.query(AcademicProject.department).distinct().all()
    departments = [d[0] for d in departments]
    
    return render_template('academic_projects.html', 
                         projects=projects, 
                         departments=departments,
                         selected_type=project_type,
                         selected_dept=department)

@app.route('/academic_project/new', methods=['GET', 'POST'])
@login_required
def new_academic_project():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        project_type = request.form.get('project_type')
        department = request.form.get('department')
        advisor = request.form.get('advisor')
        deadline = datetime.strptime(request.form.get('deadline'), '%Y-%m-%d').date()
        requirements = request.form.get('requirements')
        max_collaborators = int(request.form.get('max_collaborators'))
        tags = request.form.get('tags')
        
        project = AcademicProject(
            title=title,
            description=description,
            project_type=project_type,
            department=department,
            advisor=advisor,
            deadline=deadline,
            requirements=requirements,
            max_collaborators=max_collaborators,
            tags=tags,
            user_id=current_user.id
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash('Your academic project has been created!', 'success')
        return redirect(url_for('academic_projects'))
    
    return render_template('new_academic_project.html')

@app.route('/academic_project/<int:project_id>')
def academic_project_detail(project_id):
    project = AcademicProject.query.get_or_404(project_id)
    return render_template('academic_project_detail.html', project=project)

@app.route('/academic_project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_academic_project(project_id):
    project = AcademicProject.query.get_or_404(project_id)
    
    if project.user_id != current_user.id:
        flash('You can only edit your own projects!', 'danger')
        return redirect(url_for('academic_projects'))
    
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.department = request.form.get('department')
        project.advisor = request.form.get('advisor')
        project.deadline = datetime.strptime(request.form.get('deadline'), '%Y-%m-%d').date()
        project.requirements = request.form.get('requirements')
        project.max_collaborators = int(request.form.get('max_collaborators'))
        project.tags = request.form.get('tags')
        project.status = request.form.get('status')
        
        db.session.commit()
        flash('Your academic project has been updated!', 'success')
        return redirect(url_for('academic_project_detail', project_id=project.id))
    
    return render_template('edit_academic_project.html', project=project)

@app.route('/project/<int:project_id>/collaborate', methods=['POST'])
@login_required
def request_collaboration(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check if user already has a pending request
    existing_request = CollaborationRequest.query.filter_by(
        project_id=project_id,
        sender_id=current_user.id,
        status='pending'
    ).first()
    
    if existing_request:
        flash('You already have a pending request for this project.', 'warning')
        return redirect(url_for('project_detail', project_id=project_id))
    
    # Check if project is full
    if project.collaborators:
        current_collaborators = len(project.collaborators.split(','))
        if current_collaborators >= project.max_collaborators:
            flash('This project has reached its maximum number of collaborators.', 'warning')
            return redirect(url_for('project_detail', project_id=project_id))
    
    message = request.form.get('message', '')
    collab_request = CollaborationRequest(
        project_id=project_id,
        sender_id=current_user.id,
        message=message
    )
    
    db.session.add(collab_request)
    db.session.commit()
    
    # Send notification to project owner
    flash('Your collaboration request has been sent!', 'success')
    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/collaboration-requests')
@login_required
def collaboration_requests():
    # Get requests for user's projects
    owned_projects = Project.query.filter_by(creator_id=current_user.id).all()
    project_ids = [p.id for p in owned_projects]
    received_requests = CollaborationRequest.query.filter(
        CollaborationRequest.project_id.in_(project_ids)
    ).order_by(CollaborationRequest.created_at.desc()).all()
    
    # Get requests sent by user
    sent_requests = CollaborationRequest.query.filter_by(
        sender_id=current_user.id
    ).order_by(CollaborationRequest.created_at.desc()).all()
    
    return render_template('collaboration_requests.html',
                         received_requests=received_requests,
                         sent_requests=sent_requests)

@app.route('/collaboration-request/<int:request_id>/<action>')
@login_required
def handle_collaboration_request(request_id, action):
    collab_request = CollaborationRequest.query.get_or_404(request_id)
    project = collab_request.project
    
    # Verify the current user owns the project
    if project.creator_id != current_user.id:
        flash('You are not authorized to handle this request.', 'danger')
        return redirect(url_for('collaboration_requests'))
    
    if action == 'accept':
        # Add collaborator to project
        current_collaborators = project.collaborators.split(',') if project.collaborators else []
        current_collaborators.append(str(collab_request.sender_id))
        project.collaborators = ','.join(filter(None, current_collaborators))
        collab_request.status = 'accepted'
        flash('Collaboration request accepted!', 'success')
        
    elif action == 'reject':
        collab_request.status = 'rejected'
        flash('Collaboration request rejected.', 'info')
    
    db.session.commit()
    return redirect(url_for('collaboration_requests'))

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
    collaborators = project.collaborators.split(',') if project.collaborators else []
    for collaborator_id in collaborators:
        if collaborator_id and int(collaborator_id) != current_user.id:  # Don't review yourself
            review = Review(
                reviewer_id=current_user.id,
                reviewee_id=int(collaborator_id),
                project_id=project_id,
                rating=rating,
                comment=comment,
                feedback_tags=feedback_tags
            )
            db.session.add(review)
            user = User.query.get(int(collaborator_id))
            user.update_experience_points()
            user.update_average_rating()
    
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
            tags='Mobile, Sustainability, E-commerce',
            creator_id=users[0].id
        ),
        Project(
            title='Mental Health Chatbot',
            description='Create an AI-powered chatbot that provides mental health support and resources. The bot should be able to detect emotional states and suggest appropriate coping mechanisms.',
            required_skills='Python, Natural Language Processing, Psychology, UX Design',
            tags='AI, Healthcare, Mental Health',
            creator_id=users[3].id
        ),
        Project(
            title='Virtual Art Gallery',
            description='Build a web platform for artists to showcase their work in a virtual 3D gallery space. Users should be able to navigate through different exhibition rooms and interact with artwork.',
            required_skills='3D Modeling, WebGL, UI Design, Digital Art',
            tags='3D, Art, Web Development',
            creator_id=users[1].id
        ),
        Project(
            title='Campus Food Waste Tracker',
            description='Develop a system to track and reduce food waste in campus dining halls. Includes data collection, analysis, and visualization of waste patterns.',
            required_skills='Data Analysis, Python, UI Design, Environmental Science',
            tags='Sustainability, Data Visualization, Campus',
            creator_id=users[4].id
        ),
        Project(
            title='Student Budget Planner',
            description='Create a mobile app that helps students manage their finances, track expenses, and set savings goals. Includes features for splitting bills and finding student discounts.',
            required_skills='Mobile Development, UI Design, Data Analysis, Business',
            tags='Finance, Mobile, Education',
            creator_id=users[2].id
        )
    ]

    # Add projects to database
    for project in projects:
        db.session.add(project)
    db.session.commit()

    # Create sample academic projects
    academic_projects = [
        AcademicProject(
            title='Machine Learning for Climate Prediction',
            description='Research project to develop machine learning models for predicting climate patterns based on historical data.',
            project_type='comps',
            department='Computer Science',
            advisor='Dr. Smith',
            deadline=datetime(2023, 12, 15).date(),
            requirements='Python, Machine Learning, Data Analysis',
            max_collaborators=4,
            tags='AI, Climate Science, Research',
            user_id=users[0].id
        ),
        AcademicProject(
            title='Digital Art Exhibition',
            description='Create a digital art exhibition for the university art gallery, exploring the intersection of technology and traditional art forms.',
            project_type='gateway',
            department='Art',
            advisor='Prof. Johnson',
            deadline=datetime(2023, 11, 30).date(),
            requirements='Digital Art, 3D Modeling, Exhibition Design',
            max_collaborators=3,
            tags='Art, Exhibition, Digital',
            user_id=users[1].id
        )
    ]

    # Add academic projects to database
    for project in academic_projects:
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
    app.run(debug=True, port=5001) 