from pathlib import Path
import sys

REQUIRED_SECTIONS = [
    "---",
    "# Role",
    "# Use this skill when",
    "# Do not use this skill when",
    "# Inputs expected",
    "# Source hierarchy",
    "# Process",
    "# Output format",
    "# Quality bar",
    "# Failure modes to avoid",
    "# Related skills",
]

def lint_skill(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors = []
    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"{path}: missing section `{section}`")
    if "description:" not in text:
        errors.append(f"{path}: missing frontmatter description")
    if "name:" not in text:
        errors.append(f"{path}: missing frontmatter name")
    return errors

def main() -> int:
    skill_files = list(Path("skills").rglob("SKILL.md"))
    all_errors = []
    if not skill_files:
        print("No SKILL.md files found.")
        return 1
    for path in skill_files:
        all_errors.extend(lint_skill(path))
    if all_errors:
        print("Skill lint failed:")
        for error in all_errors:
            print(f"- {error}")
        return 1
    print(f"Skill lint passed for {len(skill_files)} skills.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
