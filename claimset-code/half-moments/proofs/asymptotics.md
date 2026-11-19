# Asymptotic normality of the sample coefficients (hypothesis H18)

Study `half-moments`, plan PL5. Notation and influence functions as in `properties.md` (H17).

*Statement.* Let $y_1, \ldots, y_n$ be independent with distribution $F$, which has a finite fourth moment, variance
$\sigma^2 > 0$, and a density bounded and continuous on a neighbourhood $(\mu_1 - \eta, \mu_1 + \eta)$ of its mean. Let
$\bar y$ be the sample mean, $\hat R = \frac{1}{n}\sum_j (y_j - \bar y)_+^{0.5}$, $\hat I = \frac{1}{n}\sum_j (\bar y - y_j)_+^{0.5}$,
$\hat\sigma^2 = \frac{1}{n}\sum_j (y_j - \bar y)^2$, and $\hat T$ the sample Asymmetry, Hypotailedness or Extremity computed from
them. Then $\sqrt{n}(\hat T - T) \to N(0, \mathrm{E}[\mathrm{IF}_T(y)^2])$, with $\mathrm{IF}_T$ the influence function of H17.

*Proof.*

**Step 1 (the parts with an estimated mean).** Let $f_t(y) = (y - t)_+^{0.5}$, $M_n(t) = \frac{1}{n}\sum_j f_t(y_j)$,
$m_+(t) = \mathrm{E} f_t(y)$ and $\mathbb{G}_n(t) = \sqrt{n}(M_n(t) - m_+(t))$. Then $\hat R = M_n(\bar y)$ and
$$\sqrt{n}(\hat R - R) = \mathbb{G}_n(\bar y) + \sqrt{n}\,(m_+(\bar y) - m_+(\mu_1)).$$

*(a) The empirical-process term.* For $t_1 < t_2$ and every $y$, $f_{t_2}(y) \le f_t(y) \le f_{t_1}(y)$ for $t \in [t_1, t_2]$
(monotone in $t$), and, since $|\sqrt{u} - \sqrt{v}|^2 \le |u - v|$ for $u, v \ge 0$ and $|(y - t_1)_+ - (y - t_2)_+| \le t_2 - t_1$,
$\mathrm{E}[(f_{t_1} - f_{t_2})^2] \le t_2 - t_1$. So the class $\{f_t : |t - \mu_1| \le 1\}$ has $L_2(F)$ bracketing numbers
$N_{[\,]}(\varepsilon) \le 2/\varepsilon^2 + 1$ and an envelope $(|y| + |\mu_1| + 1)^{0.5}$ with finite second moment. Its
bracketing integral is finite, so it is $F$-Donsker (van der Vaart 1998, *Asymptotic Statistics*, Theorem 19.5), and
the empirical process is asymptotically equicontinuous in the $L_2(F)$ semimetric $\rho(s, t) \le |s - t|^{0.5}$.
Since $\bar y \to \mu_1$ almost surely, $\rho(\bar y, \mu_1) \to 0$ in probability and $\mathbb{G}_n(\bar y) - \mathbb{G}_n(\mu_1) \to 0$ in
probability (van der Vaart 1998, Lemma 19.24).

*(b) The drift term.* $m_+$ is differentiable at $\mu_1$ with $m_+'(\mu_1) = -a_+/2$ (proof of H17), and
$\sqrt{n}(\bar y - \mu_1) = O_P(1)$ (central limit theorem), so $\sqrt{n}(m_+(\bar y) - m_+(\mu_1)) = -\frac{a_+}{2}\sqrt{n}(\bar y - \mu_1) + o_P(1)$.

Together,
$$\sqrt{n}(\hat R - R) = \frac{1}{\sqrt{n}}\sum_{j=1}^n \left[(y_j - \mu_1)_+^{0.5} - R - \frac{a_+}{2}(y_j - \mu_1)\right] + o_P(1) = \frac{1}{\sqrt{n}}\sum_{j=1}^n \mathrm{IF}_R(y_j) + o_P(1).$$
The same argument with $(t - y)_+^{0.5}$ gives $\sqrt{n}(\hat I - I) = n^{-1/2}\sum_j \mathrm{IF}_I(y_j) + o_P(1)$. This is the
situation of Randles (1982): the estimated mean changes the limit through the derivative $m_\pm'(\mu_1)$, which is not zero.

**Step 2 (the variance).** $\hat\sigma^2 = \frac{1}{n}\sum_j (y_j - \mu_1)^2 - (\bar y - \mu_1)^2$ and $\sqrt{n}(\bar y - \mu_1)^2 = o_P(1)$, so
$\sqrt{n}(\hat\sigma^2 - \sigma^2) = n^{-1/2}\sum_j [(y_j - \mu_1)^2 - \sigma^2] + o_P(1) = n^{-1/2}\sum_j \mathrm{IF}_{\sigma^2}(y_j) + o_P(1)$.

**Step 3 (joint limit).** The vector $(\mathrm{IF}_R, \mathrm{IF}_I, \mathrm{IF}_{\sigma^2})(y)$ has mean zero (each is a centred
function: $\mathrm{E}[(y-\mu_1)_+^{0.5}] = R$, $\mathrm{E}[y - \mu_1] = 0$) and finite covariance: $\mathrm{IF}_R$ and $\mathrm{IF}_I$ are
bounded by $C(1 + |y|)$, square-integrable as the variance is finite, and $\mathrm{IF}_{\sigma^2}$ is square-integrable by the finite
fourth moment. By the multivariate central limit theorem and Slutsky's lemma,
$\sqrt{n}(\hat R - R, \hat I - I, \hat\sigma^2 - \sigma^2) \to N(0, \Sigma)$ with $\Sigma = \mathrm{Cov}(\mathrm{IF}_R, \mathrm{IF}_I, \mathrm{IF}_{\sigma^2})$.

**Step 4 (delta method).** $A = \frac{4}{\pi}\arctan\frac{R - I}{R + I}$, $H = (R + I)(\sigma^2)^{-1/4}$ and $E = 2H^p - 1$ are
continuously differentiable at $(R, I, \sigma^2)$ with $R, I, \sigma^2 > 0$ (Lemma 0 of `properties.md`). The delta method
gives $\sqrt{n}(\hat T - T) \to N(0, \nabla T^\top \Sigma\,\nabla T)$, and $\nabla T^\top(\mathrm{IF}_R, \mathrm{IF}_I, \mathrm{IF}_{\sigma^2})$
is exactly the chain-rule combination that defines $\mathrm{IF}_T$ in H17; as it has mean zero, its variance is
$\mathrm{E}[\mathrm{IF}_T(y)^2]$. ∎

*Remarks.*
1. For the half absolute moment the drift is $-\frac{a_+ - a_-}{2}(\bar y - \mu_1)$, which vanishes when $a_+ = a_-$ (for example for a distribution symmetric about its mean): then estimating the mean does not change its limiting variance.
2. A plug-in standard error needs $a_\pm = \mathrm{E}[|D|^{-0.5}\mathbf{1}(\pm D > 0)]$, whose sample analogue has infinite variance when the density at the mean is positive. This is why plan PL6 evaluates jackknife and bootstrap intervals rather than the plug-in interval.
3. Asymmetry alone needs only a finite variance (its influence function is $O(|y|)$); the fourth moment is needed for Hypotailedness and Extremity, through $\hat\sigma^2$.
