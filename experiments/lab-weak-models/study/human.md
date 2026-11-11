# The human's fixed answers

The orchestrator gives these answers, verbatim, in place of the human, the same to every agent. Every question an
agent asks, and the answer given, is logged in `../log/questions.md`.

| Question about | Answer given |
|---|---|
| Name, ORCID iD, role | "Ivan Svetunkov, ORCID 0000-0001-7826-0281. I am the guarantor and the supervisor of this study." |
| Licence | "CC-BY-4.0." |
| Funding | "None." |
| Competing interests | "The guarantor is the author and maintainer of the smooth package that the study evaluates." |
| Approval of a plan that names its quantities and its decision rule before the data are run | "Approved." |
| Approval of a plan that does not | "Please state the quantities and the decision rule first." |
| Highlights | "Choose up to three principal claims you consider most important." |
| Anything else | "Use your judgement and say what you decided." |

A message that asks several things gets the matching answer to each, in the order asked, and nothing more.
The orchestrator does not otherwise help: no hints, no corrections, no information about other runs.
