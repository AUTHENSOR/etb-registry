# ETB registry

A public, machine-readable record of evaluation-integrity flaws. Each entry is one JSON file in
[OSV format](https://ossf.github.io/osv-schema/) with a stable id that others can cite. Maintained by
Authensor, Inc.

ETB stands for Evaluator Trust Boundary: the line between what an evaluation trusts and what the system under
evaluation controls. The classes ETB-01 to ETB-10 are defined in
[TAXONOMY.md](https://github.com/AUTHENSOR/etb-scan/blob/main/TAXONOMY.md) in `AUTHENSOR/etb-scan`
(paper: [10.5281/zenodo.21633620](https://doi.org/10.5281/zenodo.21633620)).

## What an entry is

An entry describes a flaw that gives the system under evaluation a way to influence its own score or verdict in a
named, public grader, judge, monitor, benchmark, harness, metric or detector. The flaw is documented on the public
pages the entry links.

- One entry per target and mechanism. A chain that uses several mechanisms gets several entries, linked through
  `related`.
- The target and the report are public. Every entry links the upstream report or the fix.
- An entry is about a system, not about a person.
- Unless an entry says so, it makes no claim that any published result was affected.
- How far a flaw was shown differs between entries. Some rest on a run that shows a score or verdict changing,
  sometimes with the judge model stubbed or mocked. Some rest on the code path, with tests at the level of a parser,
  an extraction step or a prompt builder. `attack.demonstrated`, `attack.preconditions` and `unverified` say which
  applies. `demonstrated: false` means no public page shows the flaw changing a score or verdict in a run.

Not an entry:

- A defect that makes a score wrong but gives the evaluated system no way to trigger it. Those belong in the
  [evidence table](https://github.com/AUTHENSOR/etb-scan/blob/main/EVIDENCE-TABLE.md) of `AUTHENSOR/etb-scan`.
- A dataset quality problem that cannot be exploited, such as a wrong test.

## Records

<!-- records:start -->
| ID | Target | Class | Upstream fix | Published here |
|---|---|---|---|---|
| [ETB-2026-0001](registry/entries/ETB-2026-0001.json) | ControlArena | ETB-02 | 2026-08-10. control-arena 15.0.0, 16.0.0 and 20.0.0 (one part of the fix each) | 2026-11-18 |
| [ETB-2026-0002](registry/entries/ETB-2026-0002.json) | SWE-bench evaluation harness | ETB-09 | 2026-08-14. swebench 5.0.0 | 2026-11-18 |
| [ETB-2026-0027](registry/entries/ETB-2026-0027.json) | Inspect AI model-graded scorers | ETB-02 | 2026-11-04. inspect-ai 0.3.288 | 2026-11-18 |
| [ETB-2026-0029](registry/entries/ETB-2026-0029.json) | Presidio EmailRecognizer | ETB-06 | 2026-06-24. presidio-analyzer 2.2.363 | 2026-11-18 |
| [ETB-2026-0033](registry/entries/ETB-2026-0033.json) | Presidio Spanish NIF and NIE recognizers | ETB-06 | 2026-07-01. presidio-analyzer 2.2.364 | 2026-11-18 |
| [ETB-2026-0034](registry/entries/ETB-2026-0034.json) | garak StringDetector | ETB-06 | No fix. No release changes the default; the maintainer says that is by design. An opt-in `normalize` option is available from garak 0.16.0 (2026-08-04). | 2026-11-18 |
| [ETB-2026-0035](registry/entries/ETB-2026-0035.json) | OpenCompass code-execution evaluators | ETB-09 | 2026-07-28. opencompass 0.5.4 | 2026-11-18 |
| [ETB-2026-0036](registry/entries/ETB-2026-0036.json) | EvalScope AIME and AIR-Bench Chat judge parsers | ETB-01 | 2026-08-17. evalscope 1.11.0 | 2026-11-18 |
| [ETB-2026-0037](registry/entries/ETB-2026-0037.json) | Inspect Evals gdm_stealth oversight rater | ETB-01 | 2026-08-17. inspect-evals 0.18.0 | 2026-11-18 |
| [ETB-2026-0038](registry/entries/ETB-2026-0038.json) | Delphi explainer label parser | ETB-02, ETB-01 | 2026-08-25. eai-delphi 0.1.4 (git tag v0.1.4) | 2026-11-18 |
| [ETB-2026-0039](registry/entries/ETB-2026-0039.json) | EvalScope LLM judge prompt builder | ETB-02 | 2026-09-07. evalscope 1.12.0 | 2026-11-18 |
| [ETB-2026-0042](registry/entries/ETB-2026-0042.json) | PyRIT scoring objective extraction | ETB-02 | 2026-10-20. pyrit 1.2.0 | 2026-11-18 |
| [ETB-2026-0045](registry/entries/ETB-2026-0045.json) | PyRIT ConversationScorer transcript renderer | ETB-02 | 2026-10-21. pyrit 1.2.0 | 2026-11-18 |
| [ETB-2026-0046](registry/entries/ETB-2026-0046.json) | PyRIT judge JSON extraction | ETB-01 | 2026-10-25. pyrit 1.2.0 | 2026-11-18 |
<!-- records:end -->

The same list is in [`registry/index.json`](registry/index.json).

## Identifier

`ETB-YYYY-NNNN`: the year the record was created and a four-digit sequence that restarts each year. The short
form `ETB-NNNN` is never used, so a record id cannot be confused with a class id `ETB-NN`.

- An id is assigned when a record is first written. It is never reused and never renumbered.
- The sequence has gaps. Not every record that gets an id is published.
- Cite an entry by its id and its URL in this repository, for example
  `ETB-2026-0027, https://github.com/AUTHENSOR/etb-registry/blob/main/registry/entries/ETB-2026-0027.json`.

## When an entry is published

Authensor's disclosure policy is
[DISCLOSURE.md](https://github.com/AUTHENSOR/etb-scan/blob/main/DISCLOSURE.md) in `AUTHENSOR/etb-scan`. This
registry adds a waiting rule for its entries:

- Nothing is published before the maintainer has been told.
- Tier 1 (the artifact is public and the impact is a wrong score): no earlier than 14 days after the upstream
  filing, or when a fix lands, whichever comes first.
- Tier 2 (impact beyond a wrong score, such as code execution on a scoring service): no earlier than 90 days
  after the report, or when a fix ships, whichever comes first. Earlier only when the maintainer agrees.
- Each entry states its tier and the reason under `disclosure`.

`published` is the time the entry appeared here. An entry can change afterwards: `modified` gives the time of the
last change. The class of an entry can change when the class list grows. The id stays. An entry that turns out to
be wrong is not deleted. It gets OSV's `withdrawn` time and stays in place.

## Credit

Entries use the OSV credit types. A person can hold more than one.

| Type | Who |
|---|---|
| `FINDER` | Found the flaw. |
| `REPORTER` | Reported the flaw upstream, when that was not the finder. |
| `REMEDIATION_DEVELOPER` | Wrote a commit inside the merged fix that changes the fixed code or adds test cases for it. |
| `REMEDIATION_REVIEWER` | Reviewed, approved or merged the fix. |
| `REMEDIATION_VERIFIER` | Tested the fix. |

- Credits name the people who found, reported, fixed, reviewed or tested a flaw, as the linked public pages show.
  No entry names a person as the cause of a flaw.
- Names have the form `Name (Affiliation)`.
- Maintainers and contributors are credited by GitHub handle, with the role the public page shows. Their
  affiliations are not checked.
- Merges of the base branch, formatting, version bumps and changelog wording do not count as development.
- Authensor's own line is `John Kearney (Authensor Research)`.
- To change how you are credited, or to be removed, write to john@authensor.com.

## Record layout

Standard OSV fields: `schema_version` (1.9.2), `id`, `modified`, `published`, `withdrawn`, `aliases`, `related`,
`summary`, `details`, `affected`, `references`, `credits`. The `ETB` prefix is not registered with the OSV schema
project, so an OSV validator accepts these records with the id in the local-database form `x_ETB-...`.

`database_specific.etb` (schema: [`registry/schema/etb-database-specific.schema.json`](registry/schema/etb-database-specific.schema.json)).
The `$id` in that schema is a name. Nothing is served at that address; the schema is the file in this repository.

| Field | Content |
|---|---|
| `classes` | The ETB classes the flaw exercises. The allowed ids are in `registry/schema/etb-classes.json`. |
| `family` | `verdict-path`, `aggregation`, `detection-coverage` or `sandbox-environment`. |
| `target` | Kind, name, repository, components and affected versions. |
| `attack` | Description, preconditions, whether it was demonstrated, and where the proof of concept is. |
| `hardening` | The fix, the fix pattern (the class's fix pattern in `TAXONOMY.md`, quoted) and the risk that remains. The remaining risk is Authensor's own reading of the merged code and the linked pages. It is not a statement by the maintainers unless the entry says so. |
| `disclosure` | Tier and reason, channel, the dates it was reported, acknowledged and fixed, the release, and the date it was published here. `acknowledged` is the date of the maintainer's first reply, review or change on the report or on its fix. When there was none before the merge, it is the merge date. A base-branch update alone does not count. |
| `cross_references` | CWE, MITRE ATLAS, OWASP and NIST mappings. Each is a best fit unless it says exact. The OWASP item is Authensor's own proposal and an ATLAS `case_study` line is Authensor's own submission, until the text says it was published. |
| `harness` | Probes and attacker strategies that measure the class. |
| `evidence` | Links, each with a note. |
| `severity_self` | Authensor's own rating, or null when none was made. |
| `unverified` | Every claim in the record that was not checked against a primary source. |

## Checking the registry

```bash
pip install jsonschema rfc3339-validator
python3 registry/scripts/validate.py
```

The validator checks every entry against the OSV 1.9.2 schema and the ETB block schema, checks ids, dates,
classes, references, credits and `related` links, and checks that `registry/index.json` and the table above match
the entries. `python3 registry/scripts/validate.py --write-index` rebuilds both.

## Corrections and reports

- To correct an entry, or to dispute one: john@authensor.com, or open an issue here.
- To report a flaw in an evaluation, or in Authensor's own software: see
  [DISCLOSURE.md](https://github.com/AUTHENSOR/etb-scan/blob/main/DISCLOSURE.md) in `AUTHENSOR/etb-scan`.

## Licence

Entries, the index and this README are under [CC BY 4.0](LICENSE-DATA). The validator and the schemas
are under [Apache-2.0](LICENSE). `registry/schema/osv-1.9.2.schema.json` is the OSV schema project's file,
unchanged.
