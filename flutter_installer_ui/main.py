import tkinter as tk
from tkinter import ttk, scrolledtext, font
import subprocess
import ctypes
import os
import sys
import threading
import webbrowser
import urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime

class FlutterInstallerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flutter Development Environment Installer")
        self.geometry("900x750")
        self.configure(bg='#f0f0f0')
        
        # Set window icon and styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), background='#f0f0f0', foreground='#2c3e50')
        self.style.configure('Subtitle.TLabel', font=('Segoe UI', 10), background='#f0f0f0', foreground='#7f8c8d')
        self.style.configure('Component.TLabel', font=('Segoe UI', 10, 'bold'), background='white')
        self.style.configure('Status.TLabel', font=('Segoe UI', 9), background='white')
        self.style.configure('Success.TLabel', font=('Segoe UI', 9), background='white', foreground='#27ae60')
        self.style.configure('Error.TLabel', font=('Segoe UI', 9), background='white', foreground='#e74c3c')
        self.style.configure('Warning.TLabel', font=('Segoe UI', 9), background='white', foreground='#f39c12')
        self.style.configure('Modern.TButton', font=('Segoe UI', 10, 'bold'))
        self.style.configure('Header.TFrame', background='#3498db')
        self.style.configure('Card.TFrame', background='white', relief='raised', borderwidth=1)
        
        self.log_file = os.path.join(os.path.expanduser("~"), "flutter_installer.log")

        self.components = {
            "Administrator Privileges": {"status": "Not Checked", "description": "Required for installation", "icon": "🔐"},
            "Chocolatey": {"status": "Not Checked", "description": "Package manager for Windows", "icon": "📦"},
            "Git": {"status": "Not Checked", "description": "Version control system", "icon": "🔀"},
            "Android Studio": {"status": "Not Checked", "description": "Official IDE for Android development", "icon": "📱"},
            "OpenJDK": {"status": "Not Checked", "description": "Java development kit", "icon": "☕"},
            "Flutter SDK": {"status": "Not Checked", "description": "Flutter framework and tools", "icon": "🎯"},
            "Android SDK Command-line Tools": {"status": "Not Checked", "description": "Android development tools", "icon": "🛠️"},
            "NDK": {"status": "Not Checked", "description": "Native development kit", "icon": "⚙️"},
            "Environment Variables": {"status": "Not Checked", "description": "System PATH configuration", "icon": "🌍"},
        }

        self.create_widgets()
        self.check_admin_privileges()

    def _get_flutter_versions(self):
        try:
            # Get tags from the remote repository
            result = subprocess.run(
                ["git", "ls-remote", "--tags", "https://github.com/flutter/flutter.git"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse the output to get version numbers
            tags = result.stdout.strip().split("\n")
            versions = []
            
            for tag in tags:
                tag_name = tag.split("refs/tags/")[-1]
                # Remove ^{} suffix if present
                tag_name = tag_name.replace("^{}", "")
                
                # Include all version-like tags and channel names
                if (tag_name in ["stable", "beta", "dev", "master"] or
                    (tag_name.count('.') >= 2 and 
                     not tag_name.endswith('.0') and
                     not tag_name.startswith('v') and
                     not 'rc' in tag_name.lower() and
                     not 'preview' in tag_name.lower())):
                    versions.append(tag_name)
            
            # Remove duplicates and sort versions
            versions = list(set(versions))
            
            def version_key(v):
                if v in ["stable", "beta", "dev", "master"]:
                    return (0, v)
                
                # Split version into parts for proper sorting
                parts = []
                for part in v.split('.'):
                    try:
                        parts.append(int(part))
                    except ValueError:
                        # Handle non-numeric parts
                        import re
                        match = re.match(r'(\d+)', part)
                        if match:
                            parts.append(int(match.group(1)))
                        else:
                            parts.append(0)
                return (1, tuple(parts))
            
            versions.sort(key=version_key, reverse=True)
            
            # Ensure channels are at the top
            channels = ["stable", "beta", "dev", "master"]
            ordered_versions = []
            for channel in channels:
                if channel in versions:
                    ordered_versions.append(channel)
                    versions.remove(channel)
            
            # Add the rest of the versions
            ordered_versions.extend(versions)
            
            return ordered_versions
        except Exception as e:
            print(f"Error getting Flutter versions: {e}")
            return ["stable", "beta", "dev"] # Fallback

    def _sort_versions(self, versions, prefix_to_remove=None):
        latest = "latest"
        if latest in versions:
            versions.remove(latest)
        
        def version_key(v):
            if prefix_to_remove:
                v = v.replace(prefix_to_remove, "")

            parts = []
            for part in v.split('.'):
                try:
                    parts.append(int(part))
                except ValueError:
                    import re
                    match = re.match(r'(\d+)', part)
                    if match:
                        parts.append(int(match.group(1)))
                    else:
                        parts.append(0)
            return tuple(parts)

        versions.sort(key=version_key, reverse=True)
        
        return [latest] + versions

    def _get_git_versions(self):
        try:
            url = "https://community.chocolatey.org/api/v2/FindPackagesById()?id='git'"
            with urllib.request.urlopen(url) as response:
                xml_content = response.read()
            
            root = ET.fromstring(xml_content)
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'd': 'http://schemas.microsoft.com/ado/2007/08/dataservices',
                'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata'
            }
            versions = ["latest"]
            for entry in root.findall('atom:entry', namespaces):
                properties = entry.find('m:properties', namespaces)
                if properties is not None:
                    version_element = properties.find('d:Version', namespaces)
                    if version_element is not None:
                        versions.append(version_element.text)
            return self._sort_versions(versions)
        except Exception as e:
            print(f"Error getting Git versions: {e}")
            return ["latest"]

    def _get_openjdk_versions(self):
        try:
            url = "https://community.chocolatey.org/api/v2/FindPackagesById()?id='openjdk'"
            with urllib.request.urlopen(url) as response:
                xml_content = response.read()
            
            root = ET.fromstring(xml_content)
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'd': 'http://schemas.microsoft.com/ado/2007/08/dataservices',
                'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata'
            }
            versions = ["latest"]
            for entry in root.findall('atom:entry', namespaces):
                properties = entry.find('m:properties', namespaces)
                if properties is not None:
                    version_element = properties.find('d:Version', namespaces)
                    if version_element is not None:
                        versions.append(version_element.text)
            return self._sort_versions(versions)
        except Exception as e:
            print(f"Error getting OpenJDK versions: {e}")
            return ["latest"]

    def _get_ndk_versions(self):
        try:
            android_sdk_root = os.path.join(os.getenv("LOCALAPPDATA"), "Android", "Sdk")
            sdk_manager_path = os.path.join(android_sdk_root, "cmdline-tools", "latest", "bin", "sdkmanager.bat")
            
            if not os.path.exists(sdk_manager_path):
                return ["latest"]

            result = subprocess.run(
                [sdk_manager_path, "--list"],
                capture_output=True,
                text=True,
                check=True
            )
            
            lines = result.stdout.strip().split("\n")
            versions = ["latest"]
            for line in lines:
                if "ndk;" in line:
                    version = line.split("|")[0].strip()
                    versions.append(version)
            
            return self._sort_versions(versions, prefix_to_remove="ndk;")
        except Exception as e:
            print(f"Error getting NDK versions: {e}")
            return ["latest"]

    def _get_android_studio_versions(self):
        try:
            url = "https://community.chocolatey.org/api/v2/FindPackagesById()?id='androidstudio'"
            with urllib.request.urlopen(url) as response:
                xml_content = response.read()
            
            root = ET.fromstring(xml_content)
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'd': 'http://schemas.microsoft.com/ado/2007/08/dataservices',
                'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata'
            }
            versions = ["latest"]
            for entry in root.findall('atom:entry', namespaces):
                properties = entry.find('m:properties', namespaces)
                if properties is not None:
                    version_element = properties.find('d:Version', namespaces)
                    if version_element is not None:
                        versions.append(version_element.text)
            return self._sort_versions(versions)
        except Exception as e:
            print(f"Error getting Android Studio versions: {e}")
            return ["latest"]

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self, style='Header.TFrame')
        header_frame.pack(fill="x", padx=0, pady=0)
        
        title_label = ttk.Label(header_frame, text="🎯 Flutter Development Environment", style='Title.TLabel')
        title_label.pack(pady=20)
        
        subtitle_label = ttk.Label(header_frame, text="Complete setup for Flutter, Android Studio, and all required dependencies", style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 20))
        
        # Main container
        main_container = ttk.Frame(self, style='Card.TFrame')
        main_container.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Components section
        components_label = ttk.Label(main_container, text="📋 System Components", font=('Segoe UI', 12, 'bold'), background='white')
        components_label.pack(pady=(10, 5), anchor="w", padx=15)
        
        # Create scrollable frame for components
        canvas = tk.Canvas(main_container, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Card.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Component cards
        for i, (component, details) in enumerate(self.components.items()):
            self._create_component_card(scrollable_frame, component, details, i)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Controls section
        controls_frame = ttk.Frame(main_container, style='Card.TFrame')
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Button container
        button_frame = ttk.Frame(controls_frame, style='Card.TFrame')
        button_frame.pack(pady=10)
        
        self.check_button = ttk.Button(button_frame, text="🔍 Check System", command=self.check_system, style='Modern.TButton')
        self.check_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.auto_configure_button = ttk.Button(button_frame, text="⚡ Auto Configure", command=self._auto_configure, style='Modern.TButton')
        self.auto_configure_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.run_button = ttk.Button(button_frame, text="🚀 Run Installer", command=self.run_installer, state=tk.DISABLED, style='Modern.TButton')
        self.run_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.log_button = ttk.Button(button_frame, text="📄 Open Log", command=self.open_log, state=tk.DISABLED, style='Modern.TButton')
        self.log_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Progress section
        progress_frame = ttk.Frame(main_container, style='Card.TFrame')
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        progress_label = ttk.Label(progress_frame, text="Progress:", font=('Segoe UI', 10, 'bold'), background='white')
        progress_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", length=100, mode="determinate")
        self.progress.pack(padx=10, pady=(0, 10), fill="x")
        
        # Output section
        output_label = ttk.Label(main_container, text="📝 Installation Output", font=('Segoe UI', 12, 'bold'), background='white')
        output_label.pack(pady=(10, 5), anchor="w", padx=15)
        
        output_frame = ttk.Frame(main_container, style='Card.TFrame')
        output_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, 
            wrap=tk.WORD, 
            height=12,
            font=('Consolas', 9),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='#ecf0f1'
        )
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Status bar
        self.status_bar = ttk.Label(self, text=f"Ready | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                   font=('Segoe UI', 9), background='#34495e', foreground='white')
        self.status_bar.pack(side="bottom", fill="x")
        
        # Help/Info bar
        help_frame = ttk.Frame(self, style='Card.TFrame')
        help_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        
        help_label = ttk.Label(help_frame, text="📧 Need help? Contact: manassehrandriamitsiry@gmail.com", 
                              font=('Segoe UI', 9), background='white', foreground='#3498db', cursor="hand2")
        help_label.pack(side="left", padx=10, pady=5)
        
        # Make email clickable
        def open_email(event):
            import webbrowser
            webbrowser.open('mailto:manassehrandriamitsiry@gmail.com')
        
        help_label.bind("<Button-1>", open_email)
        
        # Version info
        version_label = ttk.Label(help_frame, text="Flutter Development Environment Installer v1.0", 
                                 font=('Segoe UI', 8), background='white', foreground='#7f8c8d')
        version_label.pack(side="right", padx=10, pady=5)
    
    def _create_component_card(self, parent, component, details, index):
        # Card frame
        card_frame = ttk.Frame(parent, style='Card.TFrame')
        card_frame.pack(fill="x", padx=10, pady=5)
        
        # Icon and name
        info_frame = ttk.Frame(card_frame, style='Card.TFrame')
        info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        
        icon_label = ttk.Label(info_frame, text=details["icon"], font=('Segoe UI', 16), background='white')
        icon_label.pack(side="left", padx=(0, 10))
        
        name_frame = ttk.Frame(info_frame, style='Card.TFrame')
        name_frame.pack(side="left", fill="x", expand=True)
        
        name_label = ttk.Label(name_frame, text=component, style='Component.TLabel')
        name_label.pack(anchor="w")
        
        desc_label = ttk.Label(name_frame, text=details["description"], style='Subtitle.TLabel')
        desc_label.pack(anchor="w")
        
        # Status
        status_frame = ttk.Frame(card_frame, style='Card.TFrame')
        status_frame.pack(side="right", padx=10, pady=8)
        
        status_label = ttk.Label(status_frame, text=details["status"], style='Status.TLabel')
        status_label.pack()
        self.components[component]["label"] = status_label
        
        # Version dropdown
        if component == "Flutter SDK":
            self.flutter_version_var = tk.StringVar(value="stable")
            self.flutter_versions = self._get_flutter_versions()
            flutter_version_dropdown = ttk.Combobox(status_frame, textvariable=self.flutter_version_var, 
                                                   values=self.flutter_versions, state="readonly", width=15)
            flutter_version_dropdown.pack(pady=(5, 0))
        
        elif component == "Git":
            self.git_version_var = tk.StringVar(value="latest")
            self.git_versions = self._get_git_versions()
            git_version_dropdown = ttk.Combobox(status_frame, textvariable=self.git_version_var, 
                                               values=self.git_versions, state="readonly", width=15)
            git_version_dropdown.pack(pady=(5, 0))

        elif component == "OpenJDK":
            self.openjdk_version_var = tk.StringVar(value="latest")
            self.openjdk_versions = self._get_openjdk_versions()
            openjdk_version_dropdown = ttk.Combobox(status_frame, textvariable=self.openjdk_version_var, 
                                                  values=self.openjdk_versions, state="readonly", width=15)
            openjdk_version_dropdown.pack(pady=(5, 0))

        elif component == "NDK":
            self.ndk_version_var = tk.StringVar(value="latest")
            self.ndk_versions = self._get_ndk_versions()
            ndk_version_dropdown = ttk.Combobox(status_frame, textvariable=self.ndk_version_var, 
                                               values=self.ndk_versions, state="readonly", width=15)
            ndk_version_dropdown.pack(pady=(5, 0))

        elif component == "Android Studio":
            self.android_studio_version_var = tk.StringVar(value="latest")
            self.android_studio_versions = self._get_android_studio_versions()
            android_studio_version_dropdown = ttk.Combobox(status_frame, textvariable=self.android_studio_version_var, 
                                                         values=self.android_studio_versions, state="readonly", width=15)
            android_studio_version_dropdown.pack(pady=(5, 0))

    def _auto_configure(self):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "⚡ Auto-configuring recommended versions...\n")
        self.output_text.insert(tk.END, "=" * 50 + "\n")
        
        self.flutter_version_var.set("stable")
        self.output_text.insert(tk.END, f"🎯 Flutter: stable (recommended for production)\n")
        
        self.git_version_var.set("latest")
        self.output_text.insert(tk.END, f"🔀 Git: latest (most recent stable version)\n")
        
        self.ndk_version_var.set("latest")
        self.output_text.insert(tk.END, f"⚙️ NDK: latest (compatible with current Android Studio)\n")
        
        self.android_studio_version_var.set("latest")
        self.output_text.insert(tk.END, f"📱 Android Studio: latest (most recent stable release)\n")

        # Find the latest 17.x.x version for OpenJDK
        latest_17 = "17"
        for v in self.openjdk_versions:
            if v.startswith("17."):
                latest_17 = v
                break
        self.openjdk_version_var.set(latest_17)
        self.output_text.insert(tk.END, f"☕ OpenJDK: {latest_17} (recommended for Flutter development)\n")
        
        self.output_text.insert(tk.END, "=" * 50 + "\n")
        self.output_text.insert(tk.END, "✅ Auto-configuration complete! Click 'Run Installer' to begin installation.\n")
        
        self.status_bar.config(text="Auto-configuration complete - Ready to install")

    def check_system(self):
        self.check_button.config(state=tk.DISABLED)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "🔍 Starting system check...\n")
        self.output_text.insert(tk.END, "=" * 50 + "\n")
        self.status_bar.config(text="Checking system components...")
        
        self.progress["value"] = 0
        self.progress["maximum"] = len(self.components)
        
        threading.Thread(target=self._check_system_thread, daemon=True).start()

    def _check_system_thread(self):
        self.check_admin_privileges()
        self.check_chocolatey()
        self.check_git()
        self.check_android_studio()
        self.check_openjdk()
        self.check_flutter_sdk()
        self.check_android_sdk_tools()
        self.check_ndk()
        self.check_environment_variables()

        self.after(0, self.on_check_complete)

    def on_check_complete(self):
        self.check_button.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, "=" * 50 + "\n")
        self.output_text.insert(tk.END, "✅ System check complete.\n")
        
        # Count installed components
        installed_count = sum(1 for comp in self.components.values() if comp["status"] in ["Installed", "Set", "Activated"])
        total_count = len(self.components)
        
        self.output_text.insert(tk.END, f"\n📊 Summary: {installed_count}/{total_count} components ready\n")
        
        # Debug: Print all component statuses
        self.output_text.insert(tk.END, "\n🔍 Debug - Component Statuses:\n")
        for comp_name, comp_details in self.components.items():
            status = comp_details["status"]
            is_ready = status in ["Installed", "Set", "Activated"]
            self.output_text.insert(tk.END, f"  {comp_name}: {status} {'✅' if is_ready else '❌'}\n")
        
        all_installed = all(comp["status"] in ["Installed", "Set", "Activated"] for comp in self.components.values())
        self.output_text.insert(tk.END, f"\n🎯 All components installed: {all_installed}\n")
        
        if all_installed:
            self.output_text.insert(tk.END, "🎉 All components are installed! You're ready to develop Flutter apps.\n")
            self.status_bar.config(text="All components installed - Ready for development!")
            self.output_text.insert(tk.END, "🚫 Run Installer button remains DISABLED (nothing to install)\n")
        else:
            self.output_text.insert(tk.END, "🚀 Enabling Run Installer button (components need installation)\n")
            self.run_button.config(state=tk.NORMAL)
            self.status_bar.config(text=f"Ready to install missing components ({total_count - installed_count} remaining)")

    def check_admin_privileges(self):
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin:
                self.update_status("Administrator Privileges", "Activated", "green")
            else:
                self.update_status("Administrator Privileges", "Not Activated", "red")
                self.rerun_as_admin()
        except Exception as e:
            self.update_status("Administrator Privileges", "Error", "red")

    def rerun_as_admin(self):
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            self.destroy()
            sys.exit()

    def check_chocolatey(self):
        self.check_command("choco --version", "Chocolatey")

    def check_git(self):
        self.check_command("git --version", "Git")

    def check_android_studio(self):
        # A bit more complex as there is no direct command.
        # We will check for a common installation path.
        program_files = os.environ.get("ProgramFiles")
        android_studio_path = os.path.join(program_files, "Android", "Android Studio", "bin", "studio64.exe")
        if os.path.exists(android_studio_path):
            self.update_status("Android Studio", "Installed", "green")
        else:
            self.update_status("Android Studio", "Not Installed", "red")

    def check_openjdk(self):
        self.check_command("java -version", "OpenJDK")

    def check_command(self, command, component_name):
        try:
            subprocess.run(command, check=True, capture_output=True, text=True, shell=True)
            self.update_status(component_name, "Installed", "green")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.update_status(component_name, "Not Installed", "red")

    def check_flutter_sdk(self):
        if os.path.isdir("C:\\flutter"):
            self.update_status("Flutter SDK", "Installed", "green")
        else:
            self.update_status("Flutter SDK", "Not Installed", "red")

    def check_android_sdk_tools(self):
        android_sdk_root = os.path.join(os.getenv("LOCALAPPDATA"), "Android", "Sdk")
        sdk_manager_path = os.path.join(android_sdk_root, "cmdline-tools", "latest", "bin", "sdkmanager.bat")
        if os.path.exists(sdk_manager_path):
            self.update_status("Android SDK Command-line Tools", "Installed", "green")
        else:
            self.update_status("Android SDK Command-line Tools", "Not Installed", "red")

    def check_ndk(self):
        android_sdk_root = os.path.join(os.getenv("LOCALAPPDATA"), "Android", "Sdk")
        ndk_path = os.path.join(android_sdk_root, "ndk")
        if os.path.isdir(ndk_path):
            self.update_status("NDK", "Installed", "green")
        else:
            self.update_status("NDK", "Not Installed", "red")

    def check_environment_variables(self):
        android_home = os.getenv("ANDROID_HOME")
        path = os.getenv("PATH")
        
        android_home_ok = android_home is not None and "Android" in android_home and "Sdk" in android_home
        
        flutter_path_ok = path is not None and "flutter\\bin" in path
        android_emulator_ok = path is not None and "emulator" in path
        android_platform_tools_ok = path is not None and "platform-tools" in path
        android_cmdline_tools_ok = path is not None and "cmdline-tools\\latest\\bin" in path
        
        if android_home_ok and flutter_path_ok and android_emulator_ok and android_platform_tools_ok and android_cmdline_tools_ok:
            self.update_status("Environment Variables", "Set", "green")
        else:
            self.update_status("Environment Variables", "Not Set", "red")

    def update_status(self, component, status, color):
        def callback():
            self.components[component]["status"] = status
            label = self.components[component]["label"]
            label.config(text=status)
            
            # Update style based on status
            if status in ["Installed", "Set", "Activated"]:
                label.configure(style='Success.TLabel')
            elif status in ["Not Installed", "Not Set", "Not Activated"]:
                label.configure(style='Error.TLabel')
            elif status == "Error":
                label.configure(style='Error.TLabel')
            else:
                label.configure(style='Warning.TLabel')
            
            # Update status bar
            self.status_bar.config(text=f"Updated {component}: {status} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.after(0, callback)

    def run_installer(self):
        self.run_button.config(state=tk.DISABLED)
        self.log_button.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "🚀 Starting Flutter development environment installation...\n")
        self.output_text.insert(tk.END, "=" * 50 + "\n")
        self.output_text.insert(tk.END, f"📄 Log file: {self.log_file}\n")
        self.output_text.insert(tk.END, f"🎯 Flutter Version: {self.flutter_version_var.get()}\n")
        self.output_text.insert(tk.END, f"🔀 Git Version: {self.git_version_var.get()}\n")
        self.output_text.insert(tk.END, f"☕ Java Version: {self.openjdk_version_var.get()}\n")
        self.output_text.insert(tk.END, f"📱 Android Studio Version: {self.android_studio_version_var.get()}\n")
        self.output_text.insert(tk.END, f"⚙️ NDK Version: {self.ndk_version_var.get()}\n")
        self.output_text.insert(tk.END, "=" * 50 + "\n")
        
        self.status_bar.config(text="Installing components... This may take several minutes.")
        self.progress["value"] = 0
        self.progress["maximum"] = 100
        
        threading.Thread(target=self._run_installer_thread, daemon=True).start()

    def _run_installer_thread(self):
        try:
            with open(self.log_file, "w") as log:
                if getattr(sys, 'frozen', False):
                    # Running in a bundle
                    base_path = sys._MEIPASS
                else:
                    # Running in a normal Python environment
                    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

                script_path = os.path.join(base_path, "install_flutter_windows.ps1")
                
                process = subprocess.Popen(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path, "-FlutterVersion", self.flutter_version_var.get(), "-GitVersion", self.git_version_var.get(), "-JavaVersion", self.openjdk_version_var.get(), "-NdkVersion", self.ndk_version_var.get(), "-AndroidStudioVersion", self.android_studio_version_var.get()],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                for line in iter(process.stdout.readline, ''):
                    log.write(line)
                    self.after(0, self.output_text.insert, tk.END, line)
                    self.output_text.see(tk.END)
                    self.after(0, self.progress.step, 1)

                process.stdout.close()
                return_code = process.wait()

                if return_code == 0:
                    self.after(0, self.output_text.insert, tk.END, "\n" + "=" * 50 + "\n")
                    self.after(0, self.output_text.insert, tk.END, "🎉 Installation completed successfully!\n")
                    self.after(0, self.output_text.insert, tk.END, "📋 Please restart your terminal/command prompt to use the new environment.\n")
                    self.after(0, self.status_bar.config, text="Installation completed successfully!")
                else:
                    self.after(0, self.output_text.insert, tk.END, "\n" + "=" * 50 + "\n")
                    self.after(0, self.output_text.insert, tk.END, f"❌ Installation failed with exit code {return_code}.\n")
                    self.after(0, self.output_text.insert, tk.END, "📄 Please check the log file for details.\n")
                    self.after(0, self.status_bar.config, text=f"Installation failed (exit code: {return_code})")

        except Exception as e:
            self.after(0, self.output_text.insert, tk.END, f"\nError running installer: {e}\n")
        finally:
            self.after(0, self.run_button.config, state=tk.NORMAL)
            self.after(0, self.check_system)

    def open_log(self):
        webbrowser.open(self.log_file)


def main():
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        app = FlutterInstallerUI()
        app.mainloop()

if __name__ == "__main__":
    main()
