# govspends

Public-records investigations of government budgets, built in the open. **Website: https://govspends.github.io/govspends/**

Each investigation is a report you can read as web pages (or as a PDF rebuilt from those pages), plus everything behind it: every source document with its checksum, the data tables parsed from those documents, the scripts that parse them and draw the charts, notes, an audit summary of how the work was done, and any independent review. Anyone can propose a correction or an addition with a pull request; see [CONTRIBUTING.md](CONTRIBUTING.md).

## Investigations

| Path | Report | Status |
|---|---|---|
| `us/national/fy2026-spending-controls-and-trust-funds` | [United States: how federal spending is controlled, and the Social Security and Medicare trust funds](https://govspends.github.io/govspends/us/national/fy2026-spending-controls-and-trust-funds/) | Revision 1 (2026-10-06), not yet independently reviewed |
| `us/tx/counties/harris/fy2027-budget` | [Harris County, Texas: FY2027 budget](https://govspends.github.io/govspends/us/tx/counties/harris/fy2027-budget/) | Revision 2 (2026-09-23), independently reviewed |

## How it is organized

Every government has **its own repository**, named after its place in the hierarchy **country / state or province / level / government**:

| Government | Repository | Pages |
|---|---|---|
| United States federal government | [govspends/us-national](https://github.com/govspends/us-national) | https://govspends.github.io/govspends/us/national/ |
| Harris County, Texas | [govspends/us-tx-counties-harris](https://github.com/govspends/us-tx-counties-harris) | https://govspends.github.io/govspends/us/tx/counties/harris/ |

Levels are `national`, `state`, `counties` (county-equivalents such as parishes and boroughs), `cities` (municipalities of any kind) and `districts` (school, hospital, flood-control, port, utility and other special-purpose governments); country and state codes are ISO 3166. A government repository holds `jurisdiction.toml` (its entry: name, level, fiscal year, websites, and its investigations), `docs/` (its profile page and one folder of report pages per investigation) and `investigations/` (the evidence behind each report: sources, data, scripts, notes, manifests, reviews).

This hub repository holds the landing page, the pages for countries and states, the [structure guide](docs/about/structure.md), the shared tools, and `governments.toml`, the list of government repositories. At build time the hub clones each government repository, assembles one site with a single navigation and search, builds a PDF of every report from its pages, and publishes to GitHub Pages. A merge to `main` in any government repository triggers that rebuild; the hub also rebuilds daily as a safety net. Edit links on a government's pages open that government's repository.

```
governments.toml             the registry of government repositories and hub-owned jurisdictions
docs/                        landing page, about/structure.md, <country>/index.md, <country>/<state>/index.md, stylesheets
tools/                       assemble.py (clone repos, compose build/docs, fill the nav), build_site.py (nav, landing
                             table, jurisdiction pages), build_pdf.py (pages -> PDF), sync_docs.py, build_tables.py,
                             run_checks.py (used inside government repositories), export_markdown.py, mkdocs_hooks.py
mkdocs.yml                   site configuration (the nav is completed at build time into build/mkdocs.yml)
.github/workflows/build.yml  assemble, PDFs, mkdocs build --strict, deploy to Pages
```

## Build locally

```bash
pip install -r requirements.txt
python3 tools/assemble.py                 # clones the government repositories into build/repos and composes build/docs
mkdocs serve -f build/mkdocs.yml          # preview at http://127.0.0.1:8000
python3 tools/build_pdf.py                # PDFs into build/docs/<path>/<investigation>/
```

**Working on a government locally:** clone its repository inside this folder under its GitHub name (`git clone git@github.com:govspends/us-tx-counties-harris.git` here, giving `govspends/us-tx-counties-harris/`). The hub's git ignores these folders, `tools/assemble.py` uses them instead of cloning, and the government repository's `./tools.sh` finds the hub's tools in the parent folder. A checkout elsewhere can be used with `python3 tools/assemble.py --local us/tx/counties/harris=/path/to/it`.

## Adding a government

Create a repository `govspends/<country>-<state>-<level>-<slug>` from the shape of an existing one (a `jurisdiction.toml`, `docs/index.md`, and per investigation `docs/<name>/` and `investigations/<name>/`), add it to `governments.toml` here, and add the country or state page under `docs/` if it is new. See [How govspends is organized](docs/about/structure.md).

## Provenance

The federal investigation (in [govspends/us-national](https://github.com/govspends/us-national)) was prepared on 2026-10-05/06 with an AI assistant (Claude) from government documents only; it began as seven questions whose original answers are kept in its notes, and its [audit summary](https://github.com/govspends/us-national/blob/main/investigations/fy2026-spending-controls-and-trust-funds/AUDIT_SUMMARY.md) lists every correction made when they were checked. The Harris County investigation (in its own repository) was prepared on 2026-09-21 with an AI assistant (Claude) working from public records under a person's direction, reviewed independently on 2026-09-23, and revised the same day. Its [audit summary](https://github.com/govspends/us-tx-counties-harris/blob/main/investigations/fy2027-budget/AUDIT_SUMMARY.md) records the method, judgment calls, defects found and fixed, and how to re-verify every figure. Full-page copies of news articles used in the research are kept in a private archive and are not republished here; they are cited by URL.

## License

Text, data and images: [CC BY 4.0](LICENSE-CONTENT.md). Code: [MIT](LICENSE). Not affiliated with any government; not legal or financial advice.
