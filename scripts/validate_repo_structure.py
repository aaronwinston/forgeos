#!/usr/bin/env python3
"""
Validate repository structure and required directories/files.
"""

import os
import sys
from pathlib import Path

def validate_structure():
    """Check that required repository directories and files exist."""
    errors = []
    warnings = []
    
    # Check essential directories
    required_dirs = [
        'apps/web',
        'skills',
        '.github/workflows',
    ]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            errors.append(f"Missing required directory: {dir_path}")
    
    # Check essential files
    required_files = [
        'apps/web/package.json',
        'apps/web/next.config.mjs',
        '.github/workflows/deploy.yml',
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            errors.append(f"Missing required file: {file_path}")
    
    # Print results
    if errors:
        print("❌ Structure validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    if warnings:
        print("⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    print("✅ Repository structure is valid")
    return True

if __name__ == "__main__":
    success = validate_structure()
    sys.exit(0 if success else 1)
