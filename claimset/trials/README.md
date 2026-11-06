# Field trials (specification 0.38, core only)

Seven open-access papers, one per kind of work, converted to claimsets that use the core of specification 0.38 and no extension. They were made to find what the core cannot hold, not as reference conversions: unlike `claimset/pilot/`, no author took part, and the converter worked from the published text without a local copy.

| Paper | Kind of work |
|---|---|
| `doi-10-1016-j-physletb-2012-08-020` | particle physics (ATLAS Higgs observation, 2012) |
| `doi-10-1371-journal-pone-0185809` | field ecology (flying-insect biomass decline, 2017) |
| `doi-10-1186-s12916-017-0791-y` | randomised controlled trial (SMILES, 2017) |
| `doi-10-1098-rsos-181351` | preregistered behavioural experiment (2020) |
| `doi-10-1038-srep31707` | wet-lab cell biology (adhesome siRNA screen, 2016) |
| `doi-10-1039-d0sc01471k` | synthetic chemistry (photoredox/nickel cascade, 2020) |
| `doi-10-1017-mdh-2023-14` | history from archival sources (segmented sleep, 2023) |

For each paper:

- `<name>.claimset.json`: the claimset; valid under 0.38 with 0 errors. `<name>.claimset.txt` is its reading view (`claimset render`).
- `<name>.friction.json`: what did not fit, as a list of `{where, what, need, proposal}`; `proposal` says whether the need belongs in the core, in an extension, or nowhere.

Differences from the pilot set:

- `source_spans` name sections, figures and tables of the published paper (`"Results"`, `"Fig 6"`), not `[pN.M]` markers: the papers' texts are not in `papers/text/`. `tools/compare.py` therefore cannot compare source spans for these files.
- The claims are the converter's reading, checked against the paper but not by its authors. Use them to study the format, not as gold conversions.
- Some decisions are forced by the core (a cell line recorded as a `population`, a compound as `other`, preregistered tests left out because only a lab record can hold them); each one is in the friction file.
