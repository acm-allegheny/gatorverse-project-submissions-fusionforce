import sys
import os

# Add the skill-bridge directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'skill-bridge'))

from main import app

if __name__ == '__main__':
    app.run(debug=True, port=5001) 