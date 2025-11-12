#!/usr/bin/env python3
"""
AI Escape Room Launcher
Choose between terminal or GUI version
"""

import sys
import os

def check_pygame():
    """Check if pygame is installed"""
    try:
        import pygame
        return True
    except ImportError:
        return False

def main():
    """Main launcher"""
    print("\n" + "="*60)
    print("AI ESCAPE ROOM - GAME LAUNCHER")
    print("="*60)
    print("\nChoose your interface:")
    print("  1. Terminal Version (No dependencies)")
    print("  2. GUI Version (Requires pygame)")
    print("  3. Quick Demo (Terminal)")
    print("  4. Run Tests")
    print("  5. Exit")
    print("="*60)
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        print("\n🎮 Starting Terminal Version...\n")
        os.system("python game.py")
        
    elif choice == "2":
        if not check_pygame():
            print("\n❌ Pygame not installed!")
            print("\nTo install pygame, run:")
            print("  pip install pygame")
            print("\nOr install all dependencies:")
            print("  pip install -r requirements.txt")
            return
            
        print("\n🎨 Starting GUI Version...\n")
        os.system("python gui_pygame.py")
        
    elif choice == "3":
        print("\n⚡ Running Quick Demo...\n")
        os.system("python quick_demo.py")
        
    elif choice == "4":
        print("\n🧪 Running Tests...\n")
        os.system("python test_components.py")
        
    elif choice == "5":
        print("\n👋 Goodbye!\n")
        return
        
    else:
        print("\n❌ Invalid choice!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        sys.exit(0)
