from pathlib import Path
import argparse
import shutil
import datetime

TEMPLATES = {
    "blog": "briefs/blog-brief-template.md",
    "launch": "briefs/launch-brief-template.md",
    "case-study": "briefs/case-study-brief-template.md",
    "analyst": "briefs/analyst-comms-brief-template.md",
    "founder-social": "briefs/founder-social-brief-template.md",
    "technical-guide": "briefs/technical-guide-brief-template.md",
    "newsletter": "briefs/newsletter-brief-template.md",
    "campaign": "briefs/campaign-brief-template.md",
}

def slugify(value: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in value).strip("-").replace("--", "-")

def main() -> None:
    parser = argparse.ArgumentParser(description="Create a content brief from a template.")
    parser.add_argument("type", choices=TEMPLATES.keys())
    parser.add_argument("title")
    parser.add_argument("--out-dir", default="briefs/drafts")
    args = parser.parse_args()

    template = Path(TEMPLATES[args.type])
    if not template.exists():
        raise FileNotFoundError(f"Template not found: {template}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    date = datetime.date.today().isoformat()
    filename = f"{date}-{slugify(args.title)}.md"
    destination = out_dir / filename

    shutil.copyfile(template, destination)
    print(f"Created {destination}")

if __name__ == "__main__":
    main()
