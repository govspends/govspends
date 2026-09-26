# How govspends is organized

govspends files every government in a hierarchy of **country, state or province, level, government**, and each report under the government it examines. The address of a page tells you where you are:

```
govspends.github.io/govspends/us/tx/counties/harris/fy2027-budget/
                              |  |  |        |      +- investigation: fiscal year and topic
                              |  |  |        +- government: Harris County
                              |  |  +- level: counties
                              |  +- state or province: Texas (ISO 3166-2 code)
                              +- country: United States (ISO 3166-1 code)
```

## Levels

| Folder | What goes there | Examples |
|---|---|---|
| `national` | the national government | `us/national`, `ca/national` |
| `state` | the state or provincial government itself | `us/tx/state`, `ca/on/state` |
| `counties` | county-equivalents: counties, parishes (Louisiana), boroughs and census areas (Alaska), regional municipalities | `us/tx/counties/harris`, `us/la/counties/orleans` |
| `cities` | municipalities of any kind: cities, towns, villages, townships | `us/tx/cities/houston`, `ca/on/cities/toronto` |
| `districts` | special-purpose governments: school, hospital, flood-control, port, transit, utility and emergency-services districts | `us/tx/districts/houston-isd`, `us/tx/districts/harris-health` |

A national government has no state segment (`us/national/...`). Countries without a state or provincial layer skip it (`sg/national/...`, `sg/cities/...`). Government slugs are short and lower case; where a city and a county share a name, the level folder keeps them apart (`us/tx/cities/houston` and `us/tx/counties/houston`).

## Each government has a page

`docs/<path>/index.md` describes the government (how it is governed, its fiscal year, where it publishes its budget) and lists the investigations under it. The facts table and the investigation list are generated from the registry; the prose below them is written by contributors.

## Each government has its own repository

A government's pages and evidence live in a repository of their own, named after the path with dashes: `govspends/us-tx-counties-harris`. That repository holds `jurisdiction.toml` (the government's entry: name, level, seat, fiscal year, official websites, and the list of its investigations), `docs/index.md` (its profile page) and, for each investigation, `docs/<investigation>/` and `investigations/<investigation>/`. Pull requests about a government go to its repository; the pencil icon on any of its pages opens the right one. The hub repository (`govspends/govspends`) holds the landing page, the country and state pages, the tools and `governments.toml`, the list of government repositories. When the hub builds the website it clones every government repository, places each one at its path, and produces one site with a single navigation and search; a merge in any government repository triggers that build.

## Each investigation has two folders with the same name

| | |
|---|---|
| `docs/<investigation>/` (in the government's repository; `docs/<path>/<investigation>/` on the website) | the report as web pages (one per section), the charts, and pages generated from the records: references, sources and files, audit summary, reviews, notes |
| `investigations/<investigation>/` (in the government's repository) | everything behind it: `sources/` (official documents), `data/` (parsed tables, metrics, text extractions), `scripts/`, `notes/`, `charts/`, `report/`, `REFERENCES.md`, `AUDIT_SUMMARY.md`, `MANIFEST_SHA256.txt`, and any independent review |

## The registries

`governments.toml` in the hub lists the hub-owned jurisdictions (countries, states and provinces: `[jurisdiction."<path>"]` with name and type) and the government repositories (`[[government]]` with path, repository and branch). Each government repository's `jurisdiction.toml` describes the government (path, repository, name, type, country, state, seat, governing body, fiscal year, websites) and its investigations (`[[investigation]]`: folder, title, status, headline, the PDF name, which scripts check the data, which script rebuilds the generated tables, short navigation titles). The hub's `tools/assemble.py` reads both, composes the site, and writes the navigation, the landing-page table and the generated block of every jurisdiction page.

## Adding one

1. **A government:** create its repository from the shape of an existing one, fill `jurisdiction.toml` and `docs/index.md`, and add a `[[government]]` entry to the hub's `governments.toml`. If its country or state is new, add `docs/<country>/index.md` or `docs/<country>/<state>/index.md` to the hub (a heading, the two `generated:jurisdiction` marker lines, and a paragraph).
2. **An investigation:** in the government's repository, add an `[[investigation]]` entry, create `docs/<name>/` with the report pages and `investigations/<name>/` with the evidence (the [contributing guide](../contributing.md) has the sourcing rule), and run `./tools.sh build_site`, `./tools.sh sync_docs` and, if the report has generated tables, `./tools.sh build_tables`.
3. Open a pull request in that repository. Its checks verify that the data reproduces and the generated pages are current; after the merge, the hub rebuilds the website.
