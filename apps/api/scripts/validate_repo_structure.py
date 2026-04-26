from pathlib import Path
import sys

REQUIRED_PATHS = [
    "README.md",
    "core/VOICE.md",
    "core/STYLE_GUIDE.md",
    "core/BRAND_VOICE.md",
    "core/CONTENT_STRATEGY.md",
    "core/GOVERNANCE.md",
    "core/CLAIMS_POLICY.md",
    "core/DEVELOPER_FLUENCY.md",
    "core/DISTRIBUTION_STRATEGY.md",
    "core/EDITORIAL_PRINCIPLES.md",
    "skills/README.md",
    "playbooks/README.md",
    "prompts/README.md",
    "rubrics/README.md",
    "workflows/README.md",
    "tests/README.md",
]

REQUIRED_SKILLS = [
    "skills/foundation/ai-researcher/SKILL.md",
    "skills/foundation/dev-copywriter/SKILL.md",
    "skills/foundation/dev-reviewer/SKILL.md",
    "skills/foundation/founder-x-recap/SKILL.md",
    "skills/editorial/editorial-director/SKILL.md",
    "skills/editorial/managing-editor/SKILL.md",
    "skills/editorial/copy-chief/SKILL.md",
    "skills/editorial/content-ops-manager/SKILL.md",
    "skills/specialization/technical-fact-checker/SKILL.md",
    "skills/specialization/seo-strategist/SKILL.md",
    "skills/specialization/launch-comms-writer/SKILL.md",
    "skills/specialization/social-editor/SKILL.md",
    "skills/specialization/customer-story-producer/SKILL.md",
    "skills/specialization/analyst-relations-writer/SKILL.md",
    "skills/specialization/executive-comms-writer/SKILL.md",
    "skills/specialization/lifecycle-email-writer/SKILL.md",
    "skills/specialization/content-repurposer/SKILL.md",
    "skills/quality/claims-risk-reviewer/SKILL.md",
    "skills/quality/narrative-consistency-reviewer/SKILL.md",
    "skills/quality/final-publish-reviewer/SKILL.md",
]

def main() -> int:
    missing = []
    for item in REQUIRED_PATHS + REQUIRED_SKILLS:
        if not Path(item).exists():
            missing.append(item)
    if missing:
        print("Missing required files:")
        for item in missing:
            print(f"- {item}")
        return 1
    print("Repository structure validation passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
