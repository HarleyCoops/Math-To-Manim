/-
  DelayedPoleSurvival.lean
  ========================

  Three copies of a curve, two of them delayed by `log 2` and `log 4`, added
  with weights `-1`, `3`, `-2`:

      D(u) = -g(u) + 3 g(u - log 2) - 2 g(u - log 4).

  On the Laplace side this mix is multiplication by the *symbol*

      m(s) = -1 + 3·2^(-s) - 2·4^(-s) = (1 - 2^(-s)) (2·2^(-s) - 1).

  This file proves, with Mathlib only, that a simple pole at a point `ρ` of
  the open critical strip `0 < Re ρ < 1` survives the mix, with its residue
  multiplied by the nonzero number `m(ρ)`.

  Contents
    0. `Numeric`   : floating-point evaluation of the symbol (`#eval`, `#guard`).
    1. the mix     : `delay`, `mix`, `symbol`; the mix on exponential modes.
    2. the strip   : `1/2 < |2^(-s)| < 1`, the quantitative floor
                     `(1 - 2^(-σ)) (2·2^(-σ) - 1) ≤ |m(σ + it)|`, the zero set.
    3. Laplace     : a delay by `a` multiplies the transform by `e^(-sa)`.
    4. the pole    : an entire multiplier keeps a simple pole.
    5. the transfer: `PoleData g Φ Z → PoleData (mix (log 2) g) (m·Φ) Z`.
    6. the tent    : the same weights make the compact tent weight on (1, 4).

  Source and credit.  Sections 1, 3 and 5 are a Mathlib-only restatement of
  `ThetaTransfer.compactDifference_poleData` in
    Lee Crossley, "A delayed-difference window criterion for Dirichlet
    families", results/dirichlet-window-transfer/DelayedPole.lean,
    https://github.com/leecrossley/prime-window-rh-criterion  (CC BY 4.0).
  The proofs of `laplace_delay`, `symbol_pos_of_real` and `mix_poleData` are
  adapted from that file.  The structure `PoleData` below is a copy of
  `Deduction.PoleData` from the source release that the file above pins; the
  upstream lemmas it used (`laplace_integrable`, `poleData_dslope`) are
  proved here from Mathlib.  This file does not contain the Landau window
  theorem and does not prove any statement about zeros of L-functions.

  Toolchain: leanprover/lean4:v4.33.1, Mathlib 0df444a360eaa60ab8c11dca51a86af692955474.
-/
import Mathlib

open Complex MeasureTheory Set Filter Topology

namespace PrimeWindow

/-! ## 0. Computational layer: evaluate the symbol in floating point -/

namespace Numeric

/-- A complex number in floating point. -/
structure Cx where
  re : Float
  im : Float

def Cx.mul (a b : Cx) : Cx := ⟨a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re⟩

def Cx.abs (a : Cx) : Float := Float.sqrt (a.re * a.re + a.im * a.im)

def log2 : Float := Float.log 2.0

/-- `q = 2^(-s)` at `s = σ + i t`: radius `2^(-σ)`, angle `-t log 2`. -/
def q (σ t : Float) : Cx :=
  let r := Float.exp (-(σ * log2))
  ⟨r * Float.cos (t * log2), -(r * Float.sin (t * log2))⟩

/-- The symbol `m(s) = (1 - q)(2q - 1)` at `s = σ + i t`. -/
def symbolF (σ t : Float) : Cx :=
  let z := q σ t
  Cx.mul ⟨1 - z.re, -z.im⟩ ⟨2 * z.re - 1, 2 * z.im⟩

/-- The same number from the three weights: `-1 + 3q - 2q²`. -/
def symbolSumF (σ t : Float) : Cx :=
  let z := q σ t
  let z2 := Cx.mul z z
  ⟨-1 + 3 * z.re - 2 * z2.re, 3 * z.im - 2 * z2.im⟩

/-- The floor of `|m|` on the line `Re s = σ`: `(1 - 2^(-σ)) (2·2^(-σ) - 1)`. -/
def floorF (σ : Float) : Float :=
  let r := Float.exp (-(σ * log2))
  (1 - r) * (2 * r - 1)

/-- The smallest value of `|m(σ + it)| / floor(σ)` on a grid of the strip
(`σ = 0.01 … 0.99`, `t = 0 … 20` in steps of `0.05`). The theorem
`symbol_norm_lower` says this ratio is at least 1 everywhere. -/
def gridMinRatio : Float := Id.run do
  let mut best : Float := 1e9
  for i in [1:100] do
    for j in [0:401] do
      let σ := i.toFloat / 100
      let t := j.toFloat * 0.05
      let ratio := (symbolF σ t).abs / floorF σ
      if ratio < best then best := ratio
  return best

/-- The smallest value of `|m|` itself on the same grid. -/
def gridMinAbs : Float := Id.run do
  let mut best : Float := 1e9
  for i in [1:100] do
    for j in [0:401] do
      let v := (symbolF (i.toFloat / 100) (j.toFloat * 0.05)).abs
      if v < best then best := v
  return best

/-- Imaginary part of the first zero of the Riemann zeta function. -/
def gamma1 : Float := 14.134725141734693

-- `q` at the first zeta zero: about (-0.6586, 0.2575), radius 0.7071.
#eval (q 0.5 gamma1).re
#eval (q 0.5 gamma1).im
#eval (q 0.5 gamma1).abs
-- `m` at the first zeta zero: about -3.7106 + 1.4506 i, modulus 3.9840.
#eval (symbolF 0.5 gamma1).re
#eval (symbolF 0.5 gamma1).im
#eval (symbolF 0.5 gamma1).abs
-- The floor on the critical line: 3/√2 - 2 ≈ 0.12132.
#eval floorF 0.5
-- Grid minimum of |m| / floor (≥ 1) and of |m| (> 0).
#eval gridMinRatio
#eval gridMinAbs
-- The spacing of the zeros of `m` along each wall: 2π / log 2 ≈ 9.0647.
#eval 2 * 3.141592653589793 / log2

#guard 3.98 < (symbolF 0.5 gamma1).abs && (symbolF 0.5 gamma1).abs < 3.99
#guard ((symbolF 0.5 gamma1).re - (symbolSumF 0.5 gamma1).re).abs < 1e-12
#guard ((symbolF 0.5 gamma1).im - (symbolSumF 0.5 gamma1).im).abs < 1e-12
#guard 0.9999999 < gridMinRatio
#guard 0.001 < gridMinAbs
-- The walls do carry zeros: `m(2πi/log 2) = 0` and `m(1 + 2πi/log 2) = 0`.
#guard (symbolF 0.0 (2 * 3.141592653589793 / log2)).abs < 1e-12
#guard (symbolF 1.0 (2 * 3.141592653589793 / log2)).abs < 1e-12

end Numeric

noncomputable section

/-! ## 1. The mix and its symbol -/

/-- Delay `g` by `a`, and put zero where the delayed curve has not started. -/
def delay (a : ℝ) (g : ℝ → ℝ) (u : ℝ) : ℝ := if a < u then g (u - a) else 0

/-- Three copies of `g` with delays `0`, `c`, `2c` and weights `-1`, `3`, `-2`. -/
def mix (c : ℝ) (g : ℝ → ℝ) (u : ℝ) : ℝ :=
  -delay 0 g u + 3 * delay c g u - 2 * delay (2 * c) g u

/-- The multiplier of the mix on the Laplace side. With `c = log 2` and
`q = 2^(-s)` this is `(1 - q)(2q - 1)`. -/
def symbol (c : ℝ) (s : ℂ) : ℂ := (1 - cexp (-s * c)) * (2 * cexp (-s * c) - 1)

private theorem exp_double (c : ℝ) (s : ℂ) :
    cexp (-s * ((2 * c : ℝ) : ℂ)) = cexp (-s * c) ^ 2 := by
  rw [pow_two, ← Complex.exp_add, Complex.ofReal_mul]; congr 1; push_cast; ring

/-- The factored symbol is the sum of the three weighted delays. -/
theorem symbol_expand (c : ℝ) (s : ℂ) :
    symbol c s = -1 + 3 * cexp (-s * c) - 2 * cexp (-s * ((2 * c : ℝ) : ℂ)) := by
  rw [exp_double]; unfold symbol; ring

theorem symbol_differentiable (c : ℝ) : Differentiable ℂ (symbol c) := by
  unfold symbol
  fun_prop

/-- After the last delay has started, the mix is the plain three-term sum. -/
theorem mix_of_lt {c u : ℝ} (hc : 0 ≤ c) (hu : 2 * c < u) (g : ℝ → ℝ) :
    mix c g u = -g u + 3 * g (u - c) - 2 * g (u - 2 * c) := by
  have h0 : (0 : ℝ) < u := by linarith
  have h1 : c < u := by linarith
  simp [mix, delay, h0, h1, hu]

/-- An exponential mode is an eigenfunction of the mix: `e^(λu)` comes out
multiplied by the real symbol `-1 + 3e^(-λc) - 2e^(-2λc)`. -/
theorem mix_exp {c u : ℝ} (hc : 0 ≤ c) (hu : 2 * c < u) (lam : ℝ) :
    mix c (fun v => Real.exp (lam * v)) u =
      (-1 + 3 * Real.exp (-lam * c) - 2 * Real.exp (-lam * (2 * c))) * Real.exp (lam * u) := by
  rw [mix_of_lt hc hu]
  have e1 : Real.exp (lam * (u - c)) = Real.exp (-lam * c) * Real.exp (lam * u) := by
    rw [← Real.exp_add]; congr 1; ring
  have e2 : Real.exp (lam * (u - 2 * c)) = Real.exp (-lam * (2 * c)) * Real.exp (lam * u) := by
    rw [← Real.exp_add]; congr 1; ring
  rw [e1, e2]; ring

/-- The weights sum to zero, so the mix kills constants (the mode `s = 0`). -/
theorem mix_const {c u : ℝ} (hc : 0 ≤ c) (hu : 2 * c < u) (K : ℝ) :
    mix c (fun _ => K) u = 0 := by
  rw [mix_of_lt hc hu]; ring

/-- With `c = log 2` the mix also kills the growth `e^u` (the mode `s = 1`):
`-1 + 3/2 - 2/4 = 0`. -/
theorem mix_exp_log_two {u : ℝ} (hu : 2 * Real.log 2 < u) :
    mix (Real.log 2) Real.exp u = 0 := by
  have hc : 0 ≤ Real.log 2 := (Real.log_pos (by norm_num)).le
  rw [mix_of_lt hc hu]
  have h2 : Real.exp (Real.log 2) = 2 := Real.exp_log (by norm_num)
  have e1 : Real.exp (u - Real.log 2) = Real.exp u / 2 := by rw [Real.exp_sub, h2]
  have e2 : Real.exp (u - 2 * Real.log 2) = Real.exp u / 4 := by
    rw [Real.exp_sub, two_mul, Real.exp_add, h2]; norm_num
  rw [e1, e2]; ring

/-! ## 2. The strip: where `q = 2^(-s)` can be -/

/-- `|e^(-sc)| = e^(-Re(s) c)`: the radius of `q` depends only on `Re s`. -/
theorem norm_q (c : ℝ) (s : ℂ) : ‖cexp (-s * (c : ℂ))‖ = Real.exp (-s.re * c) := by
  simp [Complex.norm_exp]

theorem exp_neg_log_two : Real.exp (-Real.log 2) = 1 / 2 := by
  rw [Real.exp_neg, Real.exp_log (by norm_num)]; norm_num

/-- For `0 < σ < 1` the radius `2^(-σ)` lies strictly between `1/2` and `1`. -/
theorem radius_bounds {σ : ℝ} (h0 : 0 < σ) (h1 : σ < 1) :
    1 / 2 < Real.exp (-σ * Real.log 2) ∧ Real.exp (-σ * Real.log 2) < 1 := by
  have hc : 0 < Real.log 2 := Real.log_pos (by norm_num)
  constructor
  · rw [← exp_neg_log_two, Real.exp_lt_exp]; nlinarith
  · rw [Real.exp_lt_one_iff]; nlinarith

/-- The strip `0 < Re s < 1` goes into the open annulus `1/2 < |q| < 1`. -/
theorem q_mem_annulus {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    1 / 2 < ‖cexp (-s * (Real.log 2 : ℂ))‖ ∧ ‖cexp (-s * (Real.log 2 : ℂ))‖ < 1 := by
  rw [norm_q]; exact radius_bounds h0 h1

/-- The quantitative floor: on the line `Re s = σ`, `0 < σ < 1`,
`|m(s)| ≥ (1 - 2^(-σ)) (2·2^(-σ) - 1) > 0`. -/
theorem symbol_norm_lower {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    (1 - Real.exp (-s.re * Real.log 2)) * (2 * Real.exp (-s.re * Real.log 2) - 1)
      ≤ ‖symbol (Real.log 2) s‖ := by
  obtain ⟨hgt, hlt⟩ := radius_bounds h0 h1
  have hq : ‖cexp (-s * (Real.log 2 : ℂ))‖ = Real.exp (-s.re * Real.log 2) := norm_q _ s
  have h2 : ‖(2 : ℂ)‖ = 2 := by simp
  have a : 1 - Real.exp (-s.re * Real.log 2) ≤ ‖1 - cexp (-s * (Real.log 2 : ℂ))‖ := by
    have h := norm_sub_norm_le (1 : ℂ) (cexp (-s * (Real.log 2 : ℂ)))
    rw [norm_one, hq] at h; exact h
  have b : 2 * Real.exp (-s.re * Real.log 2) - 1 ≤ ‖2 * cexp (-s * (Real.log 2 : ℂ)) - 1‖ := by
    have h := norm_sub_norm_le (2 * cexp (-s * (Real.log 2 : ℂ))) (1 : ℂ)
    rw [norm_mul, norm_one, hq, h2] at h; exact h
  unfold symbol
  rw [norm_mul]
  exact mul_le_mul a b (by linarith) (norm_nonneg _)

/-- The floor is positive inside the strip. -/
theorem floor_pos {σ : ℝ} (h0 : 0 < σ) (h1 : σ < 1) :
    0 < (1 - Real.exp (-σ * Real.log 2)) * (2 * Real.exp (-σ * Real.log 2) - 1) := by
  obtain ⟨hgt, hlt⟩ := radius_bounds h0 h1
  exact mul_pos (by linarith) (by linarith)

/-- **No blind spot inside the strip.** The symbol has no zero with `0 < Re s < 1`. -/
theorem symbol_ne_zero {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    symbol (Real.log 2) s ≠ 0 :=
  norm_pos_iff.mp (lt_of_lt_of_le (floor_pos h0 h1) (symbol_norm_lower h0 h1))

/-- Every zero of the symbol lies on a wall of the strip. -/
theorem symbol_zero_re {s : ℂ} (h : symbol (Real.log 2) s = 0) : s.re = 0 ∨ s.re = 1 := by
  have hc : 0 < Real.log 2 := Real.log_pos (by norm_num)
  rcases mul_eq_zero.mp h with h | h
  · left
    have hq : cexp (-s * (Real.log 2 : ℂ)) = 1 := (sub_eq_zero.mp h).symm
    have hn := congrArg norm hq
    rw [norm_q, norm_one] at hn
    have h3 : -s.re * Real.log 2 = 0 := by
      have := Real.exp_injective (hn.trans Real.exp_zero.symm)
      exact this
    have h4 : s.re * Real.log 2 = 0 := by linarith
    rcases mul_eq_zero.mp h4 with h5 | h5
    · exact h5
    · exact absurd h5 hc.ne'
  · right
    have hq : 2 * cexp (-s * (Real.log 2 : ℂ)) = 1 := sub_eq_zero.mp h
    have hn := congrArg norm hq
    have h2 : ‖(2 : ℂ)‖ = 2 := by simp
    rw [norm_mul, norm_q, norm_one, h2] at hn
    have h3 : Real.exp (-s.re * Real.log 2) = Real.exp (-Real.log 2) := by
      rw [exp_neg_log_two]; linarith
    have h4 := Real.exp_injective h3
    have h5 : (s.re - 1) * Real.log 2 = 0 := by linarith
    rcases mul_eq_zero.mp h5 with h6 | h6
    · linarith
    · exact absurd h6 hc.ne'

/-- The left wall carries zeros: `m(2πin / log 2) = 0` for every integer `n`. -/
theorem symbol_zero_left (n : ℤ) :
    symbol (Real.log 2) (((2 * Real.pi * n / Real.log 2 : ℝ) : ℂ) * I) = 0 := by
  have hc : (Real.log 2 : ℂ) ≠ 0 := by
    exact_mod_cast (Real.log_pos (by norm_num : (1 : ℝ) < 2)).ne'
  have harg : -(((2 * Real.pi * n / Real.log 2 : ℝ) : ℂ) * I) * (Real.log 2 : ℂ) =
      ((-n : ℤ) : ℂ) * (2 * Real.pi * I) := by
    push_cast; field_simp
  have hq : cexp (-(((2 * Real.pi * n / Real.log 2 : ℝ) : ℂ) * I) * (Real.log 2 : ℂ)) = 1 := by
    rw [harg]; exact Complex.exp_int_mul_two_pi_mul_I (-n)
  unfold symbol; rw [hq]; ring

/-- The right wall carries zeros: `m(1 + 2πin / log 2) = 0` for every integer `n`. -/
theorem symbol_zero_right (n : ℤ) :
    symbol (Real.log 2) (1 + ((2 * Real.pi * n / Real.log 2 : ℝ) : ℂ) * I) = 0 := by
  have hc : (Real.log 2 : ℂ) ≠ 0 := by
    exact_mod_cast (Real.log_pos (by norm_num : (1 : ℝ) < 2)).ne'
  have harg : -(1 + ((2 * Real.pi * n / Real.log 2 : ℝ) : ℂ) * I) * (Real.log 2 : ℂ) =
      ((-Real.log 2 : ℝ) : ℂ) + ((-n : ℤ) : ℂ) * (2 * Real.pi * I) := by
    push_cast; field_simp; ring
  have hhalf : cexp (((-Real.log 2 : ℝ) : ℂ)) = 1 / 2 := by
    rw [← Complex.ofReal_exp, exp_neg_log_two]; norm_num
  have hq : cexp (-(1 + ((2 * Real.pi * n / Real.log 2 : ℝ) : ℂ) * I) * (Real.log 2 : ℂ)) = 1 / 2 := by
    rw [harg, Complex.exp_add, Complex.exp_int_mul_two_pi_mul_I (-n), hhalf, mul_one]
  unfold symbol; rw [hq]; ring

/-- On the real segment `0 < s < 1` the symbol is a positive real number.
(Adapted from `symbol_real` in the source file.) -/
theorem symbol_pos_of_real {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) (hi : s.im = 0) :
    0 < (symbol (Real.log 2) s).re ∧ (symbol (Real.log 2) s).im = 0 := by
  let c := Real.log 2
  obtain ⟨hgt, hlt⟩ := radius_bounds h0 h1
  have hs : (s.re : ℂ) = s := Complex.ext (by simp) (by simp [hi])
  have he : cexp (-s * (c : ℂ)) = (Real.exp (-s.re * c) : ℝ) := by
    rw [Complex.ofReal_exp, Complex.ofReal_mul, Complex.ofReal_neg, hs]
  let q := Real.exp (-s.re * c)
  have eq : symbol c s = (((1 - q) * (2 * q - 1) : ℝ) : ℂ) := by
    unfold symbol; rw [he]
    simp only [q, Complex.ofReal_mul, Complex.ofReal_sub, Complex.ofReal_one, Complex.ofReal_ofNat]
  change 0 < (symbol c s).re ∧ (symbol c s).im = 0
  rw [eq, Complex.ofReal_re, Complex.ofReal_im]
  exact ⟨mul_pos (by dsimp [q, c]; linarith) (by dsimp [q, c]; linarith), rfl⟩

/-! ## 3. Laplace: a delay is a multiplication -/

theorem delay_meas {g : ℝ → ℝ} (hg : Measurable g) (a : ℝ) : Measurable (delay a g) := by
  exact (hg.comp (measurable_id.sub_const a)).ite measurableSet_Ioi measurable_const

theorem delay_growth {g : ℝ → ℝ} {C a : ℝ} (hC : 0 ≤ C) (ha : 0 ≤ a)
    (hg : ∀ u : ℝ, 0 ≤ u → |g u| ≤ C * Real.exp (2 * u)) (u : ℝ) :
    |delay a g u| ≤ C * Real.exp (2 * u) := by
  unfold delay
  split_ifs with h
  · refine (hg _ (by linarith)).trans (mul_le_mul_of_nonneg_left ?_ hC)
    exact Real.exp_le_exp.mpr (by linarith)
  · simpa using mul_nonneg hC (Real.exp_pos (2 * u)).le

/-- Under the growth bound `|g(u)| ≤ C e^(2u)`, the Laplace integral converges
absolutely for `Re s > 2`. -/
theorem laplace_integrable {g : ℝ → ℝ} (hm : Measurable g) {C : ℝ}
    (hg : ∀ u : ℝ, 0 ≤ u → |g u| ≤ C * Real.exp (2 * u)) {s : ℂ} (hs : 2 < s.re) :
    IntegrableOn (fun u : ℝ => (g u : ℂ) * cexp (-s * u)) (Ioi 0) := by
  have hb : 0 < s.re - 2 := by linarith
  have hi : IntegrableOn (fun u : ℝ => C * Real.exp (-(s.re - 2) * u)) (Ioi 0) :=
    (exp_neg_integrableOn_Ioi 0 hb).const_mul C
  refine Integrable.mono' hi ?_ ?_
  · apply Measurable.aestronglyMeasurable
    fun_prop
  · refine (ae_restrict_iff' measurableSet_Ioi).mpr (Eventually.of_forall fun u hu => ?_)
    have hu0 : 0 ≤ u := le_of_lt hu
    have hre : (-s * (u : ℂ)).re = -s.re * u := by simp
    rw [norm_mul, Complex.norm_exp, Complex.norm_real, Real.norm_eq_abs, hre]
    calc |g u| * Real.exp (-s.re * u)
        ≤ C * Real.exp (2 * u) * Real.exp (-s.re * u) :=
          mul_le_mul_of_nonneg_right (hg u hu0) (Real.exp_pos _).le
      _ = C * Real.exp (-(s.re - 2) * u) := by
          rw [mul_assoc, ← Real.exp_add]; congr 2; ring

/-- **A delay is a multiplication.** Delaying `g` by `a ≥ 0` multiplies its
one-sided Laplace transform by `e^(-sa)`. (Adapted from the source file.) -/
theorem laplace_delay (g : ℝ → ℝ) (s : ℂ) {a : ℝ} (ha : 0 ≤ a) :
    (∫ u in Ioi (0 : ℝ), (delay a g u : ℂ) * cexp (-s * u)) =
      cexp (-s * a) * ∫ u in Ioi (0 : ℝ), (g u : ℂ) * cexp (-s * u) := by
  let f := (Ioi (0 : ℝ)).indicator (fun v : ℝ => (g v : ℂ) * cexp (-s * v))
  rw [← integral_indicator measurableSet_Ioi, ← integral_indicator measurableSet_Ioi]
  have h : (Ioi (0 : ℝ)).indicator (fun u : ℝ => (delay a g u : ℂ) * cexp (-s * u)) =
      fun u : ℝ => cexp (-s * a) * f (u + -a) := by
    funext u
    by_cases hau : a < u
    · have h0 : 0 < u := lt_of_le_of_lt ha hau
      have h1 : 0 < u - a := by linarith
      simp only [indicator_of_mem (show u ∈ Ioi (0:ℝ) from h0), delay, if_pos hau, f,
        ← sub_eq_add_neg, indicator_of_mem (show u - a ∈ Ioi (0:ℝ) from h1)]
      have ee : cexp (-s * (u : ℂ)) = cexp (-s * a) * cexp (-s * ((u-a : ℝ) : ℂ)) := by
        rw [← Complex.exp_add, Complex.ofReal_sub]; congr 1; ring
      rw [ee]; ring
    · have h1 : u + -a ∉ Ioi (0 : ℝ) := by change ¬ 0 < u + -a; linarith
      simp only [f, indicator_of_notMem h1, mul_zero]
      by_cases h0 : u ∈ Ioi (0 : ℝ)
      · simp [indicator_of_mem h0, delay, hau]
      · simp [h0]
  rw [h, integral_const_mul, integral_add_right_eq_self]

/-- **The mix is a multiplication.** If the three delayed integrands are
integrable, the Laplace transform of the mix is the symbol times the
Laplace transform of `g`. -/
theorem laplace_mix (g : ℝ → ℝ) (s : ℂ) {c : ℝ} (hc : 0 ≤ c)
    (hi : ∀ a : ℝ, 0 ≤ a →
      IntegrableOn (fun u : ℝ => (delay a g u : ℂ) * cexp (-s * u)) (Ioi 0)) :
    (∫ u in Ioi (0 : ℝ), (mix c g u : ℂ) * cexp (-s * u)) =
      symbol c s * ∫ u in Ioi (0 : ℝ), (g u : ℂ) * cexp (-s * u) := by
  let J (a : ℝ) (u : ℝ) := (delay a g u : ℂ) * cexp (-s * u)
  have hfunc : (fun u : ℝ => (mix c g u : ℂ) * cexp (-s * u)) =
      fun u => -J 0 u + (3 : ℂ) * J c u - (2 : ℂ) * J (2 * c) u := by
    funext u; dsimp [mix, J]; push_cast; ring
  have h2c : (0 : ℝ) ≤ 2 * c := by positivity
  rw [hfunc, integral_sub (f := fun u => -J 0 u + (3 : ℂ) * J c u)
      (g := fun u => (2 : ℂ) * J (2 * c) u)
      ((hi 0 le_rfl).neg.add ((hi c hc).const_mul 3)) ((hi (2 * c) h2c).const_mul 2),
    integral_add (f := fun u => -J 0 u) (g := fun u => (3 : ℂ) * J c u)
      (hi 0 le_rfl).neg ((hi c hc).const_mul 3), integral_neg,
    integral_const_mul, integral_const_mul]
  change -(∫ u in Ioi (0 : ℝ), (delay 0 g u : ℂ) * cexp (-s * u)) +
      3 * (∫ u in Ioi (0 : ℝ), (delay c g u : ℂ) * cexp (-s * u)) -
      2 * (∫ u in Ioi (0 : ℝ), (delay (2 * c) g u : ℂ) * cexp (-s * u)) = _
  rw [laplace_delay g s le_rfl, laplace_delay g s hc, laplace_delay g s h2c, exp_double]
  have h0 : cexp (-s * ((0 : ℝ) : ℂ)) = 1 := by simp
  rw [h0]; unfold symbol; ring

/-! ## 4. The pole: an entire multiplier keeps a simple pole -/

/-- If `Φ(s) = r/(s - ρ) + h(s)` near `ρ` with `h` analytic at `ρ`, and `m` is
entire, then `m(s) Φ(s) = m(ρ) r/(s - ρ) + h'(s)` near `ρ` with `h'` analytic
at `ρ`. The new residue is `m(ρ) r`. -/
theorem pole_transfer {m Φ h : ℂ → ℂ} {ρ r : ℂ} (hm : Differentiable ℂ m)
    (hh : AnalyticAt ℂ h ρ) (hΦ : ∀ᶠ s in 𝓝[≠] ρ, Φ s = r / (s - ρ) + h s) :
    ∃ h' : ℂ → ℂ, AnalyticAt ℂ h' ρ ∧
      ∀ᶠ s in 𝓝[≠] ρ, m s * Φ s = (m ρ * r) / (s - ρ) + h' s := by
  have hM : AnalyticAt ℂ m ρ := hm.analyticAt ρ
  have hD : AnalyticAt ℂ (dslope m ρ) ρ := by
    have hd : DifferentiableOn ℂ (dslope m ρ) univ :=
      (Complex.differentiableOn_dslope univ_mem).mpr hm.differentiableOn
    exact hd.analyticAt univ_mem
  refine ⟨fun s => m s * h s + dslope m ρ s * r,
    (hM.mul hh).add (hD.mul analyticAt_const), ?_⟩
  filter_upwards [hΦ, self_mem_nhdsWithin] with s hs hne
  have hn : s ≠ ρ := hne
  rw [hs, dslope_of_ne _ hn, slope_def_field]
  field_simp [sub_ne_zero.mpr hn]
  ring

/-- **The pole survives the mix.** A simple pole of `Φ` at a point `ρ` of the
open strip, with residue `r ≠ 0`, is a simple pole of `m·Φ` with the nonzero
residue `m(ρ) r`. -/
theorem pole_survives_mix {Φ h : ℂ → ℂ} {ρ r : ℂ} (h0 : 0 < ρ.re) (h1 : ρ.re < 1)
    (hr : r ≠ 0) (hh : AnalyticAt ℂ h ρ)
    (hΦ : ∀ᶠ s in 𝓝[≠] ρ, Φ s = r / (s - ρ) + h s) :
    symbol (Real.log 2) ρ * r ≠ 0 ∧ ∃ h' : ℂ → ℂ, AnalyticAt ℂ h' ρ ∧
      ∀ᶠ s in 𝓝[≠] ρ, symbol (Real.log 2) s * Φ s =
        (symbol (Real.log 2) ρ * r) / (s - ρ) + h' s :=
  ⟨mul_ne_zero (symbol_ne_zero h0 h1) hr,
    pole_transfer (symbol_differentiable _) hh hΦ⟩

/-- The size of the new residue is at least the floor times the old size. -/
theorem residue_norm_lower {ρ r : ℂ} (h0 : 0 < ρ.re) (h1 : ρ.re < 1) :
    (1 - Real.exp (-ρ.re * Real.log 2)) * (2 * Real.exp (-ρ.re * Real.log 2) - 1) * ‖r‖
      ≤ ‖symbol (Real.log 2) ρ * r‖ := by
  rw [norm_mul]
  exact mul_le_mul_of_nonneg_right (symbol_norm_lower h0 h1) (norm_nonneg r)

/-! ## 5. The transfer of pole data -/

/-- Copy of `Deduction.PoleData` from the source release pinned by the source
file: `Φ` continues the Laplace transform of `g` to `Re s > 0` away from `Z`,
with a simple pole at every point of `Z` (positive real residue at real
points). -/
structure PoleData (g : ℝ → ℝ) (Φ : ℂ → ℂ) (Z : Set ℂ) : Prop where
  meas : Measurable g
  growth : ∃ C : ℝ, ∀ u : ℝ, 0 ≤ u → |g u| ≤ C * Real.exp (2 * u)
  laplace : ∀ s : ℂ, 2 < s.re → Φ s = ∫ u in Ioi (0 : ℝ), (g u : ℂ) * cexp (-s * u)
  pos : ∀ ρ ∈ Z, 0 < ρ.re
  diff : DifferentiableOn ℂ Φ ({s : ℂ | 0 < s.re} \ Z)
  iso : ∀ z : ℂ, 0 < z.re → ∀ᶠ w in 𝓝[≠] z, w ∉ Z
  pole : ∀ ρ ∈ Z, ∃ c : ℂ, c ≠ 0 ∧ (ρ.im = 0 → 0 < c.re ∧ c.im = 0) ∧
    ∃ h : ℂ → ℂ, AnalyticAt ℂ h ρ ∧ ∀ᶠ s in 𝓝[≠] ρ, Φ s = c / (s - ρ) + h s

/-- **The mix keeps every pole.** If every point of `Z` lies in `Re ρ < 1`,
the mix of `g` has pole data `(m·Φ, Z)`: same pole set, residues multiplied by
`m(ρ) ≠ 0`. (Mathlib-only version of `compactDifference_poleData`.) -/
theorem mix_poleData {g : ℝ → ℝ} {Φ : ℂ → ℂ} {Z : Set ℂ}
    (p : PoleData g Φ Z) (strip : ∀ ρ ∈ Z, ρ.re < 1) :
    PoleData (mix (Real.log 2) g) (fun s => symbol (Real.log 2) s * Φ s) Z := by
  let c := Real.log 2
  have hc : 0 ≤ c := (Real.log_pos (by norm_num : (1:ℝ) < 2)).le
  obtain ⟨C, hC⟩ := p.growth
  have hCp : 0 ≤ C := by
    have h := hC 0 le_rfl
    simpa using (abs_nonneg (g 0)).trans h
  have hg (a : ℝ) (ha : 0 ≤ a) := delay_growth hCp ha hC
  refine ⟨((delay_meas p.meas 0).neg.add (measurable_const.mul (delay_meas p.meas c))).sub
    (measurable_const.mul (delay_meas p.meas (2*c))), ⟨6*C, ?_⟩, ?_, p.pos, ?_, p.iso, ?_⟩
  · intro u _
    change |-(delay 0 g u) + 3 * delay c g u - 2 * delay (2*c) g u| ≤ _
    have h := abs_add_le (-(delay 0 g u) + 3 * delay c g u) (-(2 * delay (2*c) g u))
    rw [← sub_eq_add_neg, abs_neg] at h
    have h' := abs_add_le (-(delay 0 g u)) (3 * delay c g u)
    rw [abs_neg, abs_mul, abs_of_pos (by norm_num : (0:ℝ)<3)] at h'
    rw [abs_mul, abs_of_pos (by norm_num : (0:ℝ)<2)] at h
    linarith [hg 0 le_rfl u, hg c hc u, hg (2*c) (by positivity) u]
  · intro s hs
    have hi (a : ℝ) (ha : 0 ≤ a) :
        IntegrableOn (fun u : ℝ => (delay a g u : ℂ) * cexp (-s * u)) (Ioi 0) :=
      laplace_integrable (delay_meas p.meas a) (fun u _ => hg a ha u) hs
    change symbol c s * Φ s = ∫ u in Ioi (0:ℝ), (mix c g u : ℂ) * cexp (-s*u)
    rw [laplace_mix g s hc hi, ← p.laplace s hs]
  · intro s hs
    exact ((symbol_differentiable c).differentiableAt).differentiableWithinAt.mul (p.diff s hs)
  · intro ρ hρ
    obtain ⟨r, hr, hreal, h, hh, hloc⟩ := p.pole ρ hρ
    obtain ⟨hne, h', hh', hloc'⟩ := pole_survives_mix (p.pos ρ hρ) (strip ρ hρ) hr hh hloc
    refine ⟨symbol c ρ * r, hne, ?_, h', hh', hloc'⟩
    intro hi
    obtain ⟨ha, hb⟩ := symbol_pos_of_real (p.pos ρ hρ) (strip ρ hρ) hi
    obtain ⟨hx, hy⟩ := hreal hi
    change 0 < (symbol c ρ).re at ha
    change (symbol c ρ).im = 0 at hb
    simp [Complex.mul_re, Complex.mul_im, hb, hy, mul_pos ha hx]

/-! ## 6. The tent: what the weights are for -/

/-- The ramp `(x - 1)₊`. -/
def ramp (x : ℝ) : ℝ := max (x - 1) 0

/-- The compact tent weight: `2(1 - 1/t)` on `(1, 2]`, `4/t - 1` on `(2, 4)`,
zero elsewhere. It is `1` at `t = 2` and `0` at `t = 1` and `t = 4`. -/
def tent (t : ℝ) : ℝ :=
  if t ≤ 1 then 0 else if t ≤ 2 then 2 * (1 - 1 / t) else if t < 4 then 4 / t - 1 else 0

/-- The weights `1, -3, 2` on the ramps at scales `4, 2, 1` make the tent:
`(4/t - 1)₊ - 3 (2/t - 1)₊ + 2 (1/t - 1)₊ = tent t`. Every `t ≤ 1` cancels,
so the three-term difference of ramps is a sum over the window `(1, 4)` only. -/
theorem tent_eq {t : ℝ} (ht : 0 < t) :
    ramp (4 / t) - 3 * ramp (2 / t) + 2 * ramp (1 / t) = tent t := by
  unfold ramp tent
  by_cases h1 : t ≤ 1
  · have a1 : 1 ≤ 1 / t := (one_le_div ht).mpr h1
    have a2 : 1 ≤ 2 / t := (one_le_div ht).mpr (by linarith)
    have a4 : 1 ≤ 4 / t := (one_le_div ht).mpr (by linarith)
    rw [if_pos h1, max_eq_left (by linarith), max_eq_left (by linarith),
      max_eq_left (by linarith)]
    field_simp
    ring
  · have h1' : 1 < t := not_le.mp h1
    have b1 : 1 / t ≤ 1 := (div_le_one ht).mpr h1'.le
    rw [if_neg h1, max_eq_right (a := 1 / t - 1) (by linarith)]
    by_cases h2 : t ≤ 2
    · have a2 : 1 ≤ 2 / t := (one_le_div ht).mpr h2
      have a4 : 1 ≤ 4 / t := (one_le_div ht).mpr (by linarith)
      rw [if_pos h2, max_eq_left (by linarith), max_eq_left (by linarith)]
      field_simp
      ring
    · have h2' : 2 < t := not_le.mp h2
      have b2 : 2 / t ≤ 1 := (div_le_one ht).mpr h2'.le
      rw [if_neg h2, max_eq_right (a := 2 / t - 1) (by linarith)]
      by_cases h4 : t < 4
      · have a4 : 1 ≤ 4 / t := (one_le_div ht).mpr h4.le
        rw [if_pos h4, max_eq_left (by linarith)]
        ring
      · have b4 : 4 / t ≤ 1 := (div_le_one ht).mpr (not_lt.mp h4)
        rw [if_neg h4, max_eq_right (by linarith)]
        ring

end

end PrimeWindow

/-! ## Axiom audit -/
#print axioms PrimeWindow.symbol_ne_zero
#print axioms PrimeWindow.symbol_norm_lower
#print axioms PrimeWindow.laplace_mix
#print axioms PrimeWindow.pole_survives_mix
#print axioms PrimeWindow.mix_poleData
#print axioms PrimeWindow.tent_eq
