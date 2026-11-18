#!/usr/bin/env python3
"""Validate the ETB registry and keep its index current.

    python3 registry/scripts/validate.py                 check every entry, the index and the README table
    python3 registry/scripts/validate.py --write-index   rebuild registry/index.json and the README table
    python3 registry/scripts/validate.py --root DIR      run against another copy of the repository

Needs: pip install jsonschema rfc3339-validator

Checks, for every JSON file in registry/entries:

1. The file name is the id, and the id matches ETB-YYYY-NNNN.
2. The record validates against the upstream OSV 1.9.2 schema when its id is written in
   OSV's local-database form, x_ETB-... (the ETB prefix is not registered with the OSV
   schema project).
3. database_specific validates against registry/schema/etb-database-specific.schema.json.
4. Every class the entry cites is listed in registry/schema/etb-classes.json.
5. published and modified are RFC 3339 UTC times, published is not after modified, the
   disclosure status is "published", and registry_published is the date of published.
6. The entry has at least one FIX or REPORT reference and at least one credit, and each
   credit name has the form Name (Affiliation).
7. Every id under related is an entry in this registry, and no entry lists itself.

Then: registry/index.json and the table in README.md match what the entries give.

Exit status 1 on any failure.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ID_RE = re.compile(r"^ETB-(20[2-9][0-9])-([0-9]{4})$")
RFC3339_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")
TABLE_START = "<!-- records:start -->"
TABLE_END = "<!-- records:end -->"
INDEX_SCHEMA = "etb-registry-index/1"


def load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def entry_paths(root: Path) -> list[Path]:
    return sorted((root / "registry" / "entries").glob("ETB-*.json"))


def check_entry(path: Path, osv_validator, etb_validator, classes: set[str], ids: set[str]) -> list[str]:
    name = path.name
    try:
        rec = load(path)
    except json.JSONDecodeError as exc:
        return [f"{name}: invalid JSON: {exc}"]
    if not isinstance(rec, dict):
        return [f"{name}: the record must be a JSON object"]
    errors: list[str] = []

    rid = rec.get("id", "")
    if not isinstance(rid, str) or not ID_RE.match(rid):
        errors.append(f"{name}: id {rid!r} does not match ETB-YYYY-NNNN")
        rid = str(rid)
    if path.stem != rid:
        errors.append(f"{name}: file name does not match id {rid!r}")

    shadow = dict(rec)
    shadow["id"] = "x_" + rid
    for err in sorted(osv_validator.iter_errors(shadow), key=lambda e: list(map(str, e.path))):
        errors.append(f"{name}: OSV schema: {'/'.join(map(str, err.path)) or '<root>'}: {err.message}")

    ds = rec.get("database_specific")
    etb = ds.get("etb") if isinstance(ds, dict) else None
    if not isinstance(etb, dict):
        errors.append(f"{name}: database_specific.etb block missing")
        etb = {}
    else:
        for err in sorted(etb_validator.iter_errors(ds), key=lambda e: list(map(str, e.path))):
            errors.append(f"{name}: ETB block: {'/'.join(map(str, err.path)) or '<root>'}: {err.message}")
    for cls in etb.get("classes") or []:
        if cls not in classes:
            errors.append(f"{name}: class {cls} is not listed in registry/schema/etb-classes.json")

    disclosure = etb.get("disclosure") if isinstance(etb.get("disclosure"), dict) else {}
    published = rec.get("published")
    modified = rec.get("modified")
    if not isinstance(modified, str) or not RFC3339_RE.match(modified):
        errors.append(f"{name}: modified {modified!r} is not an RFC 3339 UTC time")
    if not isinstance(published, str) or not RFC3339_RE.match(published):
        errors.append(f"{name}: published {published!r} is not an RFC 3339 UTC time")
    else:
        if isinstance(modified, str) and RFC3339_RE.match(modified) and published > modified:
            errors.append(f"{name}: published is after modified")
        if disclosure.get("registry_published") != published[:10]:
            errors.append(f"{name}: disclosure.registry_published must be the date of published ({published[:10]})")
    if disclosure.get("status") != "published":
        errors.append(f"{name}: disclosure.status must be 'published'")

    ref_types = {r.get("type") for r in rec.get("references") or [] if isinstance(r, dict)}
    if not ref_types & {"FIX", "REPORT"}:
        errors.append(f"{name}: needs at least one FIX or REPORT reference")
    credits = rec.get("credits") or []
    if not credits:
        errors.append(f"{name}: needs at least one credit")
    for credit in credits:
        cname = credit.get("name", "") if isinstance(credit, dict) else ""
        if "(" not in cname or not cname.rstrip().endswith(")"):
            errors.append(f"{name}: credit {cname!r} should be 'Name (Affiliation)'")

    for other in rec.get("related") or []:
        if other == rid:
            errors.append(f"{name}: related lists the entry itself")
        elif other not in ids:
            errors.append(f"{name}: related id {other} is not an entry in this registry")
    return errors


def index_row(rec: dict) -> dict:
    etb = rec["database_specific"]["etb"]
    target = etb["target"]
    disclosure = etb["disclosure"]
    return {
        "id": rec["id"],
        "path": f"registry/entries/{rec['id']}.json",
        "summary": rec.get("summary", ""),
        "classes": list(etb["classes"]),
        "target": {"name": target["name"], "kind": target["kind"], "repo": target["repo"]},
        "upstream": {"fixed": disclosure.get("fixed"), "released": disclosure.get("released")},
        "published": rec["published"],
        "modified": rec["modified"],
    }


def build_index(records: list[dict]) -> dict:
    rows = [index_row(r) for r in sorted(records, key=lambda r: r["id"])]
    return {"schema": INDEX_SCHEMA, "count": len(rows), "records": rows}


def render_index(index: dict) -> str:
    return json.dumps(index, indent=2, ensure_ascii=False) + "\n"


def cell(text: str) -> str:
    return " ".join(str(text).split()).replace("|", "\\|")


def render_table(index: dict) -> str:
    lines = ["| ID | Target | Class | Upstream fix | Published here |", "|---|---|---|---|---|"]
    for row in index["records"]:
        fixed, released = row["upstream"]["fixed"], row["upstream"]["released"]
        if fixed and released:
            upstream = f"{fixed}. {released}"
        elif fixed:
            upstream = fixed
        else:
            upstream = f"No fix. {released}" if released else "No fix"
        lines.append(f"| [{row['id']}]({row['path']}) | {cell(row['target']['name'])} | {', '.join(row['classes'])} "
                     f"| {cell(upstream)} | {row['published'][:10]} |")
    return "\n".join(lines)


def replace_table(readme: str, table: str) -> str | None:
    start, end = readme.find(TABLE_START), readme.find(TABLE_END)
    if start < 0 or end < start:
        return None
    return readme[: start + len(TABLE_START)] + "\n" + table + "\n" + readme[end:]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate the ETB registry and keep its index current.")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2]), help="repository root")
    ap.add_argument("--write-index", action="store_true", help="rebuild registry/index.json and the README table")
    args = ap.parse_args(argv)
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        print("jsonschema is required: pip install jsonschema rfc3339-validator", file=sys.stderr)
        return 2

    root = Path(args.root).resolve()
    schema_dir = root / "registry" / "schema"
    osv_validator = Draft202012Validator(load(schema_dir / "osv-1.9.2.schema.json"), format_checker=FormatChecker())
    etb_validator = Draft202012Validator(load(schema_dir / "etb-database-specific.schema.json"),
                                         format_checker=FormatChecker())
    classes = set(load(schema_dir / "etb-classes.json")["classes"])
    paths = entry_paths(root)
    ids = {p.stem for p in paths}

    errors: list[str] = []
    for path in paths:
        errors += check_entry(path, osv_validator, etb_validator, classes, ids)

    index_path = root / "registry" / "index.json"
    readme_path = root / "README.md"
    if not errors:
        index = build_index([load(p) for p in paths])
        table = render_table(index)
        readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
        new_readme = replace_table(readme, table)
        if args.write_index:
            index_path.write_text(render_index(index), encoding="utf-8")
            if new_readme is None:
                errors.append(f"README.md: the table markers {TABLE_START} and {TABLE_END} are missing")
            elif new_readme != readme:
                readme_path.write_text(new_readme, encoding="utf-8")
            print(f"wrote {index_path.relative_to(root)} and the README table: {index['count']} record(s)")
        else:
            current = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
            if current != render_index(index):
                errors.append("registry/index.json does not match the entries; run validate.py --write-index")
            if new_readme is None:
                errors.append(f"README.md: the table markers {TABLE_START} and {TABLE_END} are missing")
            elif new_readme != readme:
                errors.append("README.md: the records table does not match the entries; run validate.py --write-index")
    elif args.write_index:
        print("the index was not written: fix the entries first", file=sys.stderr)

    for line in errors:
        print("FAIL", line)
    print(f"checked {len(paths)} record(s), {len(errors)} error(s), classes listed: {len(classes)}")
    print("validated at " + datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
