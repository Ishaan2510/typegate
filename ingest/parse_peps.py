"""Raw PEP loader (stage 1 of 2).

Reads pep-*.rst files from a local clone of github.com/python/peps and writes
data/peps_raw.json. This stage only extracts what is literally in the file:
header fields, the section tree, each section's text, and where in that tree
each mention of another PEP appears. No schema is applied here; the knowledge
graph is built from this file by kg/build_graph.py.

Usage:
    git clone https://github.com/python/peps.git
    python ingest/parse_peps.py --peps-dir peps/peps --out data/peps_raw.json
"""
import argparse
import glob
import json
import os
import re

HEADER_RE = re.compile(r"^([A-Za-z-]+):\s*(.*)$")
PEP_MENTION_RE = re.compile(r":pep:`(?:[^`<]*<)?(\d+)|\bPEP[ -](\d{1,4})\b")
UNDERLINE_RE = re.compile(r"^([=\-~^\"'`#*+])\1{2,}\s*$")


def parse_header(block):
    """RFC-822 style header block -> dict, joining continuation lines."""
    header, key = {}, None
    for line in block.split("\n"):
        m = HEADER_RE.match(line)
        if m:
            key = m.group(1)
            header[key] = m.group(2).strip()
        elif key and line[:1] in (" ", "\t"):
            header[key] += " " + line.strip()
    return header


def parse_sections(body):
    """Split an RST body into a flat list of sections with a parent chain.

    RST has no fixed heading characters: the first underline character seen
    is level 1, the next new one is level 2, and so on. Each section records
    its title, level, the titles of its ancestors, and its own text (up to the
    next heading of any level).
    """
    lines = body.split("\n")
    heads = []  # (line_index_of_title, title, char)
    for i in range(1, len(lines)):
        title = lines[i - 1].strip()
        m = UNDERLINE_RE.match(lines[i])
        if (m and title and not UNDERLINE_RE.match(lines[i - 1])
                and len(lines[i].strip()) >= len(title)):
            heads.append((i - 1, title, m.group(1)))

    level_of = {}
    for _, _, ch in heads:
        level_of.setdefault(ch, len(level_of) + 1)

    sections, stack = [], []  # stack holds (level, title)
    for k, (start, title, ch) in enumerate(heads):
        level = level_of[ch]
        while stack and stack[-1][0] >= level:
            stack.pop()
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        text = "\n".join(lines[start + 2:end]).strip()
        sections.append({
            "index": k,
            "title": title,
            "level": level,
            "ancestors": [t for _, t in stack],
            "text": text,
        })
        stack.append((level, title))
    preamble_end = heads[0][0] if heads else len(lines)
    return sections, "\n".join(lines[:preamble_end])


def find_mentions(text, own_number):
    out = []
    for m in PEP_MENTION_RE.finditer(text):
        n = int(m.group(1) or m.group(2))
        if n != own_number:
            out.append(n)
    return out


def parse_pep(path):
    text = open(path, encoding="utf-8").read()
    header_block, _, body = text.partition("\n\n")
    header = parse_header(header_block)
    number = int(header.get("PEP", re.search(r"pep-(\d+)", path).group(1)))
    sections, preamble = parse_sections(body)
    mentions = [{"target": n, "section_index": None} for n in find_mentions(preamble, number)]
    for s in sections:
        mentions += [{"target": n, "section_index": s["index"]}
                     for n in find_mentions(s["text"], number)]
    return {
        "number": number,
        "header": header,
        "sections": sections,
        "mentions": mentions,
        "mentions_typing_extensions": "typing_extensions" in body,
        "word_count": len(body.split()),
        "source_file": os.path.basename(path),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--peps-dir", default="peps/peps")
    ap.add_argument("--out", default="data/peps_raw.json")
    args = ap.parse_args()
    files = sorted(glob.glob(os.path.join(args.peps_dir, "pep-*.rst")))
    if not files:
        raise SystemExit(f"no pep-*.rst files under {args.peps_dir}")
    records = [parse_pep(f) for f in files]
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=1, ensure_ascii=False)
    print(f"parsed {len(records)} PEPs -> {args.out}")


if __name__ == "__main__":
    main()
