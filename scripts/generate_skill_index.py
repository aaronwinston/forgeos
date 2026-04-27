#!/usr/bin/env python3
"""
Generate an index of all available skills in the repository.
"""

import json
import sys
from pathlib import Path

def generate_skill_index():
    """Generate index of skills and write to skills/index.json."""
    skills_dir = Path('skills')
    
    if not skills_dir.exists():
        print("⚠️  No skills directory found - skipping index generation")
        return True
    
    skills = []
    
    # Walk through skills directory
    for skill_dir in sorted(skills_dir.rglob('*')):
        if skill_dir.is_dir() and (skill_dir / 'SKILL.md').exists():
            skill_path = skill_dir / 'SKILL.md'
            relative_path = skill_path.relative_to(skills_dir.parent)
            
            # Read title from SKILL.md if possible
            title = skill_dir.name
            try:
                with open(skill_path, 'r') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('#'):
                        title = first_line.lstrip('# ').strip()
            except:
                pass
            
            skills.append({
                "name": skill_dir.name,
                "title": title,
                "path": str(relative_path),
            })
    
    # Write index
    index_file = skills_dir / 'index.json'
    try:
        with open(index_file, 'w') as f:
            json.dump({"skills": skills, "count": len(skills)}, f, indent=2)
        print(f"✅ Generated skill index with {len(skills)} skills")
        return True
    except Exception as e:
        print(f"❌ Failed to generate skill index: {e}")
        return False

if __name__ == "__main__":
    success = generate_skill_index()
    sys.exit(0 if success else 1)
