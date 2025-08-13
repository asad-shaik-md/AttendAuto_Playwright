#!/usr/bin/env python3
"""
Setup Script for Jain University Attendance Checker (Playwright Version)
========================================================================

This script helps set up the Playwright version of the attendance checker.
It creates a virtual environment, installs dependencies and Playwright browsers automatically.
"""

import subprocess
import sys
import os
import venv
import argparse


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n{description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✓ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("Checking Python version...")
    
    if sys.version_info < (3, 7):
        print("✗ Python 3.7+ is required. Please upgrade your Python installation.")
        return False
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} is compatible")
    return True


def create_virtual_environment():
    """Create a virtual environment for the project."""
    venv_path = os.path.join(os.path.dirname(__file__), "venv")
    
    if os.path.exists(venv_path):
        print("Virtual environment already exists, skipping creation...")
        return venv_path
    
    print("Creating virtual environment...")
    try:
        venv.create(venv_path, with_pip=True)
        print("✓ Virtual environment created successfully!")
        return venv_path
    except Exception as e:
        print(f"✗ Failed to create virtual environment: {e}")
        return None


def get_venv_python(venv_path):
    """Get the Python executable path from virtual environment."""
    if sys.platform == "win32":
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:
        return os.path.join(venv_path, "bin", "python")


def install_dependencies(python_executable=None):
    """Install Python dependencies."""
    if python_executable is None:
        python_executable = sys.executable
        
    requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    
    if not os.path.exists(requirements_file):
        print("✗ requirements.txt not found!")
        return False
    
    return run_command(
        f"{python_executable} -m pip install -r {requirements_file}",
        "Installing Python dependencies"
    )


def install_playwright_browsers(python_executable=None):
    """Install Playwright browsers."""
    if python_executable is None:
        python_executable = sys.executable
        
    return run_command(
        f"{python_executable} -m playwright install",
        "Installing Playwright browsers"
    )


def verify_installation(python_executable=None):
    """Verify that everything is installed correctly."""
    if python_executable is None:
        python_executable = sys.executable
        
    print("\nVerifying installation...")
    
    # Test import in the virtual environment
    test_command = f'{python_executable} -c "import playwright; from playwright.async_api import async_playwright; print(\\"✓ Playwright installation verified\\")"'
    
    try:
        result = subprocess.run(test_command, shell=True, check=True, capture_output=True, text=True)
        print("✓ Playwright module imported successfully")
        print("✓ Playwright async API available")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Import error: {e}")
        return False


def create_activation_script():
    """Create easy activation scripts for the virtual environment."""
    project_dir = os.path.dirname(__file__)
    venv_path = os.path.join(project_dir, "venv")
    
    if not os.path.exists(venv_path):
        return
    
    # Create activation script for Unix/macOS
    if sys.platform != "win32":
        activate_script = os.path.join(project_dir, "activate_env.sh")
        with open(activate_script, "w") as f:
            f.write(f"""#!/bin/bash
# Activate virtual environment and run attendance checker
source {venv_path}/bin/activate
echo "Virtual environment activated!"
echo "You can now run: python attendance_checker.py"
echo "To deactivate: deactivate"
""")
        os.chmod(activate_script, 0o755)
        
        # Create run script
        run_script = os.path.join(project_dir, "run_attendance_checker.sh")
        with open(run_script, "w") as f:
            f.write(f"""#!/bin/bash
# Run attendance checker in virtual environment
{venv_path}/bin/python attendance_checker.py
""")
        os.chmod(run_script, 0o755)
        
    # Create activation script for Windows
    else:
        activate_script = os.path.join(project_dir, "activate_env.bat")
        with open(activate_script, "w") as f:
            f.write(f"""@echo off
rem Activate virtual environment and run attendance checker
call {venv_path}\\Scripts\\activate.bat
echo Virtual environment activated!
echo You can now run: python attendance_checker.py
echo To deactivate: deactivate
""")
        
        # Create run script for Windows
        run_script = os.path.join(project_dir, "run_attendance_checker.bat")
        with open(run_script, "w") as f:
            f.write(f"""@echo off
rem Run attendance checker in virtual environment
{venv_path}\\Scripts\\python.exe attendance_checker.py
pause
""")
    
    print(f"✓ Created activation scripts: {os.path.basename(activate_script)}")
    return activate_script


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Setup Jain University Attendance Checker (Playwright Version)")
    parser.add_argument("--no-venv", action="store_true", help="Skip virtual environment creation")
    parser.add_argument("--venv", action="store_true", help="Force virtual environment creation")
    args = parser.parse_args()
    
    print("Jain University Attendance Checker - Playwright Setup")
    print("=" * 55)
    
    # Determine if we should use virtual environment
    if args.no_venv:
        use_venv = False
        print("\nSkipping virtual environment creation (--no-venv flag)")
    elif args.venv:
        use_venv = True
        print("\nForcing virtual environment creation (--venv flag)")
    else:
        # Default to using virtual environment, but make it non-interactive
        use_venv = True
        print("\nUsing virtual environment by default (recommended)")
        print("Use --no-venv flag to skip virtual environment creation")
    
    python_executable = sys.executable
    venv_path = None
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Create virtual environment if requested
    if use_venv:
        venv_path = create_virtual_environment()
        if venv_path:
            python_executable = get_venv_python(venv_path)
            print(f"Using virtual environment Python: {python_executable}")
        else:
            print("Failed to create virtual environment, continuing with system Python...")
    
    # Step 3: Install Python dependencies
    if not install_dependencies(python_executable):
        print("\n✗ Failed to install Python dependencies")
        sys.exit(1)
    
    # Step 4: Install Playwright browsers
    if not install_playwright_browsers(python_executable):
        print("\n✗ Failed to install Playwright browsers")
        print("You can try manually with: playwright install")
        sys.exit(1)
    
    # Step 5: Verify installation
    if not verify_installation(python_executable):
        print("\n✗ Installation verification failed")
        sys.exit(1)
    
    # Step 6: Create activation scripts if using virtual environment
    if use_venv and venv_path:
        create_activation_script()
    
    print("\n" + "=" * 55)
    print("✓ Setup completed successfully!")
    
    if use_venv and venv_path:
        print("\n🚀 VIRTUAL ENVIRONMENT SETUP:")
        print("=" * 35)
        if sys.platform == "win32":
            print("To activate virtual environment:")
            print("  activate_env.bat")
            print("\nTo run attendance checker directly:")
            print("  run_attendance_checker.bat")
            print(f"\nOr manually:")
            print(f"  {python_executable} attendance_checker.py")
        else:
            print("To activate virtual environment:")
            print("  source ./activate_env.sh")
            print("  # or")
            print(f"  source {venv_path}/bin/activate")
            print("\nTo run attendance checker directly:")
            print("  ./run_attendance_checker.sh")
            print(f"\nOr manually:")
            print(f"  {python_executable} attendance_checker.py")
        
        print(f"\nVirtual environment location: {venv_path}")
    else:
        print("\nYou can now run the attendance checker with:")
        print("python attendance_checker.py")
    
    print("\nIf you encounter any issues, check the README.md file for troubleshooting.")


if __name__ == "__main__":
    main()
