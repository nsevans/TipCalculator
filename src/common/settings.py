import json
import sys

app_settings = {}
user_settings = {}

def __load_settings__():

    # How files are accessed passed on app startup type
    # If the app is started via console, then only one '.'
    # is needed to specify file paths
    if len(sys.argv) == 2 and sys.argv[1] == 'console':
        file_path = "./src/config/settings.json"
        run_from_console = True
    # If the app is started via the exe, a second '.'
    # is needed to specify file paths
    else:
        file_path = "../src/config/settings.json"
        run_from_console = False

    with open(file_path) as f:
        data = json.load(f)
        # Load user settings from file into dictionary
        for key, value in data['user_settings'].items():
            user_settings[key] = value
        
        # Load app/server settings from file into dictionary
        for key, value in data['app_settings'].items():
            
            # Check if server was run from console
            if run_from_console:
                # Store everything regularly
                app_settings[key] = value
            else:
                # If not, add an extra '.' at start of each file path
                # for proper pathing
                if isinstance(value, str) and value[0:2] == './':
                    app_settings[key] = '.'+value
                else:
                    app_settings[key] = value

def update_user_setting(key, value):
    """
    Updates an exisiting value of a key or adds a new
    key and value to the user settings

    Args:
        key (string): Location of new data
        value (string): Value of new data
    """
    user_settings[key] = value

def write_updated_settings_to_file():
    """
    Writes the user and app/server settings to the config file 
    to be saved for future sessions
    """
    file_path = "../src/config/settings.json"
    if len(sys.argv) == 2 and sys.argv[1] == 'console':
        file_path = "./src/config/settings.json"

    with open(file_path, "w") as f:
        json.dump({'user_settings': user_settings, 'app_settings': app_settings}, f, indent=4)

__load_settings__()