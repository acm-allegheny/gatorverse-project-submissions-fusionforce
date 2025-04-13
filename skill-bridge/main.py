import sys
import os
import importlib.util

# Get the absolute path to the Flask app and its directory
app_path = os.path.join(os.path.dirname(__file__), 'skill-bridge', 'main.py')
app_dir = os.path.dirname(app_path)

# Create instance directory if it doesn't exist
instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
if not os.path.exists(instance_dir):
    os.makedirs(instance_dir)

# Set the working directory to the app directory for proper imports and file paths
os.chdir(app_dir)

# Import the app from the module
spec = importlib.util.spec_from_file_location("flask_app", app_path)
flask_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flask_app)

# Get the app object
app = flask_app.app

if __name__ == '__main__':
    # Ensure the instance path is accessible to the app
    app.instance_path = instance_dir
    app.run(debug=True, port=5001) 