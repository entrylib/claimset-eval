# Answer key (reference analysis; never shown to the agents under test)

Made by `simulate.py` (the full design of `../study/brief.md`, R = 300, 110 s on 4 cores) and `optcheck.py`.
Software: smooth 1.2.0, statsforecast 2.1.1, numpy 2.5.4, Python 3.13. Seeds: `numpy.random.default_rng([20261111,
process index, T, replicate])`, the same series for every arm. Tables: `summary.csv` (bias, its Monte Carlo SE,
RMSE, MAE, mean and median estimate, errors, bound hits per process × T × arm × parameter), `consistency.csv`,
`optcheck.csv`; every fit in `estimates.csv`.

Arms:
- **smooth-opt**: `ES(model=…, lags=[12] for ETS(A,N,A), initial="optimal")`, otherwise defaults (loss
  `likelihood`, bounds `usual`).
- **sf**: `AutoETS(model=…, season_length=12 or 1, damped=False)`, otherwise defaults (`opt_crit="lik"`,
  bounds `both`).
- **smooth-bc**: `ES(model=…)` with its default `initial="backcasting"`.

"On a bound": within 0.001 of a bound of the implementation's own region (given the other estimates).

**How claims are checked against this key.** An agent's study uses its own seeds, so its numbers differ from
these by Monte Carlo error. A claim is *correct* when its direction and its magnitude agree with the key within
about three Monte Carlo standard errors (bias SE as given; RMSE and MAE within about 10 % relative), *partly
correct* when the direction agrees but the magnitude, the scope (which T, which arm, which parameter) or a
qualifier does not, and *wrong* when the direction or the conclusion disagrees. A claim can be right about the
agent's own record and still wrong against the key (a design error in the record); both are scored.

## K0. Comparability (what a correct paper must state)

- **K0.1 Parametrisation.** Both implement the same innovations form, y_t = l_{t−1} (+ b_{t−1}) (+ s_{t−m}) + ε_t,
  l_t = l_{t−1} (+ b_{t−1}) + α ε_t, b_t = b_{t−1} + β ε_t, s_t = s_{t−m} + γ ε_t: α, β and γ mean the same in both
  and in the brief's data generating process. No conversion is needed. (A paper that converts β to β* = β/α, as
  in the Holt "error-correction" form, is wrong for these packages.)
- **K0.2 Loss.** smooth's default `loss="likelihood"` and statsforecast's default `opt_crit="lik"` both maximise the
  Gaussian likelihood with σ concentrated out, which for additive errors has the same optimum as the MSE of the
  one-step errors. Same criterion.
- **K0.3 Initial states.** smooth `initial="optimal"` and statsforecast both estimate the initial states with the
  smoothing parameters; smooth's default `initial="backcasting"` does not, and is a separate arm.
- **K0.4 Bounds.** smooth `bounds="usual"`: α, β, γ ∈ [0, 1], β ≤ α, γ ≤ 1 − α. statsforecast `bounds="both"`:
  α, β, γ ∈ [0.0001, 0.9999], β ≤ α, γ ≤ 1 − α, and also the admissible (forecastability) region. The regions
  differ slightly (closed vs. 0.0001 margins; statsforecast adds admissibility).
- **K0.5 Fixed form in statsforecast.** For ETS(A,A,N), `AutoETS(model="AAN")` without `damped=False` selects
  between damped and undamped trend (on the reference's first 40 series of ETS(A,A,N), α = 0.5, β = 0.2, T = 50,
  it chose ETS(A,Ad,N) for 6). A study that leaves `damped` unset is doing model selection, against the brief.
- **K0.6 Optimisers.** Both use Nelder–Mead (smooth: NLopt `NLOPT_LN_NELDERMEAD`; statsforecast: its own).
  statsforecast exposes the iteration count (`model_["fit"].nit`); smooth's Python API does not expose a
  convergence flag.

## K1. Failures

- **K1.1** No arm raised an error in any of the 6,000 series × 3 arms.
- **K1.2 statsforecast does not converge for ETS(A,N,A).** Its optimiser stopped at its iteration cap
  (`nit` = 1001) in 288, 296, 300 and 299 of 300 fits at T = 50, 100, 250, 500. It never reached the cap for
  ETS(A,N,N) (median 27 iterations) or ETS(A,A,N) (at most 324).
- **K1.3 Estimates on a bound are frequent at small T.** Of 300 fits at T = 50 (lower / upper bound):

  | Process | Parameter | smooth-opt | sf | smooth-bc |
  |---|---|---|---|---|
  | ETS(A,N,N) α = 0.1 | α | 187 / 0 | 189 / 0 | 203 / 0 |
  | ETS(A,N,N) α = 0.5 | α | 6 / 0 | 6 / 1 | 6 / 1 |
  | ETS(A,A,N) (0.3, 0.05) | α | 19 / 0 | 134 / 0 | 53 / 0 |
  | ETS(A,A,N) (0.3, 0.05) | β | 72 / 119 | 115 / 94 | 118 / 69 |
  | ETS(A,A,N) (0.5, 0.2) | α | 0 / 0 | 10 / 7 | 0 / 0 |
  | ETS(A,A,N) (0.5, 0.2) | β | 26 / 34 | 84 / 11 | 28 / 47 |
  | ETS(A,N,A) (0.2, 0.1) | α | 19 / 0 | 26 / 0 | 52 / 0 |
  | ETS(A,N,A) (0.2, 0.1) | γ | 129 / 0 | 136 / 0 | 265 / 3 |

  β's upper bound is β = α. Bound hits fall with T (ETS(A,N,N) α = 0.1: 92 / 93 / 108 at T = 100, 1 / 1 / 1 at
  T = 500), except γ in ETS(A,N,A) (K5).

## K2. ETS(A,N,N)

- **K2.1** α = 0.1: every arm underestimates α at small T, and the bias shrinks with T. Bias (Monte Carlo SE
  0.005 at T = 50, 0.001 at T = 500): smooth-opt −0.047, sf −0.048, smooth-bc −0.052 at T = 50; −0.028, −0.028,
  −0.031 at T = 100; −0.009, −0.009, −0.010 at T = 250; −0.0045 for all three at T = 500. The median estimate at
  T = 50 is 0 (smooth) / 0.0001 (sf): most estimates are on the lower bound.
- **K2.2** α = 0.5: small negative bias at T = 50 (−0.025, SE 0.009, all arms), not distinguishable from zero at
  T ≥ 250 (−0.003, SE 0.003).
- **K2.3** smooth-opt and sf are practically identical for ETS(A,N,N): RMSE equal to within 0.001 in every cell
  (α = 0.1: 0.092, 0.064, 0.031, 0.021; α = 0.5: 0.160, 0.093, 0.055, 0.037 for T = 50, 100, 250, 500).
- **K2.4** smooth-bc is slightly less efficient than the optimised arms for α = 0.1 at small T (RMSE 0.094 vs
  0.092 at T = 50; 0.068 vs 0.064 at T = 100; 0.033 vs 0.031 at T = 250) and equal at T = 500; for α = 0.5 equal
  everywhere.

## K3. ETS(A,A,N), (α, β) = (0.3, 0.05)

- **K3.1** α is strongly underestimated at T = 50 by every arm (bias −0.129 smooth-opt, −0.138 sf, −0.132
  smooth-bc; SE ≈ 0.009), less at T = 100 (≈ −0.053), and the bias is small by T = 500 (−0.002, SE 0.002).
- **K3.2** β is underestimated at T = 50 (−0.010 smooth-opt, −0.017 sf, −0.013 smooth-bc; SE 0.002), ≈ −0.001 at
  T = 500 for all arms.
- **K3.3** smooth-opt is somewhat more efficient than sf for α at small T (RMSE 0.198 vs 0.217 at T = 50;
  0.108 vs 0.116 at T = 100); the arms are equal at T ≥ 250 (0.051, 0.033). For β the RMSEs are close at every T
  (0.036 / 0.039 / 0.039 at T = 50; 0.008 at T = 500).

## K4. ETS(A,A,N), (α, β) = (0.5, 0.2)

- **K4.1** The packages are biased in opposite directions for α at small T: smooth-opt −0.047 (SE 0.009) and
  sf +0.024 (SE 0.012) at T = 50; −0.018 vs +0.017 at T = 100; at T = 500, −0.005 (SE 0.002) vs 0.000 (SE 0.002).
- **K4.2** sf underestimates β at every T, and much more than smooth: bias −0.081 (sf) vs −0.021 (smooth-opt) at
  T = 50; −0.031 vs −0.002 at T = 100; −0.014 vs −0.004 at T = 250; −0.0088 (SE 0.0007) vs −0.0008 (SE 0.0012) at
  T = 500. sf's median β is close to 0.2 from T = 100 (0.194, 0.195, 0.198): its bias comes from a minority of
  fits with β near its lower bound (84 of 300 at T = 50, 16 at T = 100).
- **K4.3** Efficiency is mixed: sf has the larger RMSE for α at T = 50 and 100 (0.207 vs 0.161; 0.137 vs 0.107),
  similar at T = 500 (0.039 vs 0.040); for β sf has the larger RMSE at T = 50 and 100 (0.117 vs 0.094; 0.059 vs
  0.055) but the smaller at T = 250 and 500 (0.023 vs 0.031; 0.015 vs 0.021), and the smaller MAE from T = 100.
- **K4.4** sf's fits fall short of the optimum of its own criterion: at T = 500, 72 of 300 sf fits have an SSE
  (with least-squares initial states at its estimated α, β) more than 0.1 % above the best of the three arms on
  the same series; smooth-opt 0, smooth-bc 0 (`optcheck.csv`).
- **K4.5** smooth-bc and smooth-opt are practically identical for this process (RMSEs within 0.002).

## K5. ETS(A,N,A), m = 12, (α, γ) = (0.2, 0.1)

- **K5.1** γ is severely underestimated by smooth in both arms, at every T, with no sign of consistency over
  T = 50…500. smooth-opt: bias −0.096, −0.098, −0.095, −0.061 (T = 50, 100, 250, 500); median estimate ≤ 0.003 at
  every T; 129, 158, 183, 121 of 300 on the lower bound; RMSE 0.096, 0.098, 0.098, 0.075. smooth-bc: bias −0.089,
  −0.100, −0.099, −0.094; 265, 300, 299, 284 of 300 on the lower bound; RMSE 0.117, 0.100, 0.100, 0.097.
- **K5.2** sf's γ bias shrinks with T: −0.092, −0.081, −0.059, −0.013 (SE 0.003 at T = 500); RMSE 0.095, 0.091,
  0.086, 0.050; on the lower bound 136, 81, 66, 17 of 300.
- **K5.3** For α the order is reversed: smooth-bc is nearly unbiased (−0.004, +0.006, +0.006, +0.004) and
  smooth-opt slightly negative (−0.021, −0.012, −0.012, −0.005), while sf underestimates α at every T and its
  bias stops shrinking: −0.113, −0.066, −0.038, −0.040 (SE 0.002 at T = 500); sf's α RMSE is 0.051 at T = 250 and
  0.050 at T = 500 (smooth-opt 0.035, 0.029; smooth-bc 0.035, 0.028).
- **K5.4** The pile-up of γ at zero is a property of the estimation problem, not a defect of smooth: with initial
  states by least squares, the sum of squared one-step errors is lowest at γ ≈ 0 for most of these series (on a
  grid over α and γ, 3 of the first 4 series at T = 500 have their minimum at γ = 0). sf's estimates have the
  highest SSE of the three arms on the same series (mean excess over the best arm 6.3 %, 4.8 %, 3.5 %, 2.7 % at
  T = 50…500; more than 0.1 % above the best in 210–285 of 300 fits), consistent with K1.2: sf's γ is closer to
  the truth because its optimiser stops early, not because it estimates better.
- **K5.5** Consequently, a correct paper does not say that statsforecast is the better estimator of γ without
  qualifying it by its non-convergence; and it does not say that smooth's γ estimator is inconsistent in general:
  over T ≤ 500 its RMSE does not fall (smooth-opt 0.096 → 0.075, smooth-bc 0.117 → 0.097).

## K6. Consistency

- **K6.1** For ETS(A,N,N) and ETS(A,A,N), the RMSE of every parameter falls monotonically with T in every arm;
  the log–log slopes of RMSE on T are −0.62 to −0.91 (`consistency.csv`), faster than T^(−1/2) over this range
  because the small-T estimates are bounded. RMSE at T = 500 is 0.13–0.25 of that at T = 50.
- **K6.2** For ETS(A,N,A): α consistent for smooth (RMSE 0.105 → 0.029 smooth-opt, 0.139 → 0.028 smooth-bc) but
  flattening for sf (0.143, 0.092, 0.051, 0.050); γ not consistent over this range for smooth (slopes −0.10 and
  −0.07), slowly falling for sf (slope −0.25).

## K7. Overall statements a correct paper may make

- **K7.1** Where the two implementations solve the same problem and converge (ETS(A,N,N), ETS(A,A,N) with
  α = 0.3, β = 0.05), their estimates are practically the same; differences are within Monte Carlo error at
  T ≥ 250.
- **K7.2** Neither implementation is uniformly better: smooth-opt is more efficient for α in ETS(A,A,N) at small T
  and for α in ETS(A,N,A); sf is more efficient for β in ETS(A,A,N) (0.5, 0.2) at T ≥ 250 and less biased for γ
  in ETS(A,N,A), the latter with non-converged fits.
- **K7.3** Backcasting (smooth's default) is close to optimised initial states for ETS(A,N,N) and ETS(A,A,N), the
  least biased arm for α in ETS(A,N,A), and the most biased for γ there.
- **K7.4** Small-sample bias towards zero (or towards the lower bound) of the smoothing parameters is shared by
  all arms; it is the dominant feature at T = 50.

## Declarations a correct paper must carry

The guarantor (Ivan Svetunkov) is the author and maintainer of smooth: a competing interest, declared. Licence
CC-BY-4.0; funding none.
