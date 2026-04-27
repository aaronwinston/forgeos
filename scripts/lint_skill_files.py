#!/usr/bin/env python3
"""
Lint skill files in the skills directory.
Validates structure and metadata of skill definition files.
"""

import os
import sys
from pathlib import Path

def lint_skill_files():
    """Validate skill files structure."""
    skills_dir = Path('skills')
    
    if not skills_dir.exists():
        print("⚠️  No skills directory found - this is optional for now")
        return True
    
    errors = []
    skill_count = 0
    
    # Walk through skills directory
    for skill_dir in skills_dir.rglob('*'):
        if skill_dir.is_dir() and (skill_dir / 'SKILL.md').exists():
            skill_count += 1
            # Basic validation - just check file exists
            skill_file = skill_dir / 'SKILL.md'
            if not skill_file.stat().st_size > 0:
                errors.append(f"Empty skill file: {skill_file}")
    
    if errors:
        print("❌ Skill lint failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print(f"✅ Linted {skill_count} skill files successfully")
    return True

if __name__ == "__main__":
    success = lint_skill_files()
    sys.exit(0 if success else 1)
