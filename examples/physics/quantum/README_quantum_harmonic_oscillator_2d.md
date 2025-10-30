# 2D Quantum Harmonic Oscillator Animation

## Overview
An **epic** visualization of the 2D quantum harmonic oscillator system, showcasing all the beautiful mathematics and physics behind this fundamental quantum system.

## Formulas Covered

### 1. 2D Wavefunction (Separation of Variables)
```
ψₙₓ,ₙᵧ(x,y) = ψₙₓ(x) · ψₙᵧ(y)
```

### 2. 1D Wavefunction
```
ψₙ(x) = e^(−x²/2) · Hₙ(x) / √(2ⁿ · n! · √π)
```

### 3. Hermite Polynomials
```
Hₙ(x) = (−1)ⁿ · e^(x²) · dⁿ/dxⁿ [e^(−x²)]
```

### 4. Energy Levels
```
Eₙₓ,ₙᵧ = (nₓ + nᵧ + 1) · ħω
```

### 5. Degeneracy
```
gₙₓ₊ₙᵧ = nₓ + nᵧ + 1
```

## Animation Scenes

1. **Introduction**: Beautiful title with animated particles
2. **Main Formulas**: Dramatic reveal of all key equations
3. **Separation of Variables**: Visualizing 2D → 1D × 1D decomposition
4. **Hermite Polynomials**: Plots of H₀ through H₅
5. **1D Wavefunctions**: Normalized wavefunctions for n=0,1,2,3
6. **2D Wavefunctions**: Epic 3D surface plots with rotating camera
7. **Energy & Degeneracy**: Energy level diagram showing state degeneracy
8. **Grand Finale**: All formulas with beautiful particle effects

## Rendering

### Preview Quality (Fast, ~30 seconds)
```bash
manim -pql examples/physics/quantum/quantum_harmonic_oscillator_2d.py QuantumHarmonicOscillator2D
```

### High Quality (Slow, ~5-10 minutes)
```bash
manim -pqh examples/physics/quantum/quantum_harmonic_oscillator_2d.py QuantumHarmonicOscillator2D
```

### 4K Production Quality
```bash
manim -pqk examples/physics/quantum/quantum_harmonic_oscillator_2d.py QuantumHarmonicOscillator2D
```

## Features

- **3D Visualization**: Uses ThreeDScene for stunning 3D wavefunction surfaces
- **Color-Coded**: Each formula component has distinct colors for clarity
- **Mathematical Rigor**: Properly normalized wavefunctions using scipy
- **Smooth Animations**: Progressive reveals with timing optimized for understanding
- **Camera Rotation**: Ambient camera rotation for 3D surface appreciation
- **Particle Effects**: Beautiful background particles and flash effects

## Dependencies

- Manim Community Edition (v0.19.0+)
- NumPy
- SciPy (for Hermite polynomials and factorial)

## Educational Value

This animation is perfect for:
- Quantum mechanics courses
- Graduate-level physics lectures
- Self-study of quantum systems
- Understanding separation of variables
- Visualizing energy level degeneracy

## Technical Notes

- Uses `scipy.special.hermite` for accurate Hermite polynomial evaluation
- Implements proper normalization: `1/√(2ⁿ · n! · √π)`
- Plots wavefunctions from n=0 to n=3 for clarity
- Shows quantum states: (0,0), (1,0), (0,1), (1,1)
- Energy levels displayed up to N=3 with full degeneracy

## Duration

Total animation length: ~3-4 minutes (depending on render quality and wait times)

## Customization

You can easily modify:
- Number of Hermite polynomials shown (change range in `hermite_polynomial_scene`)
- Number of quantum states visualized (add to `states` list in `wavefunction_2d_scene`)
- Camera angles and rotation speed (modify `set_camera_orientation` calls)
- Colors and styling (update color arrays)
- Animation timing (adjust `wait()` and `run_time` parameters)

---

**Created for**: Math-To-Manim project
**Formula Source**: 2D Quantum Harmonic Oscillator (quantum mechanics fundamental system)
**Animation Type**: Educational, Epic, 3D Visualization
