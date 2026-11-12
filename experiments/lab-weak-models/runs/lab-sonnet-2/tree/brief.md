# Study brief: how well do smooth and statsforecast estimate ETS parameters?

## Question

Compare how well two Python implementations of exponential smoothing (ETS) estimate the parameters of the
model that generated the data:

- `smooth` (Python package, function/class `ES`, the `es()` of the R package), by Ivan Svetunkov;
- `statsforecast` (Nixtla), `AutoETS` (or its `ets` functions) with a fixed model form.

The comparison is on simulated data, by three properties of the estimates of the smoothing parameters
(α, β, γ):

- **bias**: the mean of (estimate − true value);
- **efficiency**: the RMSE and the MAE of the estimates around the true value;
- **consistency**: whether the RMSE falls towards zero as the series length grows.

Fixed model forms only (the form that generated the data): no model selection.

## Design

Data generating processes: ETS in its innovations (single source of error) form with additive Gaussian errors,
σ = 1:

| Process | Parameters |
|---|---|
| ETS(A,N,N) | α = 0.1; α = 0.5 |
| ETS(A,A,N) | (α, β) = (0.3, 0.05); (α, β) = (0.5, 0.2) |
| ETS(A,N,A), period m = 12 | (α, γ) = (0.2, 0.1) |

The equations, with ε_t ~ N(0, 1) independent:

- ETS(A,N,N): y_t = l_{t−1} + ε_t; l_t = l_{t−1} + α ε_t
- ETS(A,A,N): y_t = l_{t−1} + b_{t−1} + ε_t; l_t = l_{t−1} + b_{t−1} + α ε_t; b_t = b_{t−1} + β ε_t
- ETS(A,N,A): y_t = l_{t−1} + s_{t−m} + ε_t; l_t = l_{t−1} + α ε_t; s_t = s_{t−m} + γ ε_t

Initial states: level l_0 = 100; trend b_0 = 1; seasonal indices s_j = 10·sin(2πj/12) for j = 0, …, 11, where
s_0 is the index of the first observation's season (they sum to zero). No burn-in: each series starts from
these states.

Series lengths T ∈ {50, 100, 250, 500}; R = 300 replicates per cell (process × parameters × T). If a full run
would take more than 20 minutes of computing, lower R to 200 and record that you did. Fix every seed and record
it.

## Making the implementations comparable

Before any comparison, establish and state, per setting, how the two implementations are made comparable:

- what α, β and γ mean in each (the same parametrisation, or a conversion between them);
- how the initial states are obtained. smooth's default is backcasting; statsforecast optimises them. Compare
  both with optimised initial states, and report smooth's default (backcasting) as a separate arm;
- the loss each minimises (likelihood or MSE);
- the parameter bounds each uses.

Failures (errors, non-convergence, estimates on a bound) are counted and reported, never dropped silently.

## People and declarations

The guarantor of the study is Ivan Svetunkov, who is the author of `smooth`: a competing interest to declare.

## Practicalities

- The Python environment with `smooth`, `statsforecast` and `claimset` installed: `source /home/user/venv/bin/activate`.
- Your folder is a git repository with a remote `origin` (a local repository). Push only there.
- Do not submit, publish or send anything to EntryLib or any other service.
