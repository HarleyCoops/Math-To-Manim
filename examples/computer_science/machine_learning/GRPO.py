from manim import *

class GRPOAnimation(Scene):
    def construct(self):
        self.show_all_scenes()
        
    def show_all_scenes(self):
        self.play(FadeIn(Text("Group Relative Policy Optimization", font_size=36)))
        self.wait(2)
        self.next_section("Traditional RL")
        self.traditional_rl()
        self.next_section("GRPO Reveal")
        self.grpo_breakthrough()
        self.next_section("Group Sampling")
        self.group_sampling()
        self.next_section("Advantage Calc")
        self.advantage_calculation()
        self.next_section("Objective Function")
        self.objective_function()
        self.next_section("Full Algorithm")
        self.full_algorithm()

    def traditional_rl(self):
        # Scene 1: Traditional RL Baseline
        policy = MathTex(r"\pi_\theta").scale(1.5).shift(LEFT*3)
        critic = MathTex(r"V_\phi").scale(1.5).shift(RIGHT*3)
        arrows = VGroup(
            CurvedArrow(policy.get_right(), critic.get_left(), angle=-TAU/4),
            CurvedArrow(critic.get_left(), policy.get_right(), angle=TAU/4)
        )
        cost_label = Text("High Training Costs", color=RED).shift(DOWN*2)
        
        self.play(LaggedStart(
            Write(policy),
            Write(critic),
            lag_ratio=0.3
        ))
        self.play(Create(arrows))
        self.play(Write(cost_label))
        self.wait(2)
        self.clear()

    def grpo_breakthrough(self):
        # Scene 2: GRPO Innovation
        old_setup = VGroup(
            MathTex(r"\pi_\theta"),
            MathTex(r"V_\phi")
        ).arrange(RIGHT, buff=2)
        
        new_setup = MathTex(r"\pi_\theta^{\text{GRPO}}").scale(1.5)
        savings = Text("60% Cost Reduction", color=GREEN)
        
        self.play(Write(old_setup))
        self.wait(1)
        self.play(
            Transform(old_setup, new_setup),
            Flash(old_setup[1], color=RED, line_length=0.3),
            run_time=2
        )
        self.play(Write(savings))
        self.wait(2)
        self.clear()

    def group_sampling(self):
        # Scene 3: Group Sampling Dynamics
        policy = MathTex(r"\pi_{\theta_{\text{old}}}").scale(1.5)
        group = VGroup(*[
            MathTex(f"o_{i}") for i in range(1,6)
        ]).arrange(RIGHT, buff=0.5).shift(DOWN*2)
        
        self.play(Write(policy))
        self.wait(1)
        for obj in group:
            arrow = Arrow(policy.get_bottom(), obj.get_top(), buff=0.2)
            self.play(
                GrowArrow(arrow),
                FadeIn(obj, shift=UP),
                run_time=0.5
            )
        self.wait(2)
        self.clear()

    def advantage_calculation(self):
        # Scene 4: Advantage Formula
        rewards = MathTex(
            r"\begin{cases} r_1 \\ r_2 \\ \vdots \\ r_G \end{cases}",
            font_size=36
        )
        mean = MathTex(r"\mu = \frac{1}{G}\sum_{i=1}^G r_i")
        std = MathTex(r"\sigma = \sqrt{\frac{1}{G}\sum_{i=1}^G (r_i - \mu)^2}")
        advantage = MathTex(
            r"A_i = \frac{r_i - \mu}{\sigma}",
            color=YELLOW
        ).scale(1.5)
        
        self.play(Write(rewards))
        self.wait(1)
        self.play(rewards.animate.to_edge(UP))
        self.play(Write(mean.next_to(rewards, DOWN)))
        self.wait(1)
        self.play(Write(std.next_to(mean, DOWN)))
        self.wait(1)
        self.play(
            TransformMatchingTex(
                VGroup(rewards, mean, std), 
                advantage
            )
        )
        self.wait(2)
        self.clear()

    def objective_function(self):
        # Scene 5: Objective Function
        main_eq = MathTex(
            r"\mathcal{J}_{GRPO}(\theta) = \mathbb{E}",
            r"\left[",
            r"\frac{1}{G}\sum_{i=1}^G",
            r"\left(",
            r"\min\left(",
            r"\frac{\pi_\theta}{\pi_{\text{old}}}A_i,",
            r"\text{clip}\left(",
            r"\frac{\pi_\theta}{\pi_{\text{old}}},",
            r"1-\varepsilon,1+\varepsilon",
            r"\right)A_i",
            r"\right)",
            r"- \beta\mathbb{D}_{KL}",
            r"\right)",
            r"\right]"
        ).scale(0.8)
        
        kl_div = MathTex(
            r"\mathbb{D}_{KL} = \frac{\pi_{ref}}{\pi_\theta}",
            r"- \log\frac{\pi_{ref}}{\pi_\theta} - 1",
            color=BLUE
        ).next_to(main_eq, DOWN)
        
        self.play(Write(main_eq))
        self.wait(2)
        self.play(Write(kl_div))
        self.wait(3)
        self.clear()

    def full_algorithm(self):
        # Scene 6: Full Algorithm
        full_eq = VGroup(
            MathTex(r"\mathcal{J}_{GRPO}(\theta) = "),
            MathTex(r"\mathbb{E}\left[q \sim P(Q),"),
            MathTex(r"\{o_i\}_{i=1}^G \sim \pi_{\theta_{old}}"),
            MathTex(r"\frac{1}{G}\sum_{i=1}^G"),
            MathTex(r"\min\left(\frac{\pi_\theta}{\pi_{\text{old}}}A_i,"),
            MathTex(r"\text{clip}(\cdots)A_i\right)"),
            MathTex(r"- \beta\mathbb{D}_{KL}\right]")
        ).arrange(DOWN, aligned_edge=LEFT).scale(0.8)
        
        self.play(LaggedStart(
            *[Write(part) for part in full_eq],
            lag_ratio=0.3
        ))
        self.wait(3)
        self.clear()

# Render command:
# manim -pql grpo_animation.py GRPOAnimation