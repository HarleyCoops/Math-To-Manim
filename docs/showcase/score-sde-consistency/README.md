# From Score SDEs to One-Step Consistency

A clean bimodal data distribution dissolves under continuous-time Brownian diffusion into a featureless Gaussian ridge. Yet hidden inside that noisy surface is a sky-blue compass—the score vector field $\nabla_x \log p_t(x)$—pointing back toward the data modes. Stripping out half the diffusion term transforms tangled reverse-time SDE paths into smooth, deterministic **Probability Flow ODE** streamlines that share the exact same marginal densities $p_t(x)$. And because every point along an ODE streamline lands on the same clean endpoint $x_\epsilon$, OpenAI's **Consistency Models** collapse the entire multi-step trajectory into a single one-step map $f_\theta(x_t, t) = x_\epsilon$.

[Full movie](../assets/score-sde-consistency.mp4) ·
[Preview GIF](../assets/score-sde-consistency.gif) ·
[Contact sheet](../assets/score-sde-consistency-contact-sheet.png) ·
[Manim source](../../../examples/argon/score_sde_consistency.py) ·
[Production request](../../prompts/score-sde-consistency.md)

## The argument, act by act

| Act | What the viewer sees | The mathematical claim |
|---|---|---|
| 1 | Two sharp coral peaks at $t = \epsilon = 0.002$ ($x = \pm 2.0, \sigma_0 = 0.35$) extrude across time into a 3D olive density surface $p_t(x)$ while eight Brownian sample paths wander into the Gaussian bell at $t = 2.5$. | Under the Karras/VE forward SDE $\mathrm{d}x = \sqrt{2t}\,\mathrm{d}w_t$, the marginal density is the exact Gaussian convolution $p_t(x) = \frac{1}{2}\mathcal{N}(-\mu_0, \sigma_0^2+t^2) + \frac{1}{2}\mathcal{N}(+\mu_0, \sigma_0^2+t^2)$, whose bimodal peaks merge at $t^* = \sqrt{\mu_0^2-\sigma_0^2} = 1.9691$. |
| 2 | Sky-blue score arrows $\nabla_x \log p_t(x)$ emerge across the $(x, t)$ floor, vanishing along the golden watershed $x = 0$ and curving toward $x = \pm 2.0$, followed by Tweedie denoiser arcs. | $\nabla_x \log p_t(x) = \frac{\mu_0 \tanh(\mu_0 x / (\sigma_0^2+t^2)) - x}{\sigma_0^2+t^2}$ points uphill toward higher density; Tweedie's formula $D(x,t) = x + t^2\nabla_x \log p_t(x)$ gives $\mathbb{E}[x_0 \mid x_t]$. |
| 3 | Eight jittery coral Reverse-SDE trajectories march backward from $t = 2.5$ to $t = \epsilon$, then morph into sleek golden-blue deterministic streamlines gliding over the 3D surface $p_t(x)$. | By the Fokker-Planck identity $\frac{1}{2}g(t)^2\Delta p_t = \nabla\cdot(\frac{1}{2}g(t)^2 p_t \nabla_x \log p_t)$, the deterministic **Probability Flow ODE** $\frac{\mathrm{d}x}{\mathrm{d}t} = -t\,\nabla_x \log p_t(x)$ shares the exact same marginals $p_t(x)$ as the SDE (Song et al., 2021). |
| 4 | **The Big Zoom:** the camera dives into the hero ODE streamline starting at $x_T = +2.30$; three markers at $t = 2.20, 1.25, 0.50$ fire simultaneous gold arcs onto the exact same endpoint $x_\epsilon = +2.04$, while a diagnostic card plots $c_{\text{skip}}(t)$ and $c_{\text{out}}(t)$. | A **Consistency Model** (Song, Dhariwal, Chen, & Sutskever, OpenAI 2023) obeys self-consistency $f_\theta(x_t, t) = f_\theta(x_{t'}, t') = x_\epsilon$ along every ODE trajectory, with boundary condition $f_\theta(x, \epsilon) = x$ enforced via $f_\theta(x,t) = c_{\text{skip}}(t)x + c_{\text{out}}(t)F_\theta(x,t)$. |
| 5 | All eight prior samples at $t = 2.5$ leap in a single golden evaluation ($NFE = 1$) across the 3D density surface onto the clean bimodal peaks at $t = \epsilon$, closing with an orbital panorama. | Learning the global flow map of the Probability Flow ODE collapses 50 sequential solver evaluations into a single consistency evaluation. |

Every identity and number shown on screen is verified in [`tests/test_score_sde_consistency.py`](../../../tests/test_score_sde_consistency.py) and [`tests/test_argon.py`](../../../tests/test_argon.py).

## How it was made

This film was produced by the **Argon Google Agent SDK (`google-adk` + `google-genai`) six-agent reasoning chain** ([`argon/`](../../../argon/)) operated with **Gemini 4 Argon** via [`scripts/operate_argon_chain.py`](../../../scripts/operate_argon_chain.py):

| Stage | ADK Agent | Artifact |
|---|---|---|
| 1 Intent | `argon_intent` (`LlmAgent`) | [01_intent.json](01_intent.json) |
| 2 Cartographer | `argon_cartographer` (`LlmAgent`) | [02_knowledge_map.json](02_knowledge_map.json) |
| 3 Curriculum | `argon_curriculum` (`LlmAgent`) | [03_curriculum.json](03_curriculum.json) |
| 4 Math Director | `argon_math_director` (`LlmAgent` + `execute_math_check`) | [04_math_dossier.json](04_math_dossier.json) |
| 5 Cinematographer | `argon_cinematographer` (`LlmAgent`) | [05_shot_list.json](05_shot_list.json) |
| 6 Composer | `argon_composer` (`LlmAgent` + `verify_scene`) | [06_scene_spec.json](06_scene_spec.json) & [argon_scene.py](argon_scene.py) |
