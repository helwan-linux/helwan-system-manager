import subprocess
import os
import sys

class PacmanAURManager:
    """
    كلاس لإدارة حزم Arch Linux باستخدام pacman (ويمكن التوسع لاحقاً لـ AUR).
    Class for managing Arch Linux packages using pacman (and potentially AUR later).
    """

    @staticmethod
    def _run_privileged_command(full_command_with_args):
        """
        دالة مساعدة لتشغيل الأوامر بصلاحيات الجذر باستخدام pkexec.
        تستقبل الأمر كاملاً مع وسائطه.
        """
        pkexec_path = "/usr/bin/pkexec"
        
        auth_commands_map = {
            "pkexec": [pkexec_path],
            "gksu": ["gksu"],
            "kdesu": ["kdesu", "-c"],
            "lxsu": ["lxsu", "-s"],
        }

        chosen_auth_command = None
        auth_prefix = []

        for tool, prefix_list in auth_commands_map.items():
            if os.path.exists(prefix_list[0]):
                chosen_auth_command = tool
                auth_prefix = prefix_list
                break
        
        if not chosen_auth_command:
            print("Error: No suitable graphical authentication tool (pkexec, gksu, kdesu, lxsu) found.")
            return "Error: No graphical authentication tool found. Please install pkexec, gksu, or kdesu."

        # بناء الأمر النهائي
        if chosen_auth_command == "pkexec":
            command = auth_prefix + ["--disable-internal-agent"] + full_command_with_args
            
        elif chosen_auth_command == "kdesu":
            command = auth_prefix + [" ".join(full_command_with_args)]
        else: # gksu, lxsu
            command = auth_prefix + full_command_with_args
            
        try:
            print(f"Executing privileged command via {chosen_auth_command}: {' '.join(command)}") 
            
            # التعديل هنا: استخدام Popen ومراقبة الـ stdout و stderr بشكل مباشر
            # هذا يمنحنا تحكمًا أفضل في التقاط المخرجات، خاصة مع البرامج التي تطلب مصادقة
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1 # لتلقي الـ output أولاً بأول
            )
            
            stdout_output = []
            stderr_output = []

            # قراءة الـ output في الوقت الفعلي
            # يمكن تعديل هذه الحلقة لعرض الـ output في الواجهة الرسومية أيضاً
            while True:
                line_stdout = process.stdout.readline()
                line_stderr = process.stderr.readline()

                if line_stdout:
                    stdout_output.append(line_stdout.strip())
                    print("Privileged command stdout:", line_stdout.strip())
                if line_stderr:
                    stderr_output.append(line_stderr.strip())
                    print("Privileged command stderr:", line_stderr.strip())

                if not line_stdout and not line_stderr and process.poll() is not None:
                    break

            # الانتظار حتى تنتهي العملية تماماً
            process.wait()
            
            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    returncode=process.returncode,
                    cmd=command,
                    output="".join(stdout_output),
                    stderr="".join(stderr_output)
                )
            
            return "\n".join(stdout_output)
        except subprocess.CalledProcessError as e:
            error_message = f"Error running privileged command: {e}\n"
            error_message += f"Command: {' '.join(command)}\n"
            error_message += f"Stdout: {e.output.strip()}\n"
            error_message += f"Stderr: {e.stderr.strip()}"
            
            if "authentication failed" in e.stderr.lower() or "not authorized" in e.stderr.lower() or "polkit-agent-helper" in e.stderr.lower():
                error_message += "\nOperation canceled or authentication failed. Root privileges are required, or no graphical authentication agent is running."
            elif "No protocol specified" in e.stderr or "cannot open display" in e.stderr.lower():
                error_message += "\nError: Cannot open display. This usually means the application is being run without access to the graphical environment."
            elif "not found" in e.stderr.lower() and "/usr/bin/pacman" in e.stderr.lower():
                 error_message += "\n/usr/bin/pacman command not found. Is Arch Linux installed correctly?"
            elif "error: could not open file /etc/pacman.conf" in e.stderr.lower() or \
                 "error: failed to initialize alpm library" in e.stderr.lower():
                error_message += "\nPacman failed to initialize. This might indicate an issue with the environment or a corrupted pacman database."
            elif "error: no operation specified" in e.stderr.lower():
                 error_message += "\nPacman operation not specified. This indicates an internal error in command construction. Please check the passed arguments."

            print(error_message) 
            return f"Error: {error_message}"
        except FileNotFoundError:
            return f"Error: Authentication command '{command[0]}' or '/usr/bin/pacman' not found. Please ensure pkexec (or gksu/kdesu) and pacman are installed."

    @staticmethod
    def _run_pacman_command(command_args, requires_sudo=False):
        """
        دالة مساعدة لتشغيل أوامر pacman.
        تستخدم _run_privileged_command إذا كانت صلاحيات الجذر مطلوبة.
        """
        # المسار الكامل لأمر pacman
        PACMAN_FULL_PATH = "/usr/bin/pacman" 

        if requires_sudo:
            # هنا نرسل المسار الكامل لـ pacman كأول عنصر، ثم باقي الـ arguments من command_args
            full_command = [PACMAN_FULL_PATH] + command_args 
            return PacmanAURManager._run_privileged_command(full_command)
        else:
            try:
                result = subprocess.run(
                    ["pacman"] + command_args,
                    capture_output=True,
                    text=True,
                    check=True,
                    shell=False
                )
                return result.stdout.strip()
            except subprocess.CalledProcessError as e:
                error_message = f"Error running pacman command: {e}\n"
                error_message += f"Stdout: {e.stdout.strip()}\n"
                error_message += f"Stderr: {e.stderr.strip()}"
                print(error_message)
                return f"Error: {error_message}"
            except FileNotFoundError:
                return "Error: pacman command not found. Is Arch Linux installed?"

    @staticmethod
    def list_installed_packages():
        """
        جلب قائمة بجميع الحزم المثبتة.
        لا تحتاج صلاحيات الجذر.
        """
        output = PacmanAURManager._run_pacman_command(["-Qq"])
        if output.startswith("Error:"):
            return []
        return output.split('\n')

    @staticmethod
    def search_packages(query):
        """
        البحث عن حزم في المستودعات الرسمية.
        لا تحتاج صلاحيات الجذر.
        """
        if not query:
            return []
        output = PacmanAURManager._run_pacman_command(["-Ss", "--color=never", query])
        if output.startswith("Error:"):
            return []

        packages = []
        current_package = {}
        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith("community/") or line.startswith("core/") or \
               line.startswith("extra/") or line.startswith("multilib/"):
                if current_package:
                    packages.append(current_package)
                parts = line.split('/')
                repo_name = parts[0]
                pkg_info = parts[1].split(' ', 1)
                pkg_name = pkg_info[0]
                pkg_version = pkg_info[1].strip('()') if len(pkg_info) > 1 else ""

                current_package = {"repo": repo_name, "name": pkg_name, "version": pkg_version}
                current_package["description"] = ""
            elif line.startswith("Description:"):
                current_package["description"] = line.replace("Description:", "").strip()

        if current_package:
            packages.append(current_package)
        return packages

    @staticmethod
    def get_package_info(package_name):
        """
        جلب معلومات مفصلة عن حزمة معينة.
        لا تحتاج صلاحيات الجذر.
        """
        output = PacmanAURManager._run_pacman_command(["-Si", package_name])
        if output.startswith("Error:"):
            output_installed = PacmanAURManager._run_pacman_command(["-Qi", package_name])
            if output_installed.startswith("Error:"):
                return {"Error": "Package not found or not installed."}
            output = output_installed

        info = {}
        for line in output.split('\n'):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info

    @staticmethod
    def install_package(package_name):
        """
        تثبيت حزمة معينة. تتطلب صلاحيات الجذر.
        """
        return PacmanAURManager._run_pacman_command(["-S", "--noconfirm", package_name], requires_sudo=True)

    @staticmethod
    def remove_package(package_name):
        """
        حذف حزمة معينة. تتطلب صلاحيات الجذر.
        """
        # -Rns: حذف الحزمة مع التبعيات غير المستخدمة والملفات الإعدادية
        return PacmanAURManager._run_pacman_command(["-Rns", "--noconfirm", package_name], requires_sudo=True)

    @staticmethod
    def update_system():
        """
        تحديث النظام بالكامل. تتطلب صلاحيات الجذر.
        """
        # هنا أمر pacman الفعلي (بدون كلمة 'pacman' نفسها)
        return PacmanAURManager._run_pacman_command(["-Syu", "--noconfirm"], requires_sudo=True)
