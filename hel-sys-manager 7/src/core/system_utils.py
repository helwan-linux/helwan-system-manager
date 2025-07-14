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
            # Attempt to read PRETTY_NAME from /etc/os-release on Linux
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=")[1].strip().strip('"')
            # Fallback for systems without /etc/os-release or if PRETTY_NAME is not found
            return platform.system()
        except FileNotFoundError:
            # Fallback for non-Linux systems or if file not found
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
            "current_usage": psutil.cpu_percent(interval=1) # interval for a non-blocking call
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
        # Using '/' for root partition on Linux, or the main drive on Windows/macOS
        # More robust implementation might list all partitions
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
                # MAC address
                if address.family == socket.AF_PACKET:
                    network_info.setdefault(interface_name, {})["mac"] = address.address
                # IPv4 address
                elif address.family == socket.AF_INET:
                    network_info.setdefault(interface_name, {})["ipv4"] = address.address
                # IPv6 address
                elif address.family == socket.AF_INET6:
                    network_info.setdefault(interface_name, {})["ipv6"] = address.address
        return network_info
