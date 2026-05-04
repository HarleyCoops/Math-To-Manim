from manim import *
from manim.mobject.geometry.tips import ArrowTriangleFilledTip
from manim.mobject.types.vectorized_mobject import VGroup
from manim.mobject.geometry.line import Line
from manim.mobject.geometry.arc import Circle
from manim.mobject.text.tex_mobject import Tex, MathTex
from manim.mobject.geometry.line import DashedLine
from manim.mobject.geometry.line import Arrow

# We can create DashedArrow as a combination of DashedLine and Arrow
class DashedArrow(DashedLine):
    def __init__(self, start, end, color=WHITE, buff=0.2, **kwargs):
        # Remove tip_shape from kwargs if it exists
        kwargs.pop('tip_shape', None)
        super().__init__(start, end, color=color, buff=buff, **kwargs)
        tip = ArrowTriangleFilledTip()
        tip.move_to(self.get_end())
        tip.rotate(self.get_angle())
        tip.set_color(self.get_color())
        self.add(tip)

class NeuralNetworkMobject(VGroup):
    def __init__(
        self,
        layer_sizes,
        neuron_radius=0.15,
        layer_labels=None,
        neuron_stroke_color=WHITE,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.layer_sizes = layer_sizes
        self.neuron_radius = neuron_radius
        self.layer_labels = layer_labels or []
        self.neuron_stroke_color = neuron_stroke_color
        
        self.layers = VGroup()
        self.edges = VGroup()
        self.output_layer = None
        
        self._create_layers()
        self._connect_layers()
        self._add_labels()
        
    def _create_layers(self):
        for i, size in enumerate(self.layer_sizes):
            layer = VGroup()
            y_positions = np.linspace(-(size-1)/2, (size-1)/2, size)
            for y_pos in y_positions:
                neuron = Circle(
                    radius=self.neuron_radius,
                    stroke_color=self.neuron_stroke_color
                )
                neuron.move_to([i*2, y_pos, 0])
                layer.add(neuron)
            self.layers.add(layer)
            if i == len(self.layer_sizes) - 1:
                self.output_layer = layer
        self.add(self.layers)
        
    def _connect_layers(self):
        for i in range(len(self.layers)-1):
            current_layer = self.layers[i]
            next_layer = self.layers[i+1]
            for n1 in current_layer:
                for n2 in next_layer:
                    edge = Line(
                        n1.get_center(),
                        n2.get_center(),
                        stroke_opacity=0.5
                    )
                    self.edges.add(edge)
        self.add(self.edges)
        
    def _add_labels(self):
        if not self.layer_labels:
            return
        for i, label in enumerate(self.layer_labels[:len(self.layers)]):
            tex = Tex(label).next_to(self.layers[i], DOWN)
            self.add(tex)

class ProLIPScene(Scene):
    def construct(self):
        # Set the aspect ratio to 16:9 and adjust frame size
        config.frame_width = 16
        config.frame_height = 9
        config.pixel_width = 1920
        config.pixel_height = 1080
        
        self.camera.background_color = "#1e1e1e"
        
        # 1. Visual and Textual Encoders
        visual_encoder = NeuralNetworkMobject(
            [3, 6, 6, 4],
            neuron_radius=0.15,
            layer_labels=["Image", "CNN", "ResNet", r"$\mathbf{v}$"],
            neuron_stroke_color=BLUE,
        ).scale(0.5).to_edge(LEFT, buff=1.5).shift(UP*0.5)
        
        text_encoder = NeuralNetworkMobject(
            [3, 6, 6, 4],
            neuron_radius=0.15,
            layer_labels=["Text", "BERT", "Transformer", r"$\mathbf{t}$"],
            neuron_stroke_color=GREEN,
        ).scale(0.5).shift(RIGHT*0.5 + UP*0.5)
        
        self.play(
            LaggedStart(
                Create(visual_encoder),
                Create(text_encoder),
                lag_ratio=0.5
            ), 
            run_time=4
        )
        self.wait(1)

        # 2. [CLS] and [UNC] Tokens
        cls_token = Tex("[CLS]", color=GOLD).next_to(visual_encoder.output_layer, UP)
        unc_token = Tex("[UNC]", color=LIGHT_GRAY).next_to(text_encoder.output_layer, UP)
        mu_eq = MathTex(r"\mu_v, \log \sigma_v^2", color=GOLD).next_to(cls_token, UP)
        logsigma_eq = MathTex(r"\mu_t, \log \sigma_t^2", color=LIGHT_GRAY).next_to(unc_token, UP)
        
        self.play(
            FadeIn(cls_token, unc_token),
            Write(mu_eq), 
            Write(logsigma_eq),
            run_time=2
        )
        self.wait(1)

        # 3. Probabilistic Contrastive Loss (Eq. 2)
        positive_arrow = Arrow(
            visual_encoder.output_layer.get_right(),
            text_encoder.output_layer.get_left(),
            color=GREEN,
            tip_shape=ArrowTriangleFilledTip,
            buff=0.2
        )
        negative_arrows = VGroup(*[
            Arrow(
                visual_encoder.output_layer.get_right(),
                text_encoder.output_layer.get_left(),
                color=RED,
                tip_shape=ArrowTriangleFilledTip,
                buff=0.2
            ).shift(DOWN*i*0.3) for i in range(1,3)
        ])
        contrastive_formula = MathTex(
            r"\mathcal{L}_{\text{contrast}} = -\log \frac{e^{s(\mathbf{v}_i,\mathbf{t}_i)/\tau}}{\sum_j e^{s(\mathbf{v}_i,\mathbf{t}_j)/\tau}}"
        ).scale(0.8).to_edge(DOWN, buff=1.5)
        
        self.play(
            GrowArrow(positive_arrow),
            LaggedStart(*[GrowArrow(a) for a in negative_arrows], lag_ratio=0.3),
            Write(contrastive_formula),
            run_time=3
        )
        self.wait(2)

        # Clean up before next section
        self.play(
            FadeOut(positive_arrow),
            FadeOut(negative_arrows),
            FadeOut(cls_token),
            FadeOut(unc_token),
            FadeOut(mu_eq),
            FadeOut(logsigma_eq),
            run_time=1
        )

        # 4. Inclusion Loss (Eq. 5)
        projection_arrow = DashedArrow(
            text_encoder.output_layer.get_left(),
            visual_encoder.output_layer.get_right(),
            color=BLUE_B,
            buff=0.2
        )
        inclusion_formula = MathTex(
            r"\mathcal{L}_{\text{inclusion}} = \mathbb{E}_{t \sim T}[\| \mathbf{t} - \text{Proj}_V(\mathbf{t}) \|_2]"
        ).scale(0.8).next_to(contrastive_formula, UP, buff=0.5)
        
        self.play(
            Transform(contrastive_formula, inclusion_formula),
            Create(projection_arrow),
            run_time=2
        )
        self.wait(2)

        # Clean up before variance visualization
        self.play(
            FadeOut(projection_arrow),
            FadeOut(contrastive_formula),
            run_time=1
        )

        # 5. Variance Visualization
        gaussian_group = VGroup()
        for i, color in enumerate([GOLD, LIGHT_GRAY]):
            graph = FunctionGraph(
                lambda x: np.exp(-x**2/0.5)*(1-i*0.2),
                x_range=[-3,3],
                color=color
            ).scale(0.5).shift(DOWN + LEFT*(2 - i*4))
            gaussian_group.add(graph)
            var_label = MathTex(r"\log \sigma^2").next_to(graph, UP).set_color(color)
            gaussian_group.add(var_label)
        
        self.play(
            Create(gaussian_group),
            run_time=3
        )
        self.wait(1)

        # Clean up before L2 constraint
        self.play(FadeOut(gaussian_group), run_time=1)

        # 6. L2-Norm Constraint
        l2_sphere = Circle(radius=1.5, color=BLUE_E, stroke_width=3).move_to(ORIGIN)
        l2_formula = MathTex(r"\|\mathbf{v}\|_2 \leq \gamma").scale(0.8).next_to(l2_sphere, DOWN)
        
        embed_points = VGroup(*[
            Dot(point, color=WHITE).scale(0.5) 
            for point in [l2_sphere.point_from_proportion(0.2), 
                         l2_sphere.point_from_proportion(0.5), 
                         l2_sphere.point_from_proportion(0.8)]
        ])
        
        self.play(
            Create(l2_sphere),
            Write(l2_formula),
            LaggedStart(*[GrowFromCenter(p) for p in embed_points], lag_ratio=0.2),
            run_time=3
        )
        self.wait(2)

        # Final Cleanup
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=2
        )
