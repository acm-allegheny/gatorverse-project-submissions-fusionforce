# SkillBridge

SkillBridge is a web application designed to help Allegheny College students find collaborators across different disciplines for projects, research, competitions, and club events.

## Motivation

SkillBridge was created to address several challenges faced by students at Allegheny College:

- **Cross-disciplinary Collaboration:** Students often struggle to find peers with complementary skills outside their majors or departments.
- **Project Team Formation:** Finding the right collaborators with specific skills for academic or personal projects can be difficult.
- **Skills Discovery:** Many students have valuable skills that aren't visible to the broader campus community.
- **Connection Building:** Creating meaningful connections across departments and disciplines enhances the educational experience.
- **Resource Optimization:** The platform helps match students based on their skills and interests, making project work more efficient and effective.

By creating this centralized platform, SkillBridge aims to foster collaboration, innovation, and community building across the entire campus. It serves as a bridge between students from different majors, allowing them to leverage their diverse skills and perspectives for more successful and impactful projects.

## Features

- **User Management**
  - Registration with skill checkboxes and "other skills" option
  - Login/logout functionality
  - Profile management with editable skills and social links
  - Experience points and ratings system

- **Project System**
  - Project creation with multiple skills and tags support
  - Detailed project view with collaboration options
  - Project editing and status management
  - Completion tracking and reviewing

- **Collaboration System**
  - Request to collaborate with message to project owner
  - Accept/reject collaboration requests
  - Team management for projects
  - Pending request tracking

- **Messaging System**
  - Direct messaging between users
  - Conversation view with real-time message status
  - Unread message notifications

- **Search & Matching**
  - Skill-based matching algorithm
  - Advanced search with filters
  - Project and user recommendations
  - Major and tag filtering

- **Academic Projects**
  - Separate section for academic projects
  - Department and type filtering

## Tech Stack

- **Backend:** Python 3 with Flask framework
- **Database:** SQLite with SQLAlchemy ORM
- **Frontend:** HTML, CSS, JavaScript
- **UI Framework:** Bootstrap 5
- **Icons:** Bootstrap Icons
- **Authentication:** Flask-Login
- **Forms:** Flask-WTF and WTForms

## Development Tools

- **AI Assistance:** Cursor AI's agent (Claude 3.5 and 3.7 Sonnet) was heavily used for code generation, debugging, and feature implementation
- **Version Control:** Git and GitHub for code management
- **IDE:** VS Code with Flask extensions

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/skill-bridge.git
   cd skill-bridge
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r skill-bridge/requirements.txt
   ```

4. Run the application:

   ```bash
   cd skill-bridge
   python main.py
   ```

5. Access the application in your browser:

   ```text
   http://localhost:5001
   ```

## Usage Guide

### For Students

1. **Register an Account**
   - Sign up with your email, username, and password
   - Select your major and skills from the checkbox list
   - Add any additional skills not listed

2. **Create or Browse Projects**
   - Create your own project with required skills and description
   - Browse existing projects with filters by skills, tags, or status
   - See projects that match your skills on the homepage

3. **Collaborate on Projects**
   - Request to collaborate on interesting projects
   - Accept collaboration requests for your projects
   - Message team members directly

4. **Academic Projects**
   - Browse academic projects by department
   - Filter by project type (comps, gateway, etc.)

### For Administrators

1. Initialize the database:

   ```text
   http://localhost:5001/init-db
   ```

2. Reset the database (if needed):

   ```text
   http://localhost:5001/reset-db
   ```

## Project Structure

```text
skill-bridge/
├── main.py                # Main application file
├── requirements.txt       # Project dependencies
├── static/                # Static files
│   ├── css/               # CSS stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Images and icons
├── templates/             # HTML templates
│   ├── base.html          # Base template with navigation
│   ├── index.html         # Homepage
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── profile.html       # User profile
│   ├── edit_profile.html  # Edit profile page
│   ├── create_project.html # Create project
│   ├── project_detail.html # Project details
│   ├── messages.html      # Messages inbox
│   ├── collaboration_requests.html # Collaboration requests
│   └── ... (additional templates)
└── README.md              # This documentation
```

## Troubleshooting

- **Database Issues:** If you encounter database errors, try initializing or resetting the database using the provided routes.
- **Python Environment:** Make sure you're using Python 3.6+ and have all dependencies installed.
- **Running the Server:** If you have port conflicts, you can change the port in the `main.py` file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
