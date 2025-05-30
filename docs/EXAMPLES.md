# Math-To-Manim Examples

This document showcases the various mathematical animations available in the Math-To-Manim repository. Each example demonstrates the capability of AI models to generate complex mathematical visualizations.

## Quantum Field Theory

### QED Journey
**Files:**
- `Scripts/QED.py`
- `Scripts/Verbose_QED.py`
- `Scripts/rotated_QED.py`
- `Scripts/rotated_QED2.py`
- `Hunyuan-T1QED.py`
- `QEDGemini25.py`
- `QwenMaxQED/qwenQED.py`
- `Scripts/Gemini2.5ProQED.py`
- `Scripts/grok_quantum2.py`

These files contain animations that visualize Quantum Electrodynamics (QED), the quantum field theory of the electromagnetic interaction. They include visualizations of:

- Minkowski spacetime
- Electric and magnetic fields
- Maxwell's equations in tensor form
- QED Lagrangian density
- Feynman diagrams
- Fine structure constant
- Renormalization group flow

**Example Usage:**
```bash
python -m manim -qh Scripts/QED.py QEDJourney
```

### Spacetime QED Scene
**File:** `SpacetimeQEDScene.py`

A specialized visualization of QED concepts in spacetime, with emphasis on the relativistic aspects of the theory.

**Example Usage:**
```bash
python -m manim -qh SpacetimeQEDScene.py SpacetimeQEDScene
```

## Optimal Transport Theory

### Benamou-Brenier-Wasserstein
**Files:**
- `Benamou-Brenier/Google_Thinking_one_shot.py`
- `RevisedBenamou-Brenier/scene1.py`
- `Scripts/diffusion_optimal_transport.py`
- `Scripts/diffusion_ot.py`

These animations visualize the Benamou-Brenier formulation of the Wasserstein distance and optimal transport theory. They demonstrate:

- Fluid dynamics interpretation of optimal transport
- Geodesics in the space of probability measures
- Connections to diffusion processes

**Example Usage:**
```bash
python -m manim -qh Benamou-Brenier/Google_Thinking_one_shot.py BenamouBrenierScene
```

## Physics Simulations

### Gravitational Waves
**Files:**
- `GravityWavesDiscovery/gravitational_wave.py`
- `GravityWavesDiscovery/Mistral_gravity_wave.py`

Animations depicting the discovery and properties of gravitational waves, including:

- Spacetime distortion
- LIGO detection method
- Binary black hole mergers

**Example Usage:**
```bash
python -m manim -qh GravityWavesDiscovery/gravitational_wave.py GravitationalWaveScene
```

### Electroweak Symmetry
**File:** `Scripts/ElectroweakSymmetryScene.py`

Visualization of electroweak symmetry breaking and the Higgs mechanism.

**Example Usage:**
```bash
python -m manim -qh Scripts/ElectroweakSymmetryScene.py ElectroweakSymmetryScene
```

## Mathematical Concepts

### Information Geometry
**Files:**
- `Scripts/information_geometry.py`
- `Scripts/information_geometry2.py`

Animations exploring the geometric structure of probability distributions and statistical manifolds.

**Example Usage:**
```bash
python -m manim -qh Scripts/information_geometry.py InformationGeometryScene
```

### Fractal Geometry
**File:** `Scripts/fractal_scene.py`

Visualization of fractal patterns and their mathematical properties.

**Example Usage:**
```bash
python -m manim -qh Scripts/fractal_scene.py FractalScene
```

### Pythagorean Theorem
**File:** `Scripts/pythagorean.py`

A visual proof of the Pythagorean theorem.

**Example Usage:**
```bash
python -m manim -qh Scripts/pythagorean.py PythagoreanScene
```

## Algorithm Visualizations

### Gale-Shapley Algorithm
**File:** `Scripts/gale-shaply.py`

Animation of the Gale-Shapley algorithm for the stable matching problem.

**Example Usage:**
```bash
python -m manim -qh Scripts/gale-shaply.py GaleShapleyScene
```

### Regularization in Machine Learning
**File:** `Scripts/regularization.py`

Visualization of regularization techniques in machine learning.

**Example Usage:**
```bash
python -m manim -qh Scripts/regularization.py RegularizationScene
```

## Physics Simulations

### Bouncing Balls
**Files:**
- `3BouncingBalls/bouncing_balls.py`
- `Rhombicosidodecahedron/bouncing.py`
- `Rhombicosidodecahedron/flythroughbouncing.py`

Simulations of bouncing balls with various physical properties.

**Example Usage:**
```bash
python -m manim -qh 3BouncingBalls/bouncing_balls.py BouncingBallsScene
```

### Radium Atom
**File:** `Scripts/radium_atom.py`

Visualization of the radium atom and its radioactive decay.

**Example Usage:**
```bash
python -m manim -qh Scripts/radium_atom.py RadiumAtomScene
```

## Neural Networks

### AlexNet
**File:** `AlexNet.py`

Visualization of the AlexNet convolutional neural network architecture.

**Example Usage:**
```bash
python -m manim -qh AlexNet.py AlexNetScene
```

### Native Sparse Attention
**Files:**
- `Scripts/NativeSparseAttention.py`
- `Scripts/NativeSparseAttention2.py`

Animations explaining sparse attention mechanisms in transformer models.

**Example Usage:**
```bash
python -m manim -qh Scripts/NativeSparseAttention.py SparseAttentionScene
```

## Financial Mathematics

### Option Skew
**File:** `optionskew.py`

Visualization of option price skew in financial markets.

**Example Usage:**
```bash
python -m manim -qh optionskew.py OptionSkewScene
```

## Spatial Reasoning Tests

### L-Shape 3D Rotation
**Files:**
- `SpatialReasoningTest/DeepSeek_LShape3D.py`
- `SpatialReasoningTest/OpenAIPro_LShape3D.py`

Animations testing spatial reasoning abilities with 3D rotations of L-shaped objects.

**Example Usage:**
```bash
python -m manim -qh SpatialReasoningTest/DeepSeek_LShape3D.py LShape3DScene
```

## Miscellaneous

### Cosmic Probability Scene
**File:** `Scripts/CosmicProbabilityScene.py`

A visualization of probability concepts in a cosmic setting.

**Example Usage:**
```bash
python -m manim -qh Scripts/CosmicProbabilityScene.py CosmicProbabilityScene
```

### Stickman Animation
**File:** `Scripts/stickman.py`

A simple stickman animation demonstrating basic Manim capabilities.

**Example Usage:**
```bash
python -m manim -qh Scripts/stickman.py StickmanScene
```

## Running Multiple Scenes

To run all scenes in a presentation format:

```bash
python run_presentation.py h
```

Where the parameter can be:
- `l` for low quality (fast)
- `m` for medium quality
- `h` for high quality
- `k` for 4K quality (very slow)

