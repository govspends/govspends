# Contributing to govspends

Thank you for helping keep these investigations accurate. Everything on the website lives in a repository, so a change to the site is a pull request. **Content about a government (report pages, evidence, notes) lives in that government's repository**, for example [govspends/us-tx-counties-harris](https://github.com/govspends/us-tx-counties-harris); the pencil icon on any page opens the right one. This hub repository holds the landing page, the country and state pages, the tools and the registry of government repositories.

## The one rule: show the source

Every factual statement and number must be traceable to a document a reader can open. When you change or add a figure:

1. Cite the document and the page (printed page number of the county document, or the PDF page where noted).
2. If the document is not already under `investigations/<investigation>/sources/`, add it there and add a row to that investigation's `REFERENCES.md` (URL, retrieval date, local file name, what it is used for). Government documents are public records and can be saved in full. Do **not** add full copies of news articles or other copyrighted pages; cite them by URL and put the facts you rely on in the notes.
3. If the figure comes from a data file, change the data file (or the script that produces it) rather than typing the number into the page, then run `python3 tools/build_tables.py` so the generated tables update.

## How to propose a change

**Small text fix:** open the page on the website, click the pencil ("Edit this page") icon. GitHub forks the repository for you; edit the Markdown, write a short description, and open a pull request.

**Larger change:** fork the government's repository, clone, create a branch, edit, and open a pull request. `./tools.sh <tool>` in that repository runs the shared checks (it fetches this hub's tools on first use). To preview the whole site with your local changes, clone this hub, clone the government repository inside it under its GitHub name, and run `python3 tools/assemble.py` then `mkdocs serve -f build/mkdocs.yml`.

The pull-request template asks you to confirm the source rule and to describe what changed and why.

## Where things live

| You want to change | Edit |
|---|---|
| Report text, a table typed by hand, a caption | `docs/<investigation>/*.md` in the government's repository |
| A table marked `generated:` in the page | the CSV/JSON under `investigations/<investigation>/data/` in the government's repository, or the script that builds it, then `./tools.sh build_tables` |
| A chart | `investigations/<investigation>/scripts/make_charts.py` in the government's repository, run it, then `./tools.sh build_tables` |
| References, the audit summary, the notes | the files under `investigations/<investigation>/` in the government's repository, then `./tools.sh sync_docs` |
| A government's profile page | the prose on `docs/index.md` in its repository (the block between the `generated:jurisdiction` markers comes from `jurisdiction.toml`) |
| A country or state page, the landing page, the tools | this hub repository (`docs/`, `tools/`) |
| A new government | a new repository plus a line in `governments.toml` here; see [How govspends is organized](docs/about/structure.md) |
| A source document | add it under `investigations/<investigation>/sources/` in the government's repository, add a `REFERENCES.md` row, and update `MANIFEST_SHA256.txt` (or ask a maintainer to) |

Continuous integration in each government repository checks that the parsers still reproduce the data tables, that generated tables and synced pages are current, and that the PDF builds; after a merge it asks the hub to rebuild the site. A maintainer reviews every pull request for sourcing before merging.

## Corrections policy

Substantive corrections are recorded in the report's Appendix B revision history and in the audit summary, with what was wrong and what changed. Independent reviews are published unchanged.

## Adding a government or an investigation

A new government gets its own repository, named after its path with dashes (`govspends/us-tx-cities-houston`, `govspends/us-tx-state`, `govspends/ca-on-cities-toronto`), containing `jurisdiction.toml`, `docs/index.md` and, per investigation, `docs/<name>/` and `investigations/<name>/`; then add one `[[government]]` entry to `governments.toml` in this hub and, if the country or state is new, its page under `docs/`. A new investigation of an existing government is an `[[investigation]]` entry in that repository's `jurisdiction.toml` plus the two folders. Details in [How govspends is organized](docs/about/structure.md).

## Style

Plain language. One idea per sentence. Dollar figures rounded to $0.1M in prose, exact in tables. Say which document a number comes from. Do not describe intent ("hidden", "concealed") unless a document supports it; describe what the documents show and where.

## Licensing of contributions

By contributing you agree that your text and data contributions are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) and your code contributions under the [MIT License](LICENSE), the same terms as the rest of the repository.
