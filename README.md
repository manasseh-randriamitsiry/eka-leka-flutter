## eka-leka-flutter - Flutter Development Environment Installer

A comprehensive Windows installer that automatically sets up a complete Flutter development environment with all necessary dependencies and tools.

## 🚀 Features

- **One-click installation** of complete Flutter development environment
- **GUI interface** for easy component selection and monitoring
- **Version selection** for all major components
- **Automatic dependency resolution** and environment configuration
- **Real-time progress tracking** and detailed logging
- **Administrator privilege handling** with automatic elevation

## 📦 Components Installed

- **Chocolatey** - Windows package manager
- **Git** - Version control system
- **Android Studio** - Official IDE for Android development
- **OpenJDK** - Java development kit
- **Flutter SDK** - Flutter framework and tools
- **Android SDK Command-line Tools** - Android development tools
- **NDK** - Native development kit
- **Environment Variables** - System PATH configuration

## 🎯 Quick Start

### Option 1: Using the Executable (Recommended)
1. Download `FlutterInstaller.exe` from release
2. Right-click and "Run as administrator"
3. Follow the GUI prompts to select versions and install

### Option 2: Using the PowerShell Script
1. Download the script from release and Open PowerShell as administrator
2. Navigate to the download directory
3. Run: `.\install_flutter_powershell.ps1`

### Option 3: Using the Python Script
1. Install Python dependencies: `pip install tkinter`
2. Run: `python main.py`

## 🛠️ Installation Options

The installer supports version selection for the following components:

- **Flutter SDK**: stable, beta, dev, master, or specific version numbers
- **Git**: latest or specific version
- **OpenJDK**: latest or specific version (17.x.x recommended)
- **Android Studio**: latest or specific version
- **NDK**: latest or specific version

### Auto-Configure Feature
Click the "⚡ Auto Configure" button to automatically select recommended versions:
- Flutter: stable (production-ready)
- Git: latest
- OpenJDK: latest 17.x.x (Flutter-compatible)
- Android Studio: latest
- NDK: latest

## 📋 System Requirements

- **Windows 10/11** (x64)
- **Administrator privileges** (required for installation)
- **Internet connection** (for downloading components)
- **At least 10GB free disk space**

## 🔧 Usage

### GUI Interface
1. **Check System**: Verifies current installation status
2. **Auto Configure**: Sets recommended versions automatically
3. **Run Installer**: Begins the installation process
4. **Open Log**: View detailed installation logs

### Command Line Options
```powershell
# Install with specific versions
.\install_flutter_windows.ps1 -FlutterVersion "stable" -GitVersion "latest" -JavaVersion "17.0.8" -NdkVersion "29.0.14206865" -AndroidStudioVersion "latest"

# Install with default versions
.\install_flutter_windows.ps1
```

## 📁 Project Structure

```
eka-leka-flutter/
├── flutter_installer_ui/
│   └── main.py                 # GUI application
├── install_flutter_windows.ps1 # PowerShell installer script
├── FlutterInstaller.spec       # PyInstaller specification
└── README.md                   # This file
```

## 🔍 Verification

After installation, restart your computer if necessary and run:

```bash
flutter doctor
```

This should show all components properly configured with checkmarks.

## 🐛 Troubleshooting

### Common Issues

1. **Administrator Privileges**: Always run as administrator
2. **Internet Connection**: Ensure stable internet for downloads
3. **Antivirus**: Temporarily disable if blocking installations
4. **Disk Space**: Ensure at least 10GB free space
5. **Windows Updates**: Install pending Windows updates first

### Log Files
- Installation log: `%USERPROFILE%\flutter_installer.log`
- Flutter log: `flutter doctor -v`

### Manual Component Check
Use the GUI's "Check System" feature to verify individual component status.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Support

For support or questions:
- Email: manassehrandriamitsiry@gmail.com
- Check the log files for detailed error information
- Ensure all system requirements are met

## 🔄 Building from Source

### Prerequisites
- Python 3.7+
- PyInstaller
- Tkinter (usually included with Python)

### Build Steps
```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller FlutterInstaller.spec

# The executable will be in dist/FlutterInstaller.exe
```

## 📈 Version History

- **v1.0**: Initial release with complete Flutter environment setup
- GUI interface for easy component management
- Version selection for all major components
- Automatic environment configuration

---

**Note**: This installer is designed for Windows systems. For macOS or Linux, please refer to the official Flutter documentation for platform-specific installation instructions or use IA to convert the script into a bash script and you can create your own.