import os
import glob

class DotfilesHandler:
    def __init__(self):
        """
        Initializes the DotfilesHandler.
        """
        self.home_directory = os.path.expanduser('~') # Get the user's home directory

    def get_dotfiles_in_home(self):
        """
        Retrieves a list of dotfiles (files starting with '.') in the user's home directory.
        Excludes '.' and '..' and common system directories.
        """
        dotfiles = []
        try:
            # List all files and directories in the home directory
            for item in os.listdir(self.home_directory):
                if item.startswith('.'):
                    full_path = os.path.join(self.home_directory, item)
                    # Exclude '.' and '..' and some common directories/files that are not typical dotfiles
                    if item not in ['.', '..', '.cache', '.config', '.local', '.gnupg', '.ssh', '.pki', '.mozilla', '.thunderbird'] and os.path.isfile(full_path):
                        dotfiles.append(item)
            dotfiles.sort() # Sort the list alphabetically
        except Exception as e:
            print(f"Error retrieving dotfiles: {e}")
        return dotfiles
