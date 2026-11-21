# Closed forms for standard distributions (hypotheses H10–H16, and their extended wordings)

Study `half-moments`, plans PL2 and PL11 (the extended wordings, at the end). Notation as in `properties.md`: $R$ and $I$ are the parts of the half central moment
above and below the mean, $\nu = R + I$, $H = \nu/\sigma^{0.5}$, $h_U = 2 \times 3^{-0.75}$.

**Lemma S (symmetric laws).** If $y$ is symmetric about its centre $m$ (its mean when the mean exists), then the half
central moment about $m$ is $(1+i)\,\nu/2$ with $\nu = \mathrm{E}|y - m|^{0.5}$. *Proof:* $R = I$ (H1, whose proof uses
only $D \overset{d}{=} -D$, so it holds about the centre of symmetry also when there is no mean), and $R + I = \nu$. ∎

So for every symmetric law below it suffices to find $\nu$; then the Asymmetry is 0 (H4) and $H = \nu/\sigma^{0.5}$.

**Lemma G.** For $s > 0$, $k > -1$: $\int_0^\infty z^{k} e^{-z^s}\,dz = \frac{1}{s}\Gamma\!\left(\frac{k+1}{s}\right)$ (substitute $u = z^s$).

## H10. Uniform distribution on $(b, c)$

$D$ is uniform on $(-a, a)$ with $a = (c - b)/2$. $\nu = \frac{1}{2a}\int_{-a}^{a}|d|^{0.5}\,dd = \frac{1}{a}\cdot\frac{2}{3}a^{1.5} = \frac{2}{3}a^{0.5}$,
so $\mu_{0.5} = (1+i)\frac{1}{3}a^{0.5} = (1+i)\frac{1}{3}\left(\frac{c-b}{2}\right)^{0.5}$. $\sigma^2 = (c-b)^2/12 = a^2/3$, so
$\sigma^{0.5} = a^{0.5}3^{-0.25}$ and $H = \frac{2}{3}\,3^{0.25} = 2 \times 3^{-0.75} = h_U$; Asymmetry 0 by Lemma S and H4;
Extremity $= 2h_U^p - 1 = 0$ by the definition of $p$. ∎

## H11. Normal distribution, standard deviation $\sigma$

By H3, $\mu_{0.5}(\mu + \sigma Z) = \sigma^{0.5}\mu_{0.5}(Z)$ for $Z$ standard normal. For $Z$: $R = \int_0^\infty z^{0.5}\frac{1}{\sqrt{2\pi}}e^{-z^2/2}dz$. With $z = \sqrt{2}\,w$:
$R = \frac{2^{0.75}}{\sqrt{2\pi}}\int_0^\infty w^{0.5}e^{-w^2}dw = \frac{2^{0.75}}{\sqrt{2\pi}}\cdot\frac{1}{2}\Gamma(0.75) = \Gamma(0.75)\,\pi^{-0.5}\,2^{-0.75}$ (Lemma G with $s = 2$, $k = 0.5$).
Hence $\mu_{0.5} = (1+i)\Gamma(0.75)\pi^{-0.5}2^{-0.75}\sigma^{0.5}$; $H = 2R = \Gamma(0.75)\pi^{-0.5}2^{0.25}$ (scale-free by H3 and $\sigma^{0.5}$); Asymmetry 0. ∎

(The manuscript's substitution "$y = x^{0.5}/2^{0.25}$, $dx = 2^{1.25} y\,dy$" should read $y = \sqrt{2}\,x^2$ in its notation, $dy = 2^{1.5} x\,dx$; its result is right.)

## H12. Laplace distribution, scale $b$

Density $\frac{1}{2b}e^{-|y - m|/b}$, symmetric about its mean $m$, variance $2b^2$.
$\nu = 2\int_0^\infty d^{0.5}\frac{1}{2b}e^{-d/b}\,dd = \frac{1}{b}\,b^{1.5}\,\Gamma(1.5) = \frac{\sqrt{\pi}}{2}b^{0.5}$, so
$\mu_{0.5} = (1+i)\frac{\sqrt{\pi}}{4}b^{0.5}$ and $H = \frac{\sqrt{\pi}}{2}b^{0.5}/(2b^2)^{0.25} = \frac{\sqrt{\pi}}{2}\,2^{-0.25}$. ∎

## H13. Generalised normal distribution, shape $s$, scale $\alpha$

Density $\frac{s}{2\alpha\Gamma(1/s)}\exp(-|y/\alpha|^s)$ (centred at 0). By Lemma G with $z = d/\alpha$:
$\mathrm{E}|y|^{k} = 2\cdot\frac{s}{2\alpha\Gamma(1/s)}\,\alpha^{k+1}\cdot\frac{1}{s}\Gamma\!\left(\frac{k+1}{s}\right) = \alpha^{k}\frac{\Gamma((k+1)/s)}{\Gamma(1/s)}$.
$k = 0.5$: $\nu = \alpha^{0.5}\Gamma(1.5/s)/\Gamma(1/s)$, so $\mu_{0.5} = (1+i)\frac{\alpha^{0.5}}{2}\frac{\Gamma(1.5/s)}{\Gamma(1/s)}$.
$k = 2$: $\sigma^2 = \alpha^2\Gamma(3/s)/\Gamma(1/s)$. Hence $H = \frac{\Gamma(1.5/s)}{\Gamma(1/s)}\left(\frac{\Gamma(1/s)}{\Gamma(3/s)}\right)^{0.25} = \Gamma(1.5/s)\,\Gamma(1/s)^{-0.75}\,\Gamma(3/s)^{-0.25}$. ∎
(Normal: $s = 2$; Laplace: $s = 1$.)

## H14. Student's t distribution, $\nu$ degrees of freedom

Write $T = Z/\sqrt{V/\nu}$ with $Z$ standard normal and $V \sim \chi^2_\nu$ independent. For $-1 < k < \nu$:
$\mathrm{E}|Z|^k = 2^{k/2}\Gamma(\frac{k+1}{2})/\sqrt{\pi}$ (Lemma G after $z = \sqrt{2}w$) and
$\mathrm{E}[V^{-k/2}] = 2^{-k/2}\Gamma(\frac{\nu - k}{2})/\Gamma(\frac{\nu}{2})$ (gamma integral, finite iff $k < \nu$). By independence
$$\mathrm{E}|T|^k = \nu^{k/2}\,\frac{\Gamma\left(\frac{k+1}{2}\right)\Gamma\left(\frac{\nu-k}{2}\right)}{\sqrt{\pi}\,\Gamma\left(\frac{\nu}{2}\right)},$$
which is also the formula of Kirkby, Nguyen & Nguyen (2019). With $k = 0.5$ it is finite iff $\nu > 0.5$; $T$ is symmetric about 0,
so by Lemma S the half central moment about 0 is $(1+i)\frac{\Gamma(0.75)\Gamma(\frac{\nu-0.5}{2})\nu^{0.25}}{2\sqrt{\pi}\Gamma(\frac{\nu}{2})}$. It is the
half central moment about the mean when the mean exists ($\nu > 1$); for $0.5 < \nu \le 1$ it is taken about the centre of
symmetry. For $\nu > 2$, $\sigma^2 = \nu/(\nu - 2)$ and $H = \frac{\Gamma(0.75)\Gamma(\frac{\nu-0.5}{2})\nu^{0.25}}{\sqrt{\pi}\Gamma(\frac{\nu}{2})}\left(\frac{\nu-2}{\nu}\right)^{0.25} = \frac{\Gamma(0.75)\Gamma(\frac{\nu-0.5}{2})(\nu-2)^{0.25}}{\sqrt{\pi}\Gamma(\frac{\nu}{2})}$. ∎

(The manuscript states the absolute-moment formula "for $k > \nu$"; it holds for $-1 < k < \nu$.)

## H15. Cauchy distribution, location 0, scale $\gamma$

For $-1 < k < 1$: $\mathrm{E}|y|^k = \frac{2}{\pi}\int_0^\infty \frac{\gamma\,d^k}{d^2 + \gamma^2}\,dd = \frac{2\gamma^k}{\pi}\int_0^\infty\frac{u^k}{1 + u^2}\,du = \frac{2\gamma^k}{\pi}\cdot\frac{\pi}{2\cos(k\pi/2)} = \gamma^k\sec(k\pi/2)$,
using $\int_0^\infty \frac{u^{k}}{1+u^2}du = \frac{\pi}{2\cos(k\pi/2)}$ for $|k| < 1$ (Beta integral: $u^2 = t/(1-t)$ gives $\frac{1}{2}B(\frac{k+1}{2}, \frac{1-k}{2}) = \frac{\pi}{2\sin(\pi(k+1)/2)}$). With $k = 0.5$ and Lemma S about the centre 0: $(1+i)\frac{\sqrt{\gamma}}{2}\sec(\pi/4)$. ∎
(Goria 1978 gives the same fractional absolute moments.)

## H16. Gamma distribution, shape $a$, rate $\lambda$

Density $\frac{\lambda^a}{\Gamma(a)}y^{a-1}e^{-\lambda y}$, $y > 0$, mean $c = a/\lambda$. With Tricomi's $U(\alpha, \beta, z) = \frac{1}{\Gamma(\alpha)}\int_0^\infty e^{-zt}t^{\alpha-1}(1+t)^{\beta-\alpha-1}dt$ and Kummer's ${}_1F_1(\alpha; \beta; z) = \frac{\Gamma(\beta)}{\Gamma(\alpha)\Gamma(\beta - \alpha)}\int_0^1 e^{zs}s^{\alpha-1}(1-s)^{\beta-\alpha-1}ds$:

*Upper part.* $y = c(1 + t)$: $R = \frac{\lambda^a}{\Gamma(a)}\int_c^\infty (y - c)^{0.5}y^{a-1}e^{-\lambda y}dy = \frac{\lambda^a c^{a+0.5}e^{-a}}{\Gamma(a)}\int_0^\infty t^{0.5}(1+t)^{a-1}e^{-at}dt$. This is $U$ with $\alpha = 1.5$, $\beta = a + 1.5$, $z = a$: the integral is $\Gamma(1.5)\,U(1.5, a + 1.5, a)$. Since $\lambda^a c^{a + 0.5} = a^{a+0.5}\lambda^{-0.5}$,
$$R = \frac{\Gamma(1.5)\,a^{a+0.5}e^{-a}}{\Gamma(a)\,\lambda^{0.5}}\,U(1.5, a + 1.5, a).$$

*Lower part.* $y = cs$: $I = \frac{\lambda^a c^{a + 0.5}}{\Gamma(a)}\int_0^1 (1 - s)^{0.5}s^{a-1}e^{-as}ds$. This is ${}_1F_1$ with $\alpha = a$, $\beta = a + 1.5$, $z = -a$: the integral is $B(a, 1.5)\,{}_1F_1(a; a + 1.5; -a)$, so
$$I = \frac{B(a, 1.5)\,a^{a+0.5}}{\Gamma(a)\,\lambda^{0.5}}\,{}_1F_1(a; a + 1.5; -a).$$

*Exponential ($a = 1$).* $U(\alpha, \alpha + 1, z) = z^{-\alpha}$, so $U(1.5, 2.5, 1) = 1$ and $R = \Gamma(1.5)e^{-1}\lambda^{-0.5} = \frac{\sqrt{\pi}}{2e\sqrt{\lambda}}$.
Directly, with $x = (1 - \lambda y)^{0.5}$: $I = \frac{2}{e\sqrt{\lambda}}\int_0^1 x^2 e^{x^2}dx$ and, since $\frac{d}{dx}\left[\frac{1}{2}xe^{x^2} - \frac{\sqrt{\pi}}{4}\mathrm{erfi}(x)\right] = x^2 e^{x^2}$ (as $\mathrm{erfi}'(x) = \frac{2}{\sqrt{\pi}}e^{x^2}$),
$I = \frac{2}{e\sqrt{\lambda}}\left(\frac{e}{2} - \frac{\sqrt{\pi}}{4}\mathrm{erfi}(1)\right) = \frac{2e - \sqrt{\pi}\,\mathrm{erfi}(1)}{2e\sqrt{\lambda}}$.
(The manuscript writes this antiderivative for $x^2e^{-x^2}$; it is the antiderivative of $x^2e^{+x^2}$.)

*Independence of $\lambda$.* Both parts are $\lambda^{-0.5}$ times a function of $a$, so $R/I$, hence the Asymmetry (by (A) of `properties.md`), depends on $a$ only. ∎

## Distributions without a closed form

For the lognormal, beta, Weibull and skew-normal distributions the integrals $\mathrm{E}[(y - \mu_1)_\pm^{0.5}]$ have no closed form in standard functions that we derive here; they are computed by numerical integration when needed.

## Asymmetry, Extremity and Complex Extremity of the standard distributions (plan PL11)

The closed forms H10–H16 are extended, each in a new wording that keeps everything the earlier one stated, by the
Asymmetry coefficient, the Extremity coefficient and the Complex Extremity. Notation as in `properties.md`:
$h_U = 2 \times 3^{-0.75}$, $p = \frac{\log 0.5}{\log h_U} \approx 5.2988$, $E = 2H^p - 1$, the one-sided Hypotailedness
$H_\pm$ and $\mathrm{CE} = (2H_+^p - 1) + i(2H_-^p - 1)$.

**Lemma C (symmetric laws).** If $y$ has a finite positive variance, a density, and a distribution symmetric about its
mean, then $A = 0$ and both parts of $\mathrm{CE}$ equal $E$. *Proof:* $R = I$ (H1), so $A = \frac{4}{\pi}\arctan 0 = 0$
by identity (A) of H4. A density puts no probability at the mean and, the variable not being constant, positive
probability on both sides (Lemma 0); then $H_+ = H_- = H$ (H9, for a law symmetric about its mean), so each part of
$\mathrm{CE}$ is $2H^p - 1 = E$. ∎

**Uniform (rewording of H10).** By H10, $A = 0$, $H = h_U$ and $E = 0$; by H9, $H_+ = H_- = h_U$, so both parts of
$\mathrm{CE}$ are $2h_U^p - 1 = 0$. ∎

**Normal (rewording of H11).** Lemma C with $H_N = \Gamma(0.75)\,\pi^{-0.5}\,2^{0.25} = 0.82218\ldots$ (H11):
$E = 2H_N^p - 1 = -0.29131\ldots$, and both parts of $\mathrm{CE}$ equal $E$. ∎

**Laplace (rewording of H12).** Lemma C with $H_L = \frac{\sqrt{\pi}}{2}\,2^{-0.25} = 0.74523\ldots$ (H12):
$A = 0$, $E = 2H_L^p - 1 = -0.57898\ldots$, both parts of $\mathrm{CE}$ equal $E$. ∎

**Generalised normal (rewording of H13).** Lemma C with $H(s)$ of H13 gives $A = 0$, $E = 2H(s)^p - 1$ and both parts of
$\mathrm{CE}$ equal to $E$. At $s = 1$ the law is the Laplace with $b = \alpha$, at $s = 2$ the normal with
$\sigma = \alpha/\sqrt{2}$ (H13 then gives $H_L$ and $H_N$). *Limit.* $\Gamma(x) = \Gamma(1 + x)/x$ and
$\Gamma(1 + x) \to 1$ as $x \to 0^+$, so with $x = \frac{1}{s}$,
$$H(s) = \frac{\Gamma(1 + 1.5x)}{1.5x}\left(\frac{\Gamma(1 + x)}{x}\right)^{-0.75}\left(\frac{\Gamma(1 + 3x)}{3x}\right)^{-0.25}
\to \frac{3^{0.25}}{1.5} = 2 \times 3^{-0.75} = h_U \quad (s \to \infty),$$
the powers of $x$ cancelling ($-1 + 0.75 + 0.25 = 0$). By continuity of $u \mapsto 2u^p - 1$, $E \to 2h_U^p - 1 = 0$. ∎

**Student's t (rewording of H14).** For $\nu > 1$ the mean 0 exists and the law is symmetric about it, so $A = 0$ (H1,
H4). For $\nu > 2$ the variance is finite and positive and Lemma C gives $E = 2H(\nu)^p - 1$, both parts of
$\mathrm{CE}$ equal to it, with $H(\nu)$ of H14. *As $\nu \to 2^+$:* $\Gamma\left(\frac{\nu-0.5}{2}\right) \to \Gamma(0.75)$
and $\Gamma\left(\frac{\nu}{2}\right) \to 1$ are finite and positive while $(\nu - 2)^{0.25} \to 0$, so $H(\nu) \to 0$ and
$E \to -1$. *As $\nu \to \infty$:* $\Gamma(z + a)/\Gamma(z + b) \sim z^{a - b}$ with $z = \frac{\nu}{2}$, $a = -0.25$,
$b = 0$ gives $\Gamma\left(\frac{\nu-0.5}{2}\right)/\Gamma\left(\frac{\nu}{2}\right) \sim \left(\frac{\nu}{2}\right)^{-0.25}$,
so $H(\nu) \sim \Gamma(0.75)\,\pi^{-0.5}\,(\nu-2)^{0.25}\left(\frac{\nu}{2}\right)^{-0.25} \to \Gamma(0.75)\,\pi^{-0.5}\,2^{0.25} = H_N$
and $E \to 2H_N^p - 1$, its normal value. ∎

**Cauchy (rewording of H15).** $\sec\frac{\pi}{4} = \sqrt{2}$, so the analogue of H15 is
$(1+i)\frac{\sqrt{\gamma}}{2}\sqrt{2} = (1+i)\sqrt{\frac{\gamma}{2}}$; its parts are equal (Lemma S), so its angle is
$\frac{\pi}{4}$ and the analogue of Asymmetry, $1 - \frac{4\phi}{\pi}$, is 0. Hypotailedness, Extremity and Complex
Extremity are defined for a finite positive variance only, and the Cauchy law has none. ∎

**Gamma (rewording of H16).** *Asymmetry*: identity (A) of H4 with $\mathcal{R}$ and $\mathcal{I}$ of H16.
*Hypotailedness*: $\sigma^2 = a/\lambda^2$, so $\sigma^{0.5} = a^{0.25}\lambda^{-0.5}$ and
$H = \frac{\mathcal{R} + \mathcal{I}}{\sigma^{0.5}} = \frac{\lambda^{0.5}}{a^{0.25}}(\mathcal{R} + \mathcal{I})$; $E = 2H^p - 1$.
*One-sided Hypotailedness.* With $c = a/\lambda$ and the gamma law of $y$: $P(y > c) = Q(a, a)$,
$\mathrm{E}[y\,\mathbf{1}(y > c)] = \frac{a}{\lambda}Q(a + 1, a)$, $\mathrm{E}[y^2\,\mathbf{1}(y > c)] = \frac{a(a+1)}{\lambda^2}Q(a + 2, a)$
(each moment of the gamma law is a gamma law of a higher shape, cut at $\lambda c = a$), so
$$M_+ = \mathrm{E}[(y - c)^2\,\mathbf{1}(y > c)] = \lambda^{-2}\left(a(a+1)q_2 - 2a^2 q_1 + a^2 q_0\right),\quad q_k = Q(a + k, a),$$
and likewise $M_-$ with the lower functions $r_k = P(a + k, a)$, and $p_+ = q_0$, $p_- = r_0$. By definition
$H_+ = \frac{\mathcal{R}/p_+}{(M_+/p_+)^{0.25}} = \mathcal{R}\,p_+^{-0.75}M_+^{-0.25}$, which is the stated form; $H_-$ likewise with
$\mathcal{I}$. *Independence of $\lambda$*: $\mathcal{R}, \mathcal{I} \propto \lambda^{-0.5}$ (H16) and $M_\pm \propto \lambda^{-2}$, so
$A$, $H$, $H_\pm$, $E$ and $\mathrm{CE}$ depend on $a$ alone. *Exponential* ($a = 1$, $\lambda = 1$): with H16's parts,
$A = \frac{4}{\pi}\arctan\frac{\mathcal{R} - \mathcal{I}}{\mathcal{R} + \mathcal{I}} = -0.21746\ldots$, $H = \mathcal{R} + \mathcal{I} = 0.78795\ldots$,
$E = -0.43430\ldots$. By memorylessness, $D$ given $D > 0$ is exponential with rate 1, so
$H_+ = \frac{\mathrm{E}Z^{0.5}}{(\mathrm{E}Z^2)^{0.25}} = \frac{\Gamma(1.5)}{2^{0.25}} = \frac{\sqrt{\pi}}{2}2^{-0.25} = H_L$ and the real part of
$\mathrm{CE}$ is $2H_L^p - 1$, the Laplace Extremity, $-0.57898\ldots$; the imaginary part is $2H_-^p - 1 = 0.20491\ldots$ ∎
