from manim import *

class GRPOArtisticExplanationOnly(Scene):
    def construct(self):
        self.camera.background_color = "#001219"
        
        # Title Slide
        title = Text("Group Relative Policy Optimization", font_size=48, color=WHITE)
        self.play(FadeIn(title), run_time=1.5)
        self.wait(2)
        self.play(FadeOut(title))
        
        # Expectation term with explanation
        expectation = MathTex(
            r"\mathcal{J}_{GRPO}(\theta) = \mathbb{E}",
            r"\left[ q \sim P(Q), \{o_i\} \sim \pi_{\theta_{\text{old}}} \right]",
            font_size=36
        )
        self.play(Write(expectation), run_time=2)
        self.wait(1)
        
        self.play(expectation.animate.move_to(UP*3))
        exp_explanation = Text(
            "Core expectation operator:\n"
            "- Samples questions from distribution P(Q)\n"
            "- Uses current policy for responses\n"
            "- Averages across all possibilities",
            font_size=24,
            line_spacing=1.2
        ).next_to(expectation, DOWN, buff=0.5)
        self.play(FadeIn(exp_explanation))
        self.wait(3)
        self.play(FadeOut(expectation), FadeOut(exp_explanation))

        # Policy ratio component
        policy_ratio = MathTex(
            r"\frac{1}{G}\sum_{i=1}^G \min\left(",
            r"\frac{\pi_\theta}{\pi_{\text{old}}}A_i,",
            r"\text{clip}\left(\frac{\pi_\theta}{\pi_{\text{old}}}, 1-\epsilon,1+\epsilon\right)A_i",
            r"\right)",
            font_size=36
        )
        self.play(Write(policy_ratio), run_time=3)
        self.wait(1)
        
        self.play(policy_ratio.animate.move_to(UP*3))
        ratio_explanation = Text(
            "Policy update mechanism:\n"
            "- Compares new/old policy probabilities\n"
            "- ε-clipping (typically 0.2) prevents large jumps\n"
            "- Group average (G responses) maintains stability",
            font_size=24,
            line_spacing=1.2
        ).next_to(policy_ratio, DOWN, buff=0.5)
        self.play(FadeIn(ratio_explanation))
        self.wait(3)
        self.play(FadeOut(policy_ratio), FadeOut(ratio_explanation))

        # KL Regularization term
        kl_term = MathTex(
            r"- \beta\left(",
            r"\frac{\pi_{\text{ref}}}{\pi_\theta} - \log\frac{\pi_{\text{ref}}}{\pi_\theta} - 1",
            r"\right)",
            font_size=36
        )
        self.play(Write(kl_term), run_time=2)
        self.wait(1)
        
        self.play(kl_term.animate.move_to(UP*3))
        kl_explanation = Text(
            "Stability preservation:\n"
            "- Keeps policy near reference (π_ref)\n"
            "- β controls constraint strength\n"
            "- Modified KL avoids over-constraint",
            font_size=24,
            line_spacing=1.2
        ).next_to(kl_term, DOWN, buff=0.5)
        self.play(FadeIn(kl_explanation))
        self.wait(3)
        self.play(FadeOut(kl_term), FadeOut(kl_explanation))

        # Advantage calculation
        advantage_eq = MathTex(
            r"A_i = \frac{r_i - \mu_r}{\sigma_r}",
            font_size=36
        )
        self.play(Write(advantage_eq), run_time=2)
        self.wait(1)
        
        self.play(advantage_eq.animate.move_to(UP*3))
        adv_explanation = Text(
            "Group-normalized advantages:\n"
            "- μ_r: Batch reward mean\n"
            "- σ_r: Reward standard deviation\n"
            "- Eliminates need for value network",
            font_size=24,
            line_spacing=1.2
        ).next_to(advantage_eq, DOWN, buff=0.5)
        self.play(FadeIn(adv_explanation))
        self.wait(3)
        self.play(FadeOut(advantage_eq), FadeOut(adv_explanation))

        # Final synthesis of all components
        expectation = MathTex(
            r"\mathcal{J}_{GRPO}(\theta) = \mathbb{E}",
            r"\left[ q \sim P(Q), \{o_i\} \sim \pi_{\theta_{\text{old}}} \right]",
            font_size=36
        )
        policy_ratio = MathTex(
            r"\frac{1}{G}\sum_{i=1}^G \min\left(",
            r"\frac{\pi_\theta}{\pi_{\text{old}}}A_i,",
            r"\text{clip}\left(\frac{\pi_\theta}{\pi_{\text{old}}}, 1-\epsilon,1+\epsilon\right)A_i",
            r"\right)",
            font_size=36
        )
        kl_term = MathTex(
            r"- \beta\left(",
            r"\frac{\pi_{\text{ref}}}{\pi_\theta} - \log\frac{\pi_{\text{ref}}}{\pi_\theta} - 1",
            r"\right)",
            font_size=36
        )
        
        full_eq = VGroup(expectation, policy_ratio, kl_term).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        self.play(
            LaggedStart(
                FadeIn(expectation, shift=UP),
                FadeIn(policy_ratio, shift=RIGHT),
                FadeIn(kl_term, shift=LEFT),
                lag_ratio=0.3
            ),
            run_time=3
        )
        self.wait(4)
        self.play(FadeOut(full_eq))