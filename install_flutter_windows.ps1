# =================================================================
# Comprehensive Flutter Development Environment Installer for Windows
# =================================================================
# This script installs and configures all necessary components for
# Flutter development on a fresh Windows system.
#
# It performs the following actions:
# 1. Ensures the script is run with Administrator privileges.
# 2. Installs Chocolatey, the package manager for Windows.
# 3. Installs Git, Android Studio, and the latest OpenJDK using Chocolatey.
# 4. Clones the stable channel of the Flutter SDK from GitHub.
# 5. Sets up all required environment variables (PATH, ANDROID_HOME).
# 6. Runs `flutter doctor` to accept Android licenses and validate the setup.
#
# Usage:
# 1. Right-click on this script.
# 2. Select "Run with PowerShell".
# 3. Follow the on-screen prompts.
# =================================================================

param(
    [string]$FlutterVersion = "stable",
    [string]$GitVersion = "latest",
    [string]$JavaVersion = "latest",
    [string]$NdkVersion = "latest",
    [string]$AndroidStudioVersion = "latest"
)

# -------------------------------
# Helper Functions
# -------------------------------
function Write-Section($message) {
    Write-Host "`n================================================================="
    Write-Host " $message"
    Write-Host "================================================================="
}

function Is-Admin {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# -------------------------------
# Administrator Check
# -------------------------------
if (-not (Is-Admin)) {
    Write-Host "This script needs to be run with Administrator privileges."
    Write-Host "Please right-click the script and select 'Run with PowerShell' as an administrator."
    Read-Host -Prompt "Press Enter to exit"
    exit
}

# -------------------------------
# Chocolatey Installation
# -------------------------------
Write-Section "Checking and Installing Chocolatey"
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Chocolatey not found. Installing..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor [System.Net.SecurityProtocolType]::Tls12
    try {
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    } catch {
        Write-Host "Error installing Chocolatey. Please check your internet connection and try again."
        Read-Host -Prompt "Press Enter to exit"
        exit
    }
} else {
    Write-Host "Chocolatey is already installed."
}

# -------------------------------
# Install Core Dependencies
# -------------------------------
Write-Section "Installing Git, Android Studio, and OpenJDK"
if ($GitVersion -eq "latest") {
    choco install git -y
} else {
    choco install git --version $GitVersion -y
}
if ($AndroidStudioVersion -eq "latest") {
    choco install androidstudio -y
} else {
    choco install androidstudio --version $AndroidStudioVersion -y
}
if ($JavaVersion -eq "latest") {
    choco install openjdk -y
} else {
    choco install openjdk --version $JavaVersion -y
}

# -------------------------------
# Flutter SDK Installation
# -------------------------------
Write-Section "Installing Flutter SDK"
$flutterRoot = "C:\flutter"
if (-not (Test-Path $flutterRoot)) {
    Write-Host "Cloning the Flutter SDK from the $FlutterVersion channel..."
    git clone https://github.com/flutter/flutter.git -b $FlutterVersion $flutterRoot
} else {
    Write-Host "Flutter SDK directory already exists. Skipping clone."
}

# -------------------------------
# Install Android SDK Components
# -------------------------------
Write-Section "Installing Android SDK Command-line Tools and NDK"

$androidSdkRoot = "$env:LOCALAPPDATA\Android\Sdk"
$cmdlineToolsDir = Join-Path $androidSdkRoot "cmdline-tools"
$latestCmdlineToolsDir = Join-Path $cmdlineToolsDir "latest"
$sdkManagerPath = Join-Path $latestCmdlineToolsDir "bin\sdkmanager.bat"

if (-not (Test-Path $sdkManagerPath)) {
    Write-Host "Android Command-line Tools not found. Downloading and installing..."
    
    # URL for the command-line tools. This might need to be updated periodically.
    $cmdlineToolsUrl = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
    $cmdlineToolsZip = "$env:TEMP\commandlinetools.zip"
    
    # Download
    Invoke-WebRequest -Uri $cmdlineToolsUrl -OutFile $cmdlineToolsZip
    
    # Unzip to a temporary location
    $tempUnzipPath = "$env:TEMP\cmdline-tools-unzipped"
    if (Test-Path $tempUnzipPath) {
        Remove-Item $tempUnzipPath -Recurse -Force
    }
    Expand-Archive -Path $cmdlineToolsZip -DestinationPath $tempUnzipPath -Force
    
    # Create destination directory and move the tools
    New-Item -ItemType Directory -Path $latestCmdlineToolsDir -Force
    Move-Item -Path "$tempUnzipPath\cmdline-tools\*" -Destination $latestCmdlineToolsDir -Force
    
    # Cleanup
    Remove-Item $tempUnzipPath -Recurse -Force
    Remove-Item $cmdlineToolsZip
    
    Write-Host "Android Command-line Tools installed."
} else {
    Write-Host "Android Command-line Tools already found."
}

# Add command-line tools to PATH for the current session
$env:Path = "$($latestCmdlineToolsDir)\bin;" + $env:Path

# Use sdkmanager to install NDK and command-line tools (latest)
Write-Host "Installing latest command-line tools and NDK via sdkmanager..."
# The following line will ensure the latest command-line tools are installed.
1..10 | ForEach-Object { "y" } | & $sdkManagerPath --licenses --sdk_root=$androidSdkRoot
& $sdkManagerPath "cmdline-tools;latest" --sdk_root=$androidSdkRoot
# This NDK version is hardcoded. You can find the latest version by running: sdkmanager --list | findstr "ndk"
if ($NdkVersion -eq "latest") {
    & $sdkManagerPath "ndk;29.0.14206865" --sdk_root=$androidSdkRoot
} else {
    & $sdkManagerPath "ndk;$NdkVersion" --sdk_root=$androidSdkRoot
}


# -------------------------------
# Environment Variable Configuration
# -------------------------------
Write-Section "Configuring Environment Variables"

# Set ANDROID_HOME
$androidHome = "$env:LOCALAPPDATA\Android\Sdk"
[Environment]::SetEnvironmentVariable('ANDROID_HOME', $androidHome, 'Machine')
Write-Host "ANDROID_HOME set to $androidHome"

# Add paths to System PATH
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
$pathsToAdd = @(
    "$flutterRoot\bin",
    "$androidHome\emulator",
    "$androidHome\platform-tools",
    "$androidHome\cmdline-tools\latest\bin"
)

foreach ($path in $pathsToAdd) {
    if ($currentPath -notlike "*$path*") {
        $currentPath += ";$path"
        Write-Host "Adding '$path' to PATH."
    } else {
        Write-Host "'$path' already in PATH."
    }
}

[Environment]::SetEnvironmentVariable('Path', $currentPath, 'Machine')
$env:Path = $currentPath # Update for current session

# -------------------------------
# Finalizing Flutter Setup
# -------------------------------
Write-Section "Running Flutter Doctor and Accepting Licenses"

# Run flutter doctor to download Dart SDK and other dependencies
Write-Host "Running 'flutter doctor' to finalize installation. This may take a few minutes..."
& "$flutterRoot\bin\flutter.bat" doctor

# Accept Android licenses
Write-Host "Attempting to automatically accept Android SDK licenses..."
1..10 | ForEach-Object { "y" } | & "$flutterRoot\bin\flutter.bat" doctor --android-licenses

# -------------------------------
# Completion
# -------------------------------
Write-Section "Installation Complete!"
Write-Host "The script has finished."
Write-Host "Please restart your computer for all changes to take effect."
Write-Host "After restarting, you can open a new terminal and run 'flutter doctor' to verify the installation."
Read-Host -Prompt "Press Enter to close this window"