import os
import glob

class DotfilesHandler:
    def __init__(self):
        self.home_directory = os.path.expanduser('~')

    def get_dotfiles_in_home(self):
        dotfiles = []
        try:
            for item in os.listdir(self.home_directory):
                full_path = os.path.join(self.home_directory, item)
                # Include dotfiles and symbolic links that point to other locations (islink)
                # Also, include regular dotfiles
                if item.startswith('.') and item not in ['.', '..']:
                    # Exclude common system directories/files that are not typical dotfiles
                    if item not in ['.cache', '.config', '.local', '.gnupg', '.ssh', '.pki', '.mozilla', '.thunderbird']:
                        dotfiles.append(item)
            dotfiles.sort()
        except Exception as e:
            print(f"Error retrieving dotfiles: {e}")
        return dotfiles

    # دالة جديدة لإنشاء رابط رمزي
    # New function for creating a symbolic link
    def create_symlink(self, source_path, link_path):
        """
        ينشئ رابطًا رمزيًا (symlink) من source_path إلى link_path.
        Creates a symbolic link from source_path to link_path.

        Args:
            source_path (str): المسار إلى الملف الأصلي.
            link_path (str): المسار الذي سيتم إنشاء الرابط الرمزي عنده.

        Returns:
            tuple: (bool, str) - True إذا نجح الإنشاء مع رسالة، False إذا فشل مع رسالة خطأ.
        """
        try:
            # التحقق مما إذا كان الرابط الرمزي المستهدف موجودًا بالفعل
            if os.path.exists(link_path):
                return False, f"Error: A file or directory already exists at '{link_path}'."
            
            # التحقق مما إذا كان الملف المصدر موجودًا
            if not os.path.exists(source_path):
                return False, f"Error: Source file '{source_path}' does not exist."

            # إنشاء الرابط الرمزي
            os.symlink(source_path, link_path)
            return True, f"Symbolic link created successfully:\n'{link_path}' -> '{source_path}'"
        except OSError as e:
            # التعامل مع الأخطاء المتعلقة بأذونات الملفات أو الأخطاء الأخرى
            return False, f"Failed to create symbolic link: {e}"
        except Exception as e:
            return False, f"An unexpected error occurred: {e}"
