"""Extract the 29 IMP rules (CC BY 4.0) from a saved rules page into markdown.

Usage: extract_rules.py <rules.html> <out.md>
Writes one section per rule: 2026 title, the 1999 rule, the reasoning,
and the related essays/tools links. Prints one summary line.
"""
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify

BASE = "https://impatientprogramming.org"
PAGE = BASE + "/rules/"

HEADER = """# The 29 rules of Impatient Programming

Source: [The rules that govern how we work]({page}) by Obie Fernandez,
impatientprogramming.org, licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Changes: reformatted from HTML to markdown, one section per rule; "Revisit this rule"
links and images removed. Text otherwise unchanged. Snapshot: {date}.

Each rule shows the 2026 IMP rule, then Don Wells's 1999 XP rule it revisits.
Anchor links (`{page}#rule-N`) point to the live page.
"""


def md(node) -> str:
    for a in node.find_all("a", href=True):
        if a["href"].startswith("/"):
            a["href"] = BASE + a["href"]
        elif a["href"].startswith("#"):
            a["href"] = PAGE + a["href"]
    text = markdownify(str(node), heading_style="ATX", bullets="-").strip()
    return "\n".join(line.rstrip() for line in text.splitlines())


def extract(src: Path, dst: Path, date: str) -> None:
    soup = BeautifulSoup(src.read_text(encoding="utf-8"), "html.parser")
    out = [HEADER.format(page=PAGE, date=date)]
    count = 0
    for group in soup.select("section.rules-group"):
        heading = group.find(["h2"])
        out.append(f"## {heading.get_text(strip=True)}\n")
        for rule in group.select("li.rule"):
            num = rule["id"].split("-")[1]
            then = rule.select_one(".rule__xp").get_text(" ", strip=True)
            now = rule.select_one(".rule__now")
            title = now.select_one(".rule__imp").get_text(" ", strip=True)
            for tag in now.select(".rule__year, .rule__imp, .rule__revisit, svg, img, figure > img"):
                tag.decompose()
            body = md(now)
            while "\n\n\n" in body:
                body = body.replace("\n\n\n", "\n\n")
            out.append(f"### Rule {num}: {title}\n\n1999: *{then}*  \nLink: {PAGE}#rule-{num}\n\n{body}\n")
            count += 1
    if count != 29:
        sys.exit(f"error: expected 29 rules, found {count}; the page layout may have changed")
    dst.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    print(f"{src.name} -> {dst}: {count} rules")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: extract_rules.py <rules.html> <out.md> <snapshot-date>")
    extract(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3])
