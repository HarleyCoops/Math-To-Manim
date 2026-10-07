# Family 003: a fixed frontier for zeros

Primary paper: OpenAI, *The Quasi-Riemann Hypothesis: A Zero-Free Half-Plane Re(s)>7/8*, September 30, 2026.

User's manuscript map: https://github.com/HarleyCoops/math
Pinned source revision: `adc7f1241b42e322a6451854ab7e4b4c146bf78a`.
PDF: https://github.com/HarleyCoops/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/paper.pdf
LaTeX: https://github.com/HarleyCoops/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/build/paper.tex
Formalization scope: https://github.com/HarleyCoops/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/docs/003.md
Official release: https://openai.com/index/sharing-ai-progress-in-mathematics/

The PDF has 199 pages. These production notes were checked against the introduction (pp. 4-7), Proposition 2.1 (pp. 8-9), the first-stage overview (p. 10), and the concluding argument in Section 20. The complete PDF, LaTeX, extracted text and formalization-scope description are retained locally under `runs/astra/quasi-riemann-source/`. The film explains the manuscript's mechanism; it does not independently validate the full proof or rebuild the Lean artifacts. Attribute the new result to the manuscript.

## Exact scope

For every Dirichlet character chi, the paper claims L(s,chi) != 0 when Re(s)>7/8, with the principal-character pole at s=1 allowed. It also claims this for every finite-order Hecke L-function over F=Q(sqrt(-3)). The bound is uniform in character, conductor and imaginary height. The boundary itself is excluded from the zero-free assertion. No zero-free lower bound on |L| is implied by nonvanishing.

The quasi-Riemann hypothesis asks for some fixed theta<1 with zeta(s) != 0 for Re(s)>theta. The full Riemann hypothesis asks for every nontrivial zeta zero to satisfy Re(rho)=1/2. These are different strengths. Functional-equation symmetry and the claimed bound confine zeta's nontrivial zeros to 1/8<=Re(rho)<=7/8. They do not force the critical line. The zeta pole at s=1 is not a zero.

The source reports Lean coverage of the zeta, Dirichlet and finite-order Hecke 7/8 bounds and a uniform logarithmic real-zero gap, excluding principal poles. Later applications are outside that documented coverage. We have not independently run those formalizations.

## Classical numerical geometry

Write s=sigma+it. The series zeta(s)=sum n^(-s) and Euler product over primes are valid only for sigma>1; values in the critical strip require analytic continuation. L(s,chi)=sum chi(n)n^(-s) initially has the same sigma>1 restriction. Use actual complex values for a numerical zeta landscape, clearly label its height log(1+|zeta(s)|), and label sampling as illustration. A finite rendered window cannot prove a zero-free half-plane at every height.

Useful positive ordinates of known zeta zeros on the critical line are approximately 14.134725141734693, 21.022039638771555, 25.01085758014569 and 30.424876125859513. An Euler-Maclaurin continuation with N around 40-64 and several Bernoulli corrections is implementable using only numpy/math. Check its values and residuals against mpmath during production; mpmath cannot be imported by the retained screened scene. Exclude the pole, avoid branch-cut claims about a single-valued arg, and cap/scale heights with disclosed labels.

For a verified simple sampled zero rho, a sufficiently small positively oriented circle rho+r exp(i theta) maps under zeta to a loop winding once around the origin. The local model zeta(s) approximately equals zeta'(rho)(s-rho). Compute the image loop from zeta itself; label any linearization as local. This is the topology of phase winding in the complex plane, not a claim about a physical surface or a change in genus. Plot reciprocal magnitude nearby as a capped pole schematic. Never animate genuine known zeros moving when the theorem boundary moves.

## The argument to visualize

Pages 5-7: two stages compare two exact representations of a completed cubic-theta sum. Reflection bounds it directly; Poisson summation isolates a principal Mellin signal plus character rows. Part I obtains 11/12. Part II changes the normalized sum, adding prime compensation, unequal scales, inverse second-moment and plain-polynomial fourth-moment estimates to obtain 7/8. Do not call the two stages the same normalized sum, or reduce the theorem to a picture of zeta alone.

Proposition 2.1, pp. 8-9: beta_* is the supremum of 1/2 and real parts of zeros of the primitive finite-order Hecke family in 1/2<=Re(rho)<=1. It need not be attained by a rightmost zero. Assume Delta_0=beta_*-sigma_0>0. The exponents 0<omega<Delta_0 and sigma>0 must be chosen independently of the target character; implied constants may depend on it.

Let C(s)=s+c and delete a finite set S of Euler factors, all nonzero for Re(s)>0. With H_eta holomorphic and sup |H_eta-1|<=1/2 on Re(s)>sigma_0, define

    f_eta(Z) = (1/(2 pi i)) integral_{Re(s)=2} Z^{C(s)} exp((s-5/6)^2) H_eta(s)/L_F^S(s,eta) ds.

The two comparisons are |J_eta(Z)| <<_eta Z^{C(sigma_0)+omega} and |J_eta(Z)-f_eta(Z)| <<_eta Z^{C(beta_*)-sigma}. They imply |f_eta(Z)| <<_eta Z^{C(beta_*)-epsilon_*}, where epsilon_*=min(Delta_0-omega,sigma)>0. Rapid decay at Z down to zero and the power saving at infinity make the Mellin transform holomorphic on Re(s)>beta_*-epsilon_*.

Fourier inversion and the identity theorem identify the transform with exp((s-5/6)^2) H_eta(s)/L_F^S(s,eta) initially on Re(s)>1. Since |H_eta|>=1/2, this continues 1/L_F^S holomorphically into the new half-plane. The definition of the supremum supplies some zero inside it. Its reciprocal must have a pole there: contradiction. The bounds, not moving a contour across an assumed zero or a visual erasure, do the work.

The exact affine powers differ: Part I C(s)=s-2/3, giving C(11/12)=1/4; Part II C(s)=s-11/16, giving C(7/8)=3/16. The Hecke-to-Dirichlet transfer uses the norm lift and quadratic factorization into the Dirichlet functions for chi and chi chi_{-3}, away from harmless finite Euler factors; poles are treated separately.

The Eisenstein integers form a triangular lattice Z[(-1+i sqrt(3))/2] in the complex plane. This lattice may be a concrete 3D set piece for the number-field arithmetic. Caption the reflection, Poisson rows and moment panels as a proof map; do not fabricate computed character rows and label them data.

## Source card

OpenAI manuscript / 30 September 2026 / family 003 / Re(s)>7/8.
"Explains the manuscript; full proof and Lean build not independently checked."
