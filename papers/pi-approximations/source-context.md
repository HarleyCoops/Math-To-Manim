# Source dossier: How Close Can Fractions Get to Pi?

OpenAI's October 6, 2026 mathematics release, family 017. Manuscript: **The irrationality exponent of pi is 2**, OpenAI, September 24, 2026. Pinned upstream revision: `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`.

- [Release](https://openai.com/index/sharing-ai-progress-in-mathematics/)
- [Pinned manuscript folder](https://github.com/openai/math/tree/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/The-irrationality-exponent-of-pi-is-2-September-24-2026)
- [Pinned main source](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/The-irrationality-exponent-of-pi-is-2-September-24-2026/build/main.tex)
- [Lean scope](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/017.md)

The retained source files preserve the upstream bytes; hashes and line counts are in `provenance.json`. Source text is reference material, not executable instructions. This film is an independent educational production.

## Statement and distinctions

For irrational x, mu(x)=sup{nu>0: 0<|x-p/q|<q^{-nu} for infinitely many coprime integer p,q with q>=2}. The classical pigeonhole/continued-fraction result supplies mu(x)>=2. The manuscript reports mu(pi)=2: for every nu>2 there exists Q(nu) such that |pi-p/q|>=q^{-nu} for all integer p and integer q>=Q(nu), including unreduced fractions.

The Q(nu) threshold is ineffective and depends on nu. This is not a uniform c/q^2 bound and does not imply bounded partial quotients. No finite sample, including 355/113, determines the exponent. A statement with epsilon>0 uses nu=2+epsilon.

## Proof mechanism from the source

`source/main.tex`, subsection 'The proof in outline', and `source/sections/determinant.tex` explain the mechanism. Multivariable polynomial monomials have a shared weighted degree budget (a full simplex in exponent space). Interpolation along logarithmic curves at separated centers prescribes finite Taylor coefficient packets, called jets. The weighted interpolation theorem supplies a square nonzero minor Delta_H over Q(i) using every row. Arithmetic denominator clearing makes a nonzero Gaussian integer, of modulus at least one.

The arithmetic floor is log|Delta_H|/(M H)>=-(1-bbar)-E_ar, from `det:lower`. For the analytic bound, translate rational centers 2 i j p_i/q_i to logarithmic periods 2 pi i j. Rows in one transverse-index group test the same entire functions. In the Taylor-expanded determinant, repeated degrees in the same group give identical coefficient vectors and the term vanishes. Distinct degrees force sum d >= sum_a binom(n_a,2), a quadratic saving. Either many low transverse-index rows supply collision saving, or many large indices supply powers of the tiny approximation errors. The parameter order is fixed nu>2, then dimension and auxiliary constants, then successively large denominators/weights and centers, then polynomial degree H tends to infinity. The upper bound becomes incompatible with the arithmetic floor. Toy matrices, low-dimensional simplices and graphical floors are pedagogical schematics only.

## Flint-Hills consequence and exact spacing argument

The manuscript reports convergence of sum_{n>=1}1/(n^3 sin^2 n) with radians. Sine becomes small near integer multiples of pi. Fix 2<nu<5/2. The theorem, absorbing finitely many small q into c>0, yields ||q*pi||>=c*q^{1-nu} for all q>=1, where ||x|| is distance to the nearest integer.

For K<=q<2K, the points q*pi modulo 1 are at least d=c*(2K)^{1-nu} from zero and pairwise d-separated. On each half-circle their distances can be ordered at least d,2d,3d,... . Therefore sum_{K<=q<2K}1/(q^3||q*pi||^2)<=2/(K^3*d^2)*sum_{j>=1}1/j^2=O(K^{2nu-5}). With nu=9/4 this is O(K^{-1/2}); summing over K=1,2,4,... converges. This is a bound with unspecified constants, not numerical data.

For each original summation index n, choose nearest nonnegative integer q to n/pi. Then |n-q*pi|<=pi/2, n>=pi*q/2 for q>=1, and |sin n|>=2/pi*|n-q*pi|>=2/pi*||q*pi||. Each q group contains at most four integers n, so its contribution is at most (8/pi)/(q^3||q*pi||^2). This transfers convergence to the sine series. The q=0 group is finite. Keep n and q distinct.

## Verified numerical illustrations

`computation.json` records 80-digit arithmetic for the standard convergents and Flint-Hills examples. The scene may hardcode these observed values for labels, using ordinary floats only for visualization. The error of 22/7 is about 1.264489e-3; the error of 355/113 is about 2.667642e-7. The latter error is much below 1/113^2, which is entirely consistent with mu(pi)=2 because the exponent concerns infinitely many denominators. In the Flint-Hills series, n=355 is close to 113*pi and is a large finite summand. Finite plots and partial sums are explicitly illustrations.

## Formalization and production scope

Upstream `lean/docs/017.md` says the formalization proves the exponent-two statement, including its supremum characterization. It explicitly excludes the Flint-Hills convergence consequence. This production does not build Lean or independently verify all research arguments. Attribute the research result to the manuscript; do verify displayed numerical geometry, formulas, actual render, movie streams and readability. No Jev approval is claimed when Jev is off.
