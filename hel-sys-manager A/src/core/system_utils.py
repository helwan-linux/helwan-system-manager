import platform
import psutil
import datetime
import subprocess
import socket
import os


class SystemUtils:
    @staticmethod
    def get_hostname():
        return platform.node()

    @staticmethod
    def get_kernel_version():
        return platform.release()

    @staticmethod
    def get_os_name():
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=")[1].strip().strip('"')
            return platform.system()
        except FileNotFoundError:
            return platform.system()

    @staticmethod
    def get_distro_id():
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        return line.split("=")[1].strip().strip('"')
            return ""
        except FileNotFoundError:
            return ""

    @staticmethod
    def get_cpu_info():
        return {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "current_usage": psutil.cpu_percent(interval=1)
        }

    @staticmethod
    def get_ram_info():
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "used_percent": mem.percent
        }

    @staticmethod
    def get_disk_usage():
        disk = psutil.disk_usage('/')
        return {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "used_percent": disk.percent
        }

    @staticmethod
    def get_uptime():
        boot_time_timestamp = psutil.boot_time()
        boot_time_datetime = datetime.datetime.fromtimestamp(boot_time_timestamp)
        now = datetime.datetime.now()
        uptime_delta = now - boot_time_datetime

        days = uptime_delta.days
        hours = uptime_delta.seconds // 3600
        minutes = (uptime_delta.seconds % 3600) // 60

        return f"{days} days, {hours} hours, {minutes} minutes"

    @staticmethod
    def get_network_info():
        net_if_addrs = psutil.net_if_addrs()
        network_info = {}
        for interface_name, interface_addresses in net_if_addrs.items():
            for address in interface_addresses:
                if address.family == socket.AF_PACKET:
                    network_info.setdefault(interface_name, {})["mac"] = address.address
                elif address.family == socket.AF_INET:
                    network_info.setdefault(interface_name, {})["ipv4"] = address.address
                elif address.family == socket.AF_INET6:
                    network_info.setdefault(interface_name, {})["ipv6"] = address.address
        return network_info

    @staticmethod
    def get_pacman_stats():
        try:
            total = int(subprocess.check_output("pacman -Q | wc -l", shell=True).decode().strip())
            updates_raw = subprocess.check_output("checkupdates", shell=True, text=True)
            updates = updates_raw.strip().splitlines() if updates_raw else []
            return {"total": total, "updates": updates, "updates_count": len(updates)}
        except subprocess.CalledProcessError:
            return {"total": 0, "updates": [], "updates_count": 0}

    @staticmethod
    def run_pacman_update():
        try:
            process = subprocess.Popen(
                ["pkexec", "pacman", "-Syu", "--noconfirm"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output, error = process.communicate()
            return output if output else error
        except Exception as e:
            return str(e)

    @staticmethod
    def install_packages(packages):
        if not packages:
            return "No packages specified."
        try:
            cmd = ["pkexec", "pacman", "-S", "--noconfirm"] + packages
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output, error = process.communicate()
            return output if output else error
        except Exception as e:
            return str(e)
