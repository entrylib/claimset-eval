# Properties of the half central moment and its coefficients (hypotheses H1–H9, H17)

Study `half-moments`, plan PL1. Proofs written by the research agent (AC1) for checking by an independent agent.

## Notation

$y$ is a real random variable with distribution $F$ and finite mean $\mu_1$; $D = y - \mu_1$; $x_+ = \max(x, 0)$,
$x_- = \max(-x, 0)$. The square root of a real number $x$ is the principal root: $x^{0.5} = \sqrt{x}$ for $x \ge 0$ and
$x^{0.5} = i\sqrt{|x|}$ for $x < 0$. Hence, for every real $x$,
$$x^{0.5} = x_+^{0.5} + i\,x_-^{0.5}. \tag{N1}$$

- Half central moment: $\mu_{0.5} = \mathrm{E}[D^{0.5}] = R + iI$ with $R = \mathrm{E}[D_+^{0.5}]$ and $I = \mathrm{E}[D_-^{0.5}]$ (by N1 and linearity of expectation). Both are finite: $\mathrm{E}|D|^{0.5} \le (\mathrm{E}|D|)^{0.5} < \infty$ by Jensen's inequality, and $R, I \ge 0$.
- Half absolute moment: $\nu = \nu_{0.5} = R + I = \mathrm{E}|D|^{0.5}$.
- Angle: $\phi = \mathrm{Arg}(\mu_{0.5}) \in [0, \pi/2]$ (defined when $\nu > 0$).
- Asymmetry: $A = 1 - \phi/(\pi/4)$.
- Hypotailedness: $H = \nu / \sigma^{0.5}$, $\sigma^2 = \mathrm{E}[D^2] \in (0, \infty)$.
- Extremity: $E = 2H^{p} - 1$ with $p = \log 0.5 / \log h_U$, $h_U = 2 \times 3^{-0.75} \approx 0.8774$, so $p \approx 5.299$.
- One-sided Hypotailedness: $H_\pm = \mathrm{E}[|D|^{0.5} \mid \pm D > 0] / (\mathrm{E}[D^2 \mid \pm D > 0])^{0.25}$.
- Complex Extremity: $\mathrm{CE} = (2H_+^{p} - 1) + i(2H_-^{p} - 1)$.
- $p_\pm = P(\pm D > 0)$; $\delta = \mathrm{E}[D_+]$.

**Lemma 0 (balance of the mean).** $\mathrm{E}[D_+] = \mathrm{E}[D_-] = \delta$, and if $y$ is not constant then $\delta > 0$, $p_+ > 0$ and $p_- > 0$.

*Proof.* $0 = \mathrm{E}[D] = \mathrm{E}[D_+] - \mathrm{E}[D_-]$. If $y$ is not constant, $P(D \ne 0) > 0$, so $\mathrm{E}|D| = 2\delta > 0$; then $\mathrm{E}[D_+] = \delta > 0$ forces $p_+ > 0$, and likewise $p_- > 0$. ∎

**Lemma J (Jensen, strict).** For a non-negative random variable $Z$ with $\mathrm{E}[Z] < \infty$ and $0 < r < 1$: $\mathrm{E}[Z^r] \le (\mathrm{E}[Z])^r$, with equality if and only if $Z$ is constant with probability one. (Strict concavity of $z \mapsto z^r$ on $[0, \infty)$.)

## H1. Symmetry gives equal parts

*Statement.* If $y$ has a finite mean and a distribution symmetric about it, then $R = I$.

*Proof.* Symmetry about $\mu_1$ means $D$ and $-D$ have the same distribution. Then $R = \mathrm{E}[D_+^{0.5}] = \mathrm{E}[(-D)_+^{0.5}] = \mathrm{E}[D_-^{0.5}] = I$. ∎

*Remark (on the manuscript's proof).* The manuscript argues from $\int_{-\infty}^{\mu_1} f = \int_{\mu_1}^{\infty} f$. Equal probability on the two sides does not make the two integrals of $|y - \mu_1|^{0.5}$ equal; what is needed is the equality in distribution of $D$ and $-D$ used above (for a density, $f(\mu_1 + x) = f(\mu_1 - x)$ and the substitution $y = \mu_1 \mp x$).

## H2. The converse is false

*Statement.* Some distributions with a finite mean have $R = I$ and are not symmetric about their mean.

*Proof.* For $x > \delta_0 > 0$ let $g(x) = \mathrm{E}|U|^{0.5}$ for $U$ uniform on $[x - \delta_0, x + \delta_0]$:
$$g(x) = \frac{(x + \delta_0)^{1.5} - (x - \delta_0)^{1.5}}{3\delta_0}.$$
Fix $b \in (0, 1)$, $c = 1/b$ and $\delta_0 = b(1-b)/2$. Then $\delta_0 < b$, $b + \delta_0 < 1$ and $c - \delta_0 > 1$, so the intervals $J_1 = [-1 - \delta_0, -1 + \delta_0]$, $J_2 = [b - \delta_0, b + \delta_0]$, $J_3 = [c - \delta_0, c + \delta_0]$ are disjoint, $J_1 \subset (-\infty, 0)$, $J_2, J_3 \subset (0, \infty)$, and $1 \notin J_2 \cup J_3$.

Let $y$ have the density that is uniform on $J_1, J_2, J_3$ with masses $w_1, w_2, w_3 > 0$ ($w_1 + w_2 + w_3 = 1$), chosen so that

(i) $\mathrm{E}[y] = 0$: $-w_1 + w_2 b + w_3 c = 0$;
(ii) $R = I$: $w_1 g(1) = w_2 g(b) + w_3 g(c)$.

Substituting $w_1 = w_2 b + w_3 c$ from (i) into (ii) and using $g(1)$, (ii) becomes $(w_2 b + w_3 c)\,g(1) = w_2 g(b) + w_3 g(c)$, i.e. $w_2\,(g(b) - b\,g(1)) = w_3\,(c\,g(1) - g(c))$.

- $g(1) \le 1$ by Lemma J ($\mathrm{E}|U|^{0.5} \le (\mathrm{E}|U|)^{0.5} = 1$ for $U$ uniform on $J_1$ reflected; on $J_1$ all values are negative, $|U|$ has mean 1).
- $g(b) \ge (b - \delta_0)^{0.5} > b$, because every point of $J_2$ is at least $b - \delta_0$, and $b - \delta_0 = b(1+b)/2 > b^2$ for $b < 1$.
- $g(c) \le (c)^{0.5} < c$ by Lemma J and $c > 1$.

Hence $g(b) - b\,g(1) \ge g(b) - b > 0$, and $c\,g(1) - g(c)$: since $g(1) \ge (1 - \delta_0)^{0.5}$ and $c(1-\delta_0)^{0.5} \ge c^{0.5}$ iff $c(1 - \delta_0) \ge 1$, which holds because $c(1 - \delta_0) = (1 - \delta_0)/b > 1$ (as $\delta_0 < 1 - b$), we get $c\,g(1) \ge c(1-\delta_0)^{0.5} \ge c^{0.5} \ge g(c)$, with strict inequality in the first step, so $c\,g(1) - g(c) > 0$. Therefore $w_3/w_2 = (g(b) - b g(1))/(c g(1) - g(c)) > 0$, $w_1 = w_2 b + w_3 c > 0$, and normalising gives positive masses satisfying (i) and (ii). The mean is 0, so by (N1) $R = w_2 g(b) + w_3 g(c)$ and $I = w_1 g(1)$, equal by (ii).

The distribution is not symmetric about 0: its density is positive on $J_1 \ni -1$ but zero at $+1$, since $1 \notin J_2 \cup J_3$ and $1 \ne$ any point of $J_1$. ∎

(The three-point distribution of run RN1, masses $0.45, 5/12, 2/15$ at $-1, 0.36, 2.25$, is the limit $\delta_0 \to 0$ of the same construction with $c \neq 1/b$; it has mean 0, $R = I = 0.45$ and skewness 0.85.)

## H3. Location, scale and sign

*Statement.* The half central moment is unchanged by adding a constant; multiplying $y$ by $c > 0$ multiplies it by $c^{0.5}$; multiplying by $c < 0$ multiplies it by $|c|^{0.5}$ and exchanges its real and imaginary parts.

*Proof.* Adding $a$ to $y$ adds $a$ to $\mu_1$ and leaves $D$ unchanged. Multiplying by $c$ multiplies the mean by $c$, so $D$ becomes $cD$. For $c > 0$: $(cD)_\pm = c\,D_\pm$, so $R$ and $I$ are multiplied by $c^{0.5}$. For $c < 0$: $(cD)_+ = |c|\,D_-$ and $(cD)_- = |c|\,D_+$, so the new real part is $|c|^{0.5} I$ and the new imaginary part $|c|^{0.5} R$. The same holds for the sample estimate with the sample mean in place of $\mu_1$ (the sample mean is equivariant in the same way). ∎

## H4. Range and sign of Asymmetry

*Statement* (as reworded after the first verdict; the first version stated $[-1, 1]$). For $y$ with a finite mean that is not constant, $A \in (-1, 1)$; $A = 0$ when $R = I$; $A < 0$ exactly when $I > R$.

*Proof.* By Lemma 0, $p_\pm > 0$, so $R = \mathrm{E}[D_+^{0.5}] > 0$ and $I > 0$; $\nu > 0$ and $\phi = \arctan(I/R) \in (0, \pi/2)$. For $t = I/R > 0$, $\arctan 1 - \arctan t = \arctan\frac{1 - t}{1 + t}$ (the subtraction formula, valid as $1 \cdot t > -1$), so
$$A = \frac{4}{\pi}\left(\arctan 1 - \arctan\frac{I}{R}\right) = \frac{4}{\pi}\arctan\frac{R - I}{R + I} = \frac{4}{\pi}\arctan\frac{R - I}{\nu}. \tag{A}$$
Since $|R - I| < R + I$ (both positive), the argument lies in $(-1, 1)$ and $\arctan$ maps it into $(-\pi/4, \pi/4)$; hence $A \in (-1, 1)$. $\arctan$ is odd and increasing, so $A = 0$ iff $R = I$ and $A < 0$ iff $I > R$. ∎

*Remark.* The bounds $\pm 1$ are not attained by any non-constant distribution with a finite mean: $A = \pm 1$ would need $I = 0$ or $R = 0$, i.e. no probability on one side of the mean, which Lemma 0 excludes. The manuscript's "the boundary values are only possible if the centre is set at the maximum or minimum" agrees: they need a centre other than the mean.

## H5. What Asymmetry measures

*Statement.* For $y$ with a finite mean and $p_\pm > 0$, let $h_\pm = \mathrm{E}[|D|^{0.5} \mid \pm D > 0] / (\mathrm{E}[|D| \mid \pm D > 0])^{0.5}$. Then $h_\pm \in (0, 1]$, each equal to 1 exactly when $|D|$ is constant on its side, and
$$\frac{R}{I} = \left(\frac{p_+}{p_-}\right)^{0.5}\frac{h_+}{h_-}.$$

*Proof.* Conditionally on $D > 0$, $D$ is positive with mean $\mathrm{E}[D_+]/p_+ = \delta/p_+$ (Lemma 0), finite. Lemma J with $r = 0.5$ gives $0 < h_+ \le 1$, with equality iff $D$ is constant given $D > 0$. Then
$$R = \mathrm{E}[D_+^{0.5}] = p_+\,\mathrm{E}[D^{0.5} \mid D > 0] = p_+\,h_+\left(\frac{\delta}{p_+}\right)^{0.5} = h_+\,(p_+\delta)^{0.5},$$
and likewise $I = h_-\,(p_-\delta)^{0.5}$. Dividing, $\delta$ cancels. ∎

*Reading.* By (A), $A = \frac{4}{\pi}\arctan\frac{R/I - 1}{R/I + 1}$ is an increasing function of $R/I$. So Asymmetry is positive when more of the probability lies above the mean ($p_+ > p_-$, the mean below the median) and when the deviations above the mean are more evenly spread than those below it ($h_+ > h_-$). A long right tail makes both factors small: few values above the mean, and spread unevenly. Hence Asymmetry is negative for right-skewed distributions, the opposite sign to moment skewness, by construction.

## H6. Asymmetry and the $L_{3/2}$-quantile of the mean

*Statement.* For $y$ with $\mathrm{E}|y|^{1.5} < \infty$, not constant, the mean is the $L_{3/2}$-quantile of $y$ at level $\tau^* = I/\nu$, and $A = \frac{4}{\pi}\arctan(1 - 2\tau^*)$.

*Proof.* For $\tau \in (0, 1)$ the $L_p$-quantile with $p = 3/2$ is the minimiser of $\psi_\tau(\theta) = \mathrm{E}\left[\,|\tau - \mathbf{1}(y < \theta)|\,|y - \theta|^{1.5}\right] = \tau\,\mathrm{E}[(y-\theta)_+^{1.5}] + (1-\tau)\,\mathrm{E}[(\theta - y)_+^{1.5}]$, finite for every $\theta$ because $\mathrm{E}|y|^{1.5} < \infty$. The map $x \mapsto x_+^{1.5}$ is convex and continuously differentiable with derivative $1.5\,x_+^{0.5}$; for $\theta$ in a bounded interval the difference quotients are dominated by $1.5(|y| + C)^{0.5}$, integrable, so by dominated convergence
$$\psi_\tau'(\theta) = 1.5\left[(1-\tau)\,\mathrm{E}[(\theta - y)_+^{0.5}] - \tau\,\mathrm{E}[(y - \theta)_+^{0.5}]\right].$$
The first expectation is non-decreasing and the second non-increasing in $\theta$, and on the interior of the convex hull of the support both are strictly monotone, so $\psi_\tau'$ is strictly increasing there; $\psi_\tau$ is strictly convex on that interval and has a unique minimiser, the root of $\psi_\tau'$. At $\theta = \mu_1$, $\psi_\tau'(\mu_1) = 1.5[(1-\tau) I - \tau R]$, which is zero iff $\tau = I/(R + I) = \tau^*$. As $\mu_1$ lies in the interior of the hull (Lemma 0), $\mu_1$ is the $L_{3/2}$-quantile at level $\tau^*$. Finally $(R - I)/\nu = (\nu - 2I)/\nu = 1 - 2\tau^*$, and (A) gives the formula. ∎

*Reading.* Asymmetry says where the mean sits within the distribution in the $L_{3/2}$ sense: $\tau^* < 1/2$ (mean below the $L_{3/2}$-median) gives $A > 0$. At $p = 1$ the same construction gives $\tau^* = F(\mu_1)$ and Tajuddin's measure $2F(\mu_1) - 1$ (up to sign); at $p = 2$ the mean is always the expectile at level 1/2 and the construction is empty.

## H7. Range of Hypotailedness and Extremity

*Statement.* For $y$ with a finite positive variance, $H \in (0, 1]$, with $H = 1$ exactly when $|y - \mu_1|$ is constant with probability one; hence $E \in (-1, 1]$, $E = 0$ for the uniform distribution and $E < 0$ exactly when $H < h_U = 2 \times 3^{-0.75}$.

*Proof.* Lemma J with $Z = D^2$ (mean $\sigma^2 < \infty$) and $r = 1/4$: $\nu = \mathrm{E}[(D^2)^{0.25}] \le (\sigma^2)^{0.25} = \sigma^{0.5}$, with equality iff $D^2$, i.e. $|D|$, is constant almost surely. $\sigma > 0$ means $D$ is not almost surely 0, so $\nu > 0$. Hence $0 < H \le 1$.

$0 < h_U < 1$, so $p = \log 0.5/\log h_U > 0$ and $u \mapsto 2u^p - 1$ is continuous and strictly increasing on $[0, 1]$ with $0 \mapsto -1$, $1 \mapsto 1$ and $h_U \mapsto 2 \times 0.5 - 1 = 0$ (as $h_U^p = 0.5$ by the choice of $p$). Hence $E \in (-1, 1]$ and $E < 0$ iff $H < h_U$. For the uniform distribution $H = h_U$ (H10), so $E = 0$. ∎

## H8. The sharp lower bound in a sample

*Statement.* For a sample $y_1, \ldots, y_n$ ($n \ge 2$), not all equal, with sample mean $m_1$ and $e_j = y_j - m_1$, the sample Hypotailedness $\hat H = \frac{\frac{1}{n}\sum_j |e_j|^{0.5}}{\left(\frac{1}{n}\sum_j e_j^2\right)^{0.25}}$ satisfies $\hat H \ge 2^{0.75} n^{-0.75}$, with equality exactly when two values lie at equal distances on either side of $m_1$ and all others equal $m_1$.

*Proof.* $\hat H = n^{-0.75} \left( \frac{(\sum_j |e_j|^{0.5})^4}{\sum_j e_j^2} \right)^{0.25}$. Let $P = \{j: e_j > 0\}$, $N = \{j: e_j < 0\}$, $S = \sum_{P} e_j = \sum_{N} |e_j|$ (the deviations sum to zero); $S > 0$ because the values are not all equal.

(a) For non-negative $a_1, \ldots, a_k$: $\sum \sqrt{a_i} \ge \sqrt{\sum a_i}$ (square both sides), with equality iff at most one $a_i$ is positive. Hence $\sum_j |e_j|^{0.5} \ge \sqrt{S} + \sqrt{S} = 2\sqrt{S}$.

(b) For non-negative $a_i$: $\sum a_i^2 \le (\sum a_i)^2$, with equality iff at most one $a_i$ is positive. Hence $\sum_j e_j^2 \le S^2 + S^2 = 2S^2$.

So $(\sum_j |e_j|^{0.5})^4 / \sum_j e_j^2 \ge 16 S^2 / (2 S^2) = 8$ and $\hat H \ge n^{-0.75}\,8^{0.25} = 2^{0.75} n^{-0.75}$. Equality needs equality in (a) and (b): exactly one positive and one negative deviation, which then equal $\pm S$, all others zero. Conversely such a sample gives equality. ∎

*Remark.* The manuscript's bound $n^{-0.75}$ holds but is not attained: the ratio of (a)–(b) is at least 8, not 1. For $n = 2$ the bound is 1, so $\hat H = 1$ for every sample of two distinct values.

## H9. One-sided Hypotailedness and the bounded Complex Extremity

*Statement.* For $y$ with a finite positive variance, $P(D = 0) = 0$ and $p_\pm > 0$: $H_\pm \in (0, 1]$, each 1 exactly when $|D|$ is constant on its side; $H_+ = H_- = h_U$ for the uniform distribution; $H_+ = H_- = H$ for a distribution symmetric about its mean; hence each part of CE lies in $(-1, 1]$ and is 0 for the uniform distribution.

*Proof.* Conditionally on $D > 0$, $D^2$ is positive with finite mean ($\le \sigma^2/p_+$). Lemma J with $Z = D^2$, $r = 1/4$ gives $0 < H_+ \le 1$, with equality iff $D$ is constant given $D > 0$; likewise $H_-$.

Uniform on $(b, c)$, $a = (c - b)/2$: given $D > 0$, $D$ is uniform on $(0, a)$, so $\mathrm{E}[D^{0.5} \mid D > 0] = \frac{2}{3}a^{0.5}$ and $\mathrm{E}[D^2 \mid D > 0] = a^2/3$; $H_+ = \frac{2}{3}a^{0.5}/(a^2/3)^{0.25} = \frac{2}{3}\,3^{0.25} = 2 \times 3^{-0.75} = h_U$, and $H_- = h_U$ by symmetry.

Symmetric with $P(D = 0) = 0$: $D$ and $-D$ have the same law, so the law of $D$ given $D > 0$ is the law of $|D|$ given $D \ne 0$, which is the law of $|D|$. Hence $H_+ = \mathrm{E}|D|^{0.5}/(\mathrm{E}D^2)^{0.25} = H$, and $H_- = H$ likewise.

The parts of CE are $u \mapsto 2u^p - 1$ applied to $H_\pm \in (0, 1]$; as in H7 they lie in $(-1, 1]$ and are 0 when $H_\pm = h_U$. ∎

*Remark.* Without the condition $P(D = 0) = 0$ the symmetric case gives $H_\pm = H\,(1 - p_0)^{-3/4}$ with $p_0 = P(D = 0)$, because $\nu = (1 - p_0)\,\mathrm{E}[|D|^{0.5} \mid D \ne 0]$ and $\sigma^2 = (1 - p_0)\,\mathrm{E}[D^2 \mid D \ne 0]$: an atom at the mean raises both one-sided values above $H$. (Corrected after the independent check; the run RN6 holds the earlier text with the exponent $-1/4$.)

## H17. Influence functions

*Statement.* At a distribution with finite variance (finite fourth moment for the variance terms to have finite second moments) and a density bounded near its mean, the influence function of $A$ is unbounded and grows linearly in the outlying value $x$ as $|x| \to \infty$, decreasing for large positive $x$; those of $H$ and $E$ grow quadratically and decrease in both directions.

*Proof.* Write $F_\varepsilon = (1 - \varepsilon)F + \varepsilon\,\Delta_x$ and $\mathrm{IF}_T(x) = \frac{d}{d\varepsilon} T(F_\varepsilon)\big|_{\varepsilon = 0}$.

*Mean and variance.* $\mu_1(F_\varepsilon) = \mu_1 + \varepsilon(x - \mu_1)$, so $\mathrm{IF}_{\mu_1}(x) = x - \mu_1$; $\mathrm{IF}_{\sigma^2}(x) = (x - \mu_1)^2 - \sigma^2$ (standard).

*Partial moments.* Let $m_+(t) = \mathrm{E}_F[(y - t)_+^{0.5}]$ and $m_-(t) = \mathrm{E}_F[(t - y)_+^{0.5}]$. If $F$ has a density $f$ bounded by $K$ on $(\mu_1 - \eta, \mu_1 + \eta)$, then $a_\pm = \mathrm{E}_F[|D|^{-0.5}\mathbf{1}(\pm D > 0)]$ are finite ($\int_0^\eta K d^{-0.5}\,dd < \infty$, and the rest of the integral is bounded by $\eta^{-0.5}$), and $m_\pm$ are differentiable at $\mu_1$ with $m_+'(\mu_1) = -a_+/2$ and $m_-'(\mu_1) = a_-/2$: for $h \to 0$ consider the difference quotient $q_h(y) = [(y - \mu_1 - h)_+^{0.5} - (y - \mu_1)_+^{0.5}]/h$. On $\{|D| > 2|h|\}$ the mean value theorem gives $|q_h(y)| \le \frac{1}{2}(|D| - |h|)^{-0.5} \le |D|^{-0.5}$, an integrable bound (bounded density near $\mu_1$, and $|D|^{-0.5} \le \eta^{-0.5}$ away from it), and $q_h(y) \to -\frac{1}{2}D^{-0.5}\mathbf{1}(D > 0)$; dominated convergence applies there. On $\{|D| \le 2|h|\}$, $|q_h| \le (3|h|)^{0.5}/|h| \le 2|h|^{-0.5}$ and the set has probability at most $4K|h|$ (for $|h| < \eta/2$), so its contribution is at most $8K|h|^{0.5} \to 0$, and the part of $a_+$ it removes tends to 0 as well. Hence $m_+'(\mu_1) = -\frac{1}{2}\mathrm{E}[D^{-0.5}\mathbf{1}(D > 0)]$. Then
$$R(F_\varepsilon) = (1 - \varepsilon)\,m_+(\mu_1 + \varepsilon(x - \mu_1)) + \varepsilon\,(x - \mu_1 - \varepsilon(x - \mu_1))_+^{0.5},$$
and differentiating at $\varepsilon = 0$:
$$\mathrm{IF}_R(x) = (x - \mu_1)_+^{0.5} - R - \frac{a_+}{2}(x - \mu_1), \qquad \mathrm{IF}_I(x) = (\mu_1 - x)_+^{0.5} - I + \frac{a_-}{2}(x - \mu_1).$$

*Asymmetry.* By (A), $A = \frac{4}{\pi}\arctan u$ with $u = (R - I)/(R + I)$. The chain rule gives $\mathrm{d}u = 2(I\,\mathrm{d}R - R\,\mathrm{d}I)/\nu^2$ and $\mathrm{d}A = \frac{4}{\pi}\,\mathrm{d}u/(1 + u^2)$, and $\nu^2(1 + u^2) = (R + I)^2 + (R - I)^2 = 2(R^2 + I^2)$, so
$$\mathrm{IF}_A(x) = \frac{4}{\pi}\,\frac{I\,\mathrm{IF}_R(x) - R\,\mathrm{IF}_I(x)}{R^2 + I^2}.$$
The constants cancel ($I \cdot (-R) - R \cdot (-I) = 0$), leaving
$$\mathrm{IF}_A(x) = \frac{4}{\pi(R^2 + I^2)}\left[I\,(x - \mu_1)_+^{0.5} - R\,(\mu_1 - x)_+^{0.5} - \frac{I a_+ + R a_-}{2}(x - \mu_1)\right].$$
The coefficient $\kappa_A = \frac{2(I a_+ + R a_-)}{\pi(R^2 + I^2)}$ is positive, and the square-root terms are $o(|x|)$, so $\mathrm{IF}_A(x) = -\kappa_A (x - \mu_1) + o(|x|)$: unbounded, linear, $\to -\infty$ as $x \to +\infty$ and $\to +\infty$ as $x \to -\infty$.

*Hypotailedness.* $\nu = R + I$ gives $\mathrm{IF}_\nu(x) = |x - \mu_1|^{0.5} - \nu - \frac{a_+ - a_-}{2}(x - \mu_1)$. With $H = \nu\,(\sigma^2)^{-1/4}$,
$$\mathrm{IF}_H(x) = \frac{\mathrm{IF}_\nu(x)}{\sigma^{0.5}} - \frac{\nu}{4\sigma^{2.5}}\left[(x - \mu_1)^2 - \sigma^2\right] = -\frac{H}{4\sigma^2}(x - \mu_1)^2 + O(|x|),$$
quadratic and $\to -\infty$ in both directions. *Extremity.* $\mathrm{IF}_E = 2pH^{p-1}\,\mathrm{IF}_H$, with $2pH^{p-1} > 0$: the same. ∎

*For comparison* (standard results, not proved here): moment skewness and excess kurtosis have influence functions growing like $|x|^3$ and $x^4$ (Ruppert 1987); L-moment ratios like $|x|$; quartile and octile measures and the medcouple have bounded influence functions (Brys et al. 2004).
