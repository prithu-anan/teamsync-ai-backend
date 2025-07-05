#!/usr/bin/env python3
"""
Dependency checker and installer for RAG system
"""

import subprocess
import sys
import importlib

def check_package(package_name):
    """Check if a package is installed"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main function to check and install dependencies"""
    print("🔍 Checking RAG system dependencies...")
    
    # List of required packages
    required_packages = [
        "qdrant-client",
        "langchain",
        "langchain-openai",
        "langchain-community",
        "openai",
        "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if check_package(package.replace("-", "_")):
            print(f"✅ {package} is installed")
        else:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing {len(missing_packages)} missing packages...")
        for package in missing_packages:
            print(f"Installing {package}...")
            if install_package(package):
                print(f"✅ Successfully installed {package}")
            else:
                print(f"❌ Failed to install {package}")
                return False
    else:
        print("\n🎉 All dependencies are already installed!")
    
    print("\n🚀 Ready to run RAG system!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 