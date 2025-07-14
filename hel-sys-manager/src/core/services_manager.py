import subprocess

class ServicesManager:
    """
    كلاس لإدارة خدمات systemd.
    Class for managing systemd services.
    """

    @staticmethod
    def _run_systemctl_command(command_args, check_output=True):
        """
        دالة مساعدة لتشغيل أوامر systemctl.
        Helper function to run systemctl commands.
        """
        try:
            result = subprocess.run(
                ["systemctl"] + command_args,
                capture_output=True,
                text=True,
                check=True, # يرفع CalledProcessError إذا كان رمز الخروج غير صفري
                shell=False # لا تستخدم shell لتجنب مشاكل الأمان
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error running systemctl command: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            return f"Error: {e.stderr.strip()}"
        except FileNotFoundError:
            return "Error: systemctl command not found. Is systemd installed?"

    @staticmethod
    def list_services():
        """
        جلب قائمة بجميع خدمات systemd النشطة وغير النشطة.
        Fetches a list of all systemd services (active and inactive).
        """
        output = ServicesManager._run_systemctl_command(["list-units", "--type=service", "--all", "--no-pager"])
        services = []
        if output.startswith("Error:"):
            return services # إرجاع قائمة فارغة في حالة الخطأ

        lines = output.split('\n')
        # تخطي أول سطرين (العناوين والفاصل) وآخر سطر (ملخص)
        # Skip first two lines (headers and separator) and last line (summary)
        for line in lines[1:-1]:
            parts = line.split()
            if len(parts) >= 5:
                name = parts[0]
                load = parts[1]
                active = parts[2]
                sub = parts[3]
                description = " ".join(parts[4:]) # الوصف قد يحتوي على مسافات
                services.append({
                    "name": name,
                    "load": load,
                    "active": active,
                    "sub": sub,
                    "description": description
                })
        return services

    @staticmethod
    def get_service_status(service_name):
        """
        جلب حالة خدمة معينة (نشطة، غير نشطة، إلخ).
        Fetches the status of a specific service (active, inactive, etc.).
        """
        output = ServicesManager._run_systemctl_command(["is-active", service_name], check_output=False)
        if output.startswith("Error:"):
            return output
        return output.strip()

    @staticmethod
    def start_service(service_name):
        """
        بدء خدمة معينة.
        Starts a specific service.
        """
        return ServicesManager._run_systemctl_command(["start", service_name])

    @staticmethod
    def stop_service(service_name):
        """
        إيقاف خدمة معينة.
        Stops a specific service.
        """
        return ServicesManager._run_systemctl_command(["stop", service_name])

    @staticmethod
    def restart_service(service_name):
        """
        إعادة تشغيل خدمة معينة.
        Restarts a specific service.
        """
        return ServicesManager._run_systemctl_command(["restart", service_name])

    @staticmethod
    def enable_service(service_name):
        """
        تمكين خدمة لتبدأ تلقائياً عند الإقلاع.
        Enables a service to start automatically on boot.
        """
        return ServicesManager._run_systemctl_command(["enable", service_name])

    @staticmethod
    def disable_service(service_name):
        """
        تعطيل خدمة لمنعها من البدء تلقائياً عند الإقلاع.
        Disables a service from starting automatically on boot.
        """
        return ServicesManager._run_systemctl_command(["disable", service_name])

    @staticmethod
    def is_service_enabled(service_name):
        """
        التحقق مما إذا كانت الخدمة ممكّنة (تلقائياً عند الإقلاع).
        Checks if a service is enabled (autostarts on boot).
        """
        output = ServicesManager._run_systemctl_command(["is-enabled", service_name], check_output=False)
        if output.startswith("Error:"):
            return "unknown" # أو يمكنك إرجاع False حسب رغبتك في التعامل مع الأخطاء
        return output.strip() # سيكون "enabled" أو "disabled" أو "static" أو "masked"
