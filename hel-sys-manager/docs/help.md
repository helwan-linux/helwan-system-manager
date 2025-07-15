# Welcome to Hel System Manager

Hel System Manager is a powerful graphical tool designed to simplify your Linux system administration tasks. This application aims to provide a unified and user-friendly interface to control various aspects of your system, from package management to resource monitoring and service control.

---

## Key Features

Hel System Manager consists of several main tabs, each focusing on a specific set of functionalities:

### 1. "System" Tab
This tab provides a comprehensive overview of your system's resources and performance:
* **General Information:** Display hostname, OS version, kernel version, and uptime.
* **CPU Usage:** Monitor CPU utilization, physical, and logical core counts.
* **RAM Usage:** Track total, available, and used RAM, and its percentage.
* **Disk Usage:** Monitor total, used, and free disk space, and its percentage.
* **Network Information:** Display details of network interfaces.
* **Live Updates:** All information is periodically refreshed to reflect the current state of your system.

### 2. "Services" Tab
Control the systemd services running on your system:
* **View Services:** List all services with their status details (active, inactive, loaded, sub-state).
* **Search and Filter:** Easily search for specific services.
* **Start/Stop/Restart:** Control the state of active services.
* **Enable/Disable:** Manage services that start automatically at boot.
* **Note:** This tab requires the application to be run on a Linux system that uses systemd.

### 3. "Packages" Tab
This tab is your central hub for managing Arch Linux packages. From here, you can:
* **Search for Packages:** Find available packages in official repositories.
* **View Details:** Get detailed information about any package (description, version, dependencies, install size).
* **List Installed:** Browse a list of all packages currently installed on your system.
* **Install Packages:** Easily install new packages.
* **Remove Packages:** Uninstall unwanted packages from your system.
* **Update System:** Update all installed packages to the latest versions (requires root privileges).
* **View History:** Review the history of package installation/removal/update operations.

### 4. "Dotfiles" Tab - *Under Development*
This tab is dedicated to managing your personal configuration files (Dotfiles). It will provide tools for:
* Creating backups of your dotfiles.
* Restoring dotfiles.
* Synchronizing dotfiles across different machines (future features).

---

## Support and Help

If you encounter any issues or have questions, please refer to the [project's GitHub repository](https://github.com/helwan-linux/helwan-system-manager) 
or contact the developers.
Saeed Badrelden
EMAIL : saeedbadrelden2021@gmail.com
EMAIL : helwanlinux@gmail.com
**Thank you for using Hel System Manager!**