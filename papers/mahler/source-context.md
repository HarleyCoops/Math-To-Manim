# Source context: symmetric Mahler, family 087

Paper: OpenAI, *The symmetric Mahler conjecture and its equality cases*, September 22, 2026.
Requested collection: https://github.com/HarleyCoops/math
Pinned revision: adc7f1241b42e322a6451854ab7e4b4c146bf78a
PDF: https://github.com/HarleyCoops/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/The-symmetric-Mahler-conjecture-and-its-equality-cases-September-22-2026/paper.pdf
Formalization scope: https://github.com/HarleyCoops/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/docs/087.md

These notes were checked against the downloaded 26-page PDF. The source reports a Lean formalization of the symmetric inequality and Hanner equality classification. We have not run the Lean checker or independently validated the all-dimensional proof. Attribute that result to the manuscript. The three-dimensional symmetric result predates this paper (Iriyeh-Shibata, cited on paper page 2). The new claim here is every dimension and its equality cases, not the cube calculation or first proof in dimension three.

## Exact statement and examples (pages 1-2 and 5-6)

A convex body is compact, convex, with nonempty interior. Assume K=-K, centered at the origin. Its polar is
K^circ = {y in R^n : <x,y> <= 1 for every x in K}.
The volume product is P(K)=|K||K^circ|, using n-dimensional Lebesgue volume. The manuscript's Theorem 1.1 states P(K)>=4^n/n! for every n>=1; equality exactly for invertible linear images of Hanner polytopes. Do not conflate this with the nonsymmetric Mahler conjecture, which has a different constant and a translated polar.

For an invertible linear T, (TK)^circ=T^{-T}K^circ. Volumes get factors |det T| and |det T|^{-1}, so P(TK)=P(K). A nonuniform diagonal stretch diag(a,b,c) maps the polar by diag(1/a,1/b,1/c). No arbitrary interpolation of vertices certifies polar duality.

For K=[-1,1]^3, its polar is the octahedron |y1|+|y2|+|y3|<=1. The cube has volume 8. The octahedron's eight tetrahedra conv(0, +/-e1, +/-e2, +/-e3), one sign choice per orthant, each have volume 1/6, hence volume 4/3. P(K)=32/3=4^3/3!.
The Euclidean unit ball is self-polar, with volume 4*pi/3, hence volume product 16*pi^2/9, approximately 17.546, exceeding 32/3, approximately 10.667.

Hanner polytopes begin with centered intervals [-a,a]. If H1,H2 are Hanner polytopes, both their Cartesian product and conv((H1,0) union (0,H2)) are Hanner polytopes. Polarity exchanges these product and convex-hull operations. All Hanner bodies attain 4^n/n!, including mixed constructions; cubes and cross-polytopes are examples, not the entire all-dimensional classification.

## Actual proof route (page 3 and sections 3-6)

Start with an origin-symmetric polytope A={X in R^n: |b_i dot X|<=1}, whose nonzero pairwise nonproportional rows span R^n. Its polar is conv{+/-b_i}. The analytic lens is a complex planar domain D={v+it: |t|<=1, |v|<=lambda(t)}. It is mapped from the unit disk by
F(z)=(8/pi^2) sum_{j=0}^infinity (-1)^j z^(2j+1)/(2j+1)^2.
Uniform boundary angle gives F(exp(i Theta)) distributed as epsilon lambda(T)+iT, with T uniform on [-1,1] and an independent fair sign epsilon. Lambda is even, positive inside, zero at endpoints, with lambda''(t)=-sec(pi*t/2)<0. A lens sketch is an illustration unless this exact series or its width is computed; do not label an arbitrary ellipse as the exact conformal image.

For each X in int A define L_X={Y: |b_i dot Y|<=lambda(b_i dot X)}. A basis of n signed rows is feasible if its unique tight-constraint vector Y belongs to L_X. Sigma_X is the union of simplices conv(0,epsilon_1 b_i1,...,epsilon_n b_in) for feasible bases and signs. Each simplex lies in A^circ. Almost everywhere, these simplices have disjoint interiors. General Sigma_X need not fill the polar; paper Figure 2 and page 16 explicitly show missing volume.

The holomorphic isolated-zero mass estimate and boundary sampling establish S=sum_I P_I>=1, where P_I is a feasibility probability. Proposition 6.1, equation (27), page 15, then gives
1 <= S = (n!/4^n) integral_A |Sigma_X| dX <= (n!/4^n)|A||A^circ|.
The equality comes from the lens boundary law and a determinant change of variables; the final inequality comes from Sigma_X subset A^circ. This implies |A||A^circ|>=4^n/n!. Approximation extends the inequality to all origin-symmetric convex bodies (section 6.1). The video may illuminate this route but must name the analytic input rather than pretend tetrahedra alone prove it.

For the axis-aligned cube example the three rows are e1,e2,e3, so every sign choice is feasible; the eight tetrahedra tile the octahedron. That exact example is available on screen. A moving point can represent X while these eight pieces remain unchanged; avoid inventing missing-volume dynamics for this cube.

## Equality route (pages 17-23)

Lift K by its convex-hull sum with an interval, so the polar becomes K^circ times [-1,1]. Vanishing integrated missing volume supplies common feasibility witnesses. Endpoint lens asymptotics imply a metric-median property for triples in the polar norm. This implies the three-ball intersection property. The classical Hansen-Lima classification identifies finite-dimensional spaces with this property as recursive l1 and l-infinity sums, whose unit balls are Hanner polytopes. This is a separate equality argument; a cube example does not classify every equality case.
