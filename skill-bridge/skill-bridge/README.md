# SkillBridge

SkillBridge is a web application designed to help Allegheny College students find collaborators across different disciplines for projects, research, competitions, and club events.

## Features

- User registration and authentication
- Project creation and browsing
- Skill-based matching
- User profiles with major and skills information
- Collaboration requests
- Modern, responsive UI

## Tech Stack

- Backend: Python/Flask
- Database: SQLite
- Frontend: HTML, CSS, Bootstrap 5
- Authentication: Flask-Login

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. Register a new account or login
2. Create a profile with your major and skills
3. Browse existing projects or create your own
4. Connect with other students for collaboration

## Project Structure

```
skill-bridge/
├── main.py              # Main application file
├── requirements.txt     # Project dependencies
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── create_project.html
│   ├── project_detail.html
│   └── profile.html
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 