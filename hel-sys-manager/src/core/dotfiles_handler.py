import os
import glob
import shutil # إضافة مكتبة shutil للنسخ والتحريك

class DotfilesHandler:
    def __init__(self):
        self.home_directory = os.path.expanduser('~')

    def get_dotfiles_in_home(self):
        dotfiles = []
        try:
            for item in os.listdir(self.home_directory):
                full_path = os.path.join(self.home_directory, item)
                if item.startswith('.') and item not in ['.', '..']:
                    if item not in ['.cache', '.config', '.local', '.gnupg', '.ssh', '.pki', '.mozilla', '.thunderbird']:
                        dotfiles.append(item)
            dotfiles.sort()
        except Exception as e:
            print(f"Error retrieving dotfiles: {e}")
        return dotfiles

    def create_symlink(self, source_path, link_path):
        try:
            if os.path.exists(link_path):
                return False, f"Error: A file or directory already exists at '{link_path}'."
            
            if not os.path.exists(source_path):
                return False, f"Error: Source file '{source_path}' does not exist."

            os.symlink(source_path, link_path)
            return True, f"Symbolic link created successfully:\n'{link_path}' -> '{source_path}'"
        except OSError as e:
            return False, f"Failed to create symbolic link: {e}"
        except Exception as e:
            return False, f"An unexpected error occurred: {e}"

    # دالة جديدة للنسخ الاحتياطي
    # New function for backing up
    def backup_dotfiles(self, dotfile_names, backup_directory):
        """
        ينسخ ملفات الـ Dotfiles المحددة إلى دليل النسخ الاحتياطي.
        Copies specified dotfiles to the backup directory.

        Args:
            dotfile_names (list): قائمة بأسماء ملفات الـ Dotfiles للنسخ الاحتياطي (مثال: ['.bashrc', '.vimrc']).
            backup_directory (str): المسار الكامل للدليل الذي سيتم حفظ النسخ الاحتياطية فيه.

        Returns:
            tuple: (bool, str) - True إذا نجح النسخ مع رسالة، False إذا فشل مع رسالة خطأ.
        """
        if not os.path.isdir(backup_directory):
            try:
                os.makedirs(backup_directory) # إنشاء الدليل إذا لم يكن موجودًا
            except OSError as e:
                return False, f"Failed to create backup directory '{backup_directory}': {e}"

        successful_backups = []
        failed_backups = []

        for name in dotfile_names:
            source_path = os.path.join(self.home_directory, name)
            destination_path = os.path.join(backup_directory, name)
            
            try:
                if os.path.isfile(source_path) or os.path.islink(source_path): # انسخ الملفات والروابط الرمزية
                    shutil.copy2(source_path, destination_path) # copy2 يحافظ على metadata الملف
                    successful_backups.append(name)
                elif os.path.isdir(source_path): # إذا كان مجلد (مثل .config)
                    # يمكننا إضافة خيارات لضغط المجلدات لاحقًا
                    shutil.copytree(source_path, destination_path, dirs_exist_ok=True) # dirs_exist_ok تتطلب بايثون 3.8+
                    successful_backups.append(name)
                else:
                    failed_backups.append(f"{name} (not a file or directory)")
            except Exception as e:
                failed_backups.append(f"{name} ({e})")
        
        if successful_backups:
            message = f"Successfully backed up: {', '.join(successful_backups)} to '{backup_directory}'."
            if failed_backups:
                message += f"\nFailed to backup: {', '.join(failed_backups)}"
            return True, message
        else:
            return False, f"No dotfiles were backed up. Failed: {', '.join(failed_backups)}"

    # دالة جديدة للاستعادة
    # New function for restoring
    def restore_dotfiles(self, source_directory, target_directory):
        """
        يستعيد ملفات الـ Dotfiles من دليل النسخ الاحتياطي إلى الدليل المستهدف (غالباً دليل المنزل).
        Restores dotfiles from a backup directory to the target directory (usually home directory).

        Args:
            source_directory (str): المسار إلى الدليل الذي يحتوي على ملفات النسخ الاحتياطي.
            target_directory (str): المسار إلى الدليل الذي سيتم استعادة الملفات إليه.

        Returns:
            tuple: (bool, str) - True إذا نجحت الاستعادة مع رسالة، False إذا فشلت مع رسالة خطأ.
        """
        if not os.path.isdir(source_directory):
            return False, f"Error: Source directory '{source_directory}' does not exist or is not a directory."
        
        restored_files = []
        failed_restores = []

        for item in os.listdir(source_directory):
            source_path = os.path.join(source_directory, item)
            destination_path = os.path.join(target_directory, item)
            
            # فقط استعد الملفات أو الروابط الرمزية التي تبدأ بنقطة
            if not item.startswith('.') or item in ['.', '..']: # تجاهل . و .. وغيرها من غير الدوتفايلز
                 continue

            try:
                if os.path.isfile(source_path) or os.path.islink(source_path):
                    # قم بالنسخ ولكن احذر من الكتابة فوق الملفات الموجودة
                    # يمكننا إضافة تأكيد للمستخدم هنا إذا أردنا
                    if os.path.exists(destination_path) and not os.path.samefile(source_path, destination_path):
                        # للحفاظ على أمان المستخدم، يمكننا طلب تأكيد أو إعادة تسمية الملف القديم
                        # حالياً، سنكتب فوقه، لكن هذا يمكن أن يكون خطيراً.
                        # للحصول على تحكم أفضل، يمكننا إضافة خيارات في الواجهة.
                        shutil.copy2(source_path, destination_path)
                        restored_files.append(f"{item} (overwritten)")
                    else:
                        shutil.copy2(source_path, destination_path)
                        restored_files.append(item)
                elif os.path.isdir(source_path):
                    # نسخ المجلدات
                    shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
                    restored_files.append(f"{item} (directory)")
            except Exception as e:
                failed_restores.append(f"{item} ({e})")
        
        if restored_files:
            message = f"Successfully restored: {', '.join(restored_files)} from '{source_directory}'."
            if failed_restores:
                message += f"\nFailed to restore: {', '.join(failed_restores)}"
            return True, message
        else:
            return False, f"No dotfiles were restored. Failed: {', '.join(failed_restores)}"
