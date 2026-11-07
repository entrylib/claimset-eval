# Field trials (core only)

Seven open-access papers, one per kind of work, converted to claimsets that use the core of the specification and no extension: first under 0.38, then again under 0.39, which added core forms for the gaps the first round found. They were made to find what the core cannot hold, not as reference conversions: unlike `claimset/pilot/`, no author took part, and the converter worked from the published text without a local copy.

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

- `<name>.claimset.json`: the claimset, converted again under 0.39; valid with 0 errors. `<name>.claimset.txt` is its reading view (`claimset render`).
- `<name>.friction.json`: what did not fit, as a list of `{where, what, need, proposal, v0.39}`. `proposal` says whether the need belongs in the core, in an extension, or nowhere. `v0.39` says what happened in the second round: `resolved` or `partly resolved` (and how), `extension` (left to an extension), `open` (a core gap that remains), `none` (nothing needed), or `new` (found in the second round).

Differences from the pilot set:

- `source_spans` name sections, figures and tables of the published paper (`"Results"`, `"Fig 6"`), not `[pN.M]` markers: the papers' texts are not in `papers/text/`. `tools/compare.py` therefore cannot compare source spans for these files.
- The claims are the converter's reading, checked against the paper but not by its authors. Use them to study the format, not as gold conversions.
- Some decisions are still forced by the core; each is in the friction file.

## Results of the second round (0.39)

Of the 63 points of friction from the first round, 24 are resolved and 6 partly resolved by 0.39, 19 are left to extensions, 11 needed nothing and 3 remain open in the core. The second round found 8 more. One of them, a registered test whose registration date is not at hand, was fixed by revising rule 43: the preregistered study's confirmatory tests are now recorded, without the date, which neither the paper nor the registry gave.

Open in the core:

- typed statistics (effect-size kinds), still free text in `conditions`;
- approximate values ("about 1.5-fold");
- an intervention's target (a knockdown and the gene it knocks down);
- processes as a kind (decay channels, reactions);
- units on condition values;
- guidance: trial registries' CURIE prefixes, and whether `se` covers a posterior SD.
