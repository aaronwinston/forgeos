from pathlib import Path
import argparse
import re

RISKY_PHRASES = [
    "unlock",
    "unleash",
    "revolutionary",
    "game-changing",
    "seamless",
    "next-generation",
    "guarantee",
    "eliminate hallucinations",
    "fully automated",
]

def main() -> None:
    parser = argparse.ArgumentParser(description="Run a basic editorial check on a markdown file.")
    parser.add_argument("file")
    args = parser.parse_args()

    path = Path(args.file)
    text = path.read_text(encoding="utf-8")
    lower = text.lower()

    print(f"Editorial check: {path}")
    print()

    found = []
    for phrase in RISKY_PHRASES:
        if phrase in lower:
            found.append(phrase)

    if found:
        print("Potential risky or weak phrases:")
        for phrase in found:
            print(f"- {phrase}")
    else:
        print("No risky phrases from the basic list were found.")

    em_dash_count = text.count("\u2014")
    if em_dash_count:
        print(f"\nFound {em_dash_count} em dash(es). Consider replacing them.")

    headings = re.findall(r"^#+\s+", text, flags=re.MULTILINE)
    print(f"\nHeading count: {len(headings)}")

if __name__ == "__main__":
    main()
