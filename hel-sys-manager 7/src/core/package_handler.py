import subprocess
import os
import sys
import shutil

try:
    from .pacman_aur_manager import PacmanAURManager
    _PACMAN_AUR_MANAGER_AVAILABLE = True
except ImportError:
    _PACMAN_AUR_MANAGER_AVAILABLE = False
    print("Warning: pacman_aur_manager.py not found. Pacman features will be limited.")


class PackageHandler:
    def __init__(self):
        self.package_manager = self._detect_package_manager()
        if self.package_manager == 'pacman' and _PACMAN_AUR_MANAGER_AVAILABLE:
            self.pacman_handler = PacmanAURManager()
        else:
            self.pacman_handler = None

    def _detect_package_manager(self):
        if sys.platform.startswith('linux'):
            if os.path.exists('/usr/bin/pacman'):
                return 'pacman'
            elif os.path.exists('/usr/bin/apt'):
                return 'apt'
            elif os.path.exists('/usr/bin/dnf'):
                return 'dnf'
            elif os.path.exists('/usr/bin/yum'):
                return 'yum'
        elif sys.platform == 'win32':
            if shutil.which("winget"):
                return 'winget'
            return None
        return None

    def _run_command(self, command, check_error=True):
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=check_error, encoding='utf-8')
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, f"Command failed with error: {e.stderr.strip()}"
        except FileNotFoundError:
            return False, f"Command not found: '{command[0]}'. Is the package manager installed and in PATH?"
        except Exception as e:
            return False, f"An unexpected error occurred: {e}"

    def search_packages(self, query):
        if self.package_manager == 'pacman' and self.pacman_handler:
            packages_data = self.pacman_handler.search_packages(query)
            if isinstance(packages_data, list):
                package_names = [pkg['name'] for pkg in packages_data if 'name' in pkg]
                return True, package_names if package_names else ["No packages found for this query."]
            else:
                return False, packages_data
        elif self.package_manager == 'apt':
            success, output = self._run_command(['apt', 'search', query])
            if success:
                packages = []
                for line in output.split('\n'):
                    if line and not line.startswith('Sorting...') and not line.startswith('Full Text Search...'):
                        try:
                            pkg_name = line.split('/')[0].strip()
                            packages.append(pkg_name)
                        except IndexError:
                            pass
                return True, packages if packages else ["No packages found for this query."]
            return False, output
        elif self.package_manager == 'dnf' or self.package_manager == 'yum':
            success, output = self._run_command([self.package_manager, 'search', query])
            if success:
                packages = []
                for line in output.split('\n'):
                    if line and not line.startswith('Last metadata expiration check:'):
                        try:
                            parts = line.split(' : ')
                            if len(parts) > 0:
                                pkg_name = parts[0].split('.')[0].strip()
                                packages.append(pkg_name)
                        except IndexError:
                            pass
                return True, packages if packages else ["No packages found for this query."]
            return False, output
        elif self.package_manager == 'winget':
            success, output = self._run_command(['winget', 'search', query])
            if success:
                packages = []
                lines = output.splitlines()
                if len(lines) > 1:
                    for line in lines[2:]:
                        parts = line.strip().split('  ')
                        if len(parts) > 0 and parts[0]:
                            packages.append(parts[0].strip())
                return True, packages if packages else ["No packages found for this query."]
            return False, output
        else:
            return False, "No supported package manager detected."

    def get_package_details(self, package_name):
        if self.package_manager == 'pacman' and self.pacman_handler:
            info = self.pacman_handler.get_package_info(package_name)
            if "Error" in info:
                return False, info["Error"]
            
            details_str = ""
            for key, value in info.items():
                details_str += f"{key}: {value}\n"
            return True, details_str
        elif self.package_manager == 'apt':
            success, output = self._run_command(['apt', 'show', package_name])
            if success:
                return True, output
            return False, output
        elif self.package_manager == 'dnf' or self.package_manager == 'yum':
            success, output = self._run_command([self.package_manager, 'info', package_name])
            if success:
                return True, output
            return False, output
        elif self.package_manager == 'winget':
            success, output = self._run_command(['winget', 'show', package_name])
            if success:
                return True, output
            return False, output
        else:
            return False, "No supported package manager detected."

    # دالة جديدة لعرض الحزم المثبتة
    def list_installed_packages(self):
        if self.package_manager == 'pacman' and self.pacman_handler:
            # PacmanAURManager.list_installed_packages() تعيد قائمة من القواميس
            installed_packages_data = self.pacman_handler.list_installed_packages()
            if installed_packages_data:
                package_names = [pkg['name'] for pkg in installed_packages_data if 'name' in pkg]
                return True, package_names
            return False, "Failed to retrieve installed packages from PacmanAURManager."
        elif self.package_manager == 'apt':
            success, output = self._run_command(['apt', 'list', '--installed'])
            if success:
                packages = []
                for line in output.split('\n'):
                    if line.startswith('Listing...'): continue
                    if '/' in line:
                        pkg_name = line.split('/')[0].strip()
                        packages.append(pkg_name)
                return True, packages if packages else ["No installed packages found."]
            return False, output
        elif self.package_manager == 'dnf' or self.package_manager == 'yum':
            success, output = self._run_command([self.package_manager, 'list', 'installed'])
            if success:
                packages = []
                for line in output.split('\n'):
                    if not line or line.startswith('Installed Packages') or line.startswith('Last metadata expiration check:'): continue
                    parts = line.split()
                    if len(parts) > 0:
                        pkg_name = parts[0].split('.')[0].strip()
                        packages.append(pkg_name)
                return True, packages if packages else ["No installed packages found."]
            return False, output
        elif self.package_manager == 'winget':
            success, output = self._run_command(['winget', 'list'])
            if success:
                packages = []
                lines = output.splitlines()
                if len(lines) > 1:
                    for line in lines[2:]:
                        parts = line.strip().split('  ')
                        if len(parts) > 0 and parts[0]:
                            packages.append(parts[0].strip())
                return True, packages if packages else ["No installed packages found."]
            return False, output
        else:
            return False, "No supported package manager detected."

    def install_package(self, package_name):
        if self.package_manager == 'pacman' and self.pacman_handler:
            return_message = self.pacman_handler.install_package(package_name)
            if "Error" in return_message:
                return False, return_message
            return True, return_message
        elif self.package_manager == 'winget':
            return False, "Install not implemented for Winget yet."
        return False, "No supported package manager detected or functionality not implemented."

    def remove_package(self, package_name):
        if self.package_manager == 'pacman' and self.pacman_handler:
            return_message = self.pacman_handler.remove_package(package_name)
            if "Error" in return_message:
                return False, return_message
            return True, return_message
        elif self.package_manager == 'winget':
            return False, "Remove not implemented for Winget yet."
        return False, "No supported package manager detected or functionality not implemented."

    def update_system(self):
        if self.package_manager == 'pacman' and self.pacman_handler:
            return_message = self.pacman_handler.update_system()
            if "Error" in return_message:
                return False, return_message
            return True, return_message
        elif self.package_manager == 'winget':
            return False, "System update not implemented for Winget yet."
        return False, "No supported package manager detected or functionality not implemented."

    def get_package_history(self):
        if self.package_manager == 'pacman' and self.pacman_handler:
            log_path = '/var/log/pacman.log'
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return True, f.read()
                except PermissionError:
                    return False, f"Permission denied to read '{log_path}'. Run the application as root/administrator."
                except Exception as e:
                    return False, f"Error reading '{log_path}': {e}"
            return False, "pacman log file not found at /var/log/pacman.log"
        elif self.package_manager == 'apt':
            log_path = '/var/log/apt/history.log'
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return True, f.read()
                except PermissionError:
                    return False, f"Permission denied to read '{log_path}'. Try running as administrator/root."
                except Exception as e:
                    return False, f"Error reading '{log_path}': {e}"
            return False, "apt history log file not found at /var/log/apt/history.log"
        elif self.package_manager == 'dnf' or self.package_manager == 'yum':
            log_path_dnf = '/var/log/dnf.log'
            log_path_yum = '/var/log/yum.log'
            if os.path.exists(log_path_dnf):
                 try:
                    with open(log_path_dnf, 'r', encoding='utf-8', errors='ignore') as f:
                        return True, f.read()
                 except PermissionError:
                    return False, f"Permission denied to read '{log_path_dnf}'. Try running as administrator/root."
                 except Exception as e:
                    return False, f"Error reading '{log_path_dnf}': {e}"
            elif os.path.exists(log_path_yum):
                 try:
                    with open(log_path_yum, 'r', encoding='utf-8', errors='ignore') as f:
                        return True, f.read()
                 except PermissionError:
                    return False, f"Permission denied to read '{log_path_yum}'. Try running as administrator/root."
                 except Exception as e:
                    return False, f"Error reading '{log_path_yum}': {e}"
            return False, f"{self.package_manager} log file not found."
        elif self.package_manager == 'winget':
            return False, "winget does not have a simple command for history. This feature is not supported yet for winget."
        else:
            return False, "No supported package manager detected."

    def manage_repositories(self, action, repo_details=None):
        return False, "Repository management is an advanced feature and is not yet implemented."
