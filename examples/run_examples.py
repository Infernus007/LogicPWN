#!/usr/bin/env python3
"""
LogicPWN Examples Runner
A simple script to demonstrate all available examples.
"""

import os
import sys

def print_banner():
    print("🎯 LogicPWN Examples Runner")
    print("=" * 50)
    print("Available examples for LogicPWN security testing framework")
    print()

def list_examples():
    examples = [
        {
            "file": "01_basic_example.py",
            "name": "Basic HTTP Requests & Security Analysis",
            "description": "Demonstrates basic LogicPWN functionality",
            "prerequisites": "Internet connection"
        },
        {
            "file": "02_dvwa_complete.py", 
            "name": "Complete DVWA Testing Workflow",
            "description": "End-to-end DVWA testing (setup → login → explore)",
            "prerequisites": "DVWA on localhost:8080"
        },
        {
            "file": "03_simple_exploits.py",
            "name": "Basic Exploit Chains",
            "description": "SQL injection and XSS testing chains",
            "prerequisites": "DVWA logged in"
        },
        {
            "file": "dvwa_real_test.py",
            "name": "DVWA Connectivity Test",
            "description": "Test DVWA setup and connectivity",
            "prerequisites": "DVWA running"
        },
        {
            "file": "dvwa_auth_example.py",
            "name": "DVWA Authentication Demo",
            "description": "Authentication flow with admin/admin",
            "prerequisites": "DVWA database setup"
        }
    ]
    
    print("📚 Available Examples:")
    print()
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['name']}")
        print(f"   File: {example['file']}")
        print(f"   Description: {example['description']}")
        print(f"   Prerequisites: {example['prerequisites']}")
        print()
    
    return examples

def show_usage():
    print("🔧 Usage:")
    print("poetry run python examples/01_basic_example.py")
    print("poetry run python examples/02_dvwa_complete.py")
    print("poetry run python examples/03_simple_exploits.py")
    print()

def show_dvwa_setup():
    print("🎯 DVWA Setup (for DVWA examples):")
    print("1. Start DVWA: docker run -d -p 8080:80 vulnerables/web-dvwa:latest")
    print("2. Setup database: Visit http://localhost:8080/setup.php")
    print("3. Click 'Create / Reset Database'")
    print("4. Login with admin/admin")
    print()

def show_troubleshooting():
    print("🔍 Troubleshooting:")
    print("• Import errors: poetry install")
    print("• DVWA not accessible: Check Docker container")
    print("• Login failed: Ensure database is setup")
    print("• Network errors: Check internet connection")
    print()

def main():
    print_banner()
    examples = list_examples()
    show_usage()
    show_dvwa_setup()
    show_troubleshooting()
    
    print("🎉 Ready to start testing!")
    print("💡 Begin with 01_basic_example.py for a quick start")

if __name__ == "__main__":
    main()
