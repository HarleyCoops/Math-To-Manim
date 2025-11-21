from manim import *
import random

class DakotaRLVisualization(Scene):
    def construct(self):
        # Color Palette - Earthy tones mixed with Data/Neon
        DAKOTA_RED = "#8B0000"
        SPIRIT_BLUE = "#40E0D0"
        GOLDEN_PLAINS = "#D4AF37"
        DEEP_DATA = "#1A1A2E"
        TEXT_COLOR = "#E0E0E0"

        self.camera.background_color = DEEP_DATA

        # ---------------------------------------------------------
        # PART 1: THE CORPUS INITIALIZATION (The Seven Council Fires)
        # ---------------------------------------------------------
        
        # Title
        title = Text("The Dakota Project: RL Gradient Definition", font_size=36, color=GOLDEN_PLAINS)
        subtitle = Text("1890 Grammar / 1497 Rules / 1860 Examples", font_size=24, color=GRAY)
        title.to_edge(UP)
        subtitle.next_to(title, DOWN)

        self.play(Write(title), FadeIn(subtitle))
        
        # Create the central nodes representing the Seven Council Fires (Oćéti šakowin)
        # acting as the central nodes of the Neural Network
        council_fires = VGroup()
        for i in range(7):
            fire = Dot(radius=0.15, color=DAKOTA_RED).set_glow_factor(2)
            fire.move_to(3 * RIGHT * np.cos(i * 2 * PI / 7) + 3 * UP * np.sin(i * 2 * PI / 7))
            council_fires.add(fire)
        
        council_fires.move_to(ORIGIN)
        
        # Connecting lines representing the structure of the language
        connections = VGroup()
        for i in range(7):
            for j in range(i + 1, 7):
                line = Line(council_fires[i].get_center(), council_fires[j].get_center(), stroke_width=0.5, stroke_opacity=0.3, color=SPIRIT_BLUE)
                connections.add(line)

        self.play(
            LaggedStart(*[GrowFromCenter(f) for f in council_fires], lag_ratio=0.1),
            Create(connections, run_time=3)
        )
        self.play(Rotate(council_fires, angle=PI, run_time=2), Rotate(connections, angle=PI, run_time=2))

        # ---------------------------------------------------------
        # PART 2: THE GRADIENT EQUATIONS (Morphology & Phonology)
        # ---------------------------------------------------------

        # Transition to specific rules visualization
        self.play(
            FadeOut(council_fires),
            FadeOut(connections),
            FadeOut(subtitle),
            title.animate.scale(0.7).to_corner(UL)
        )

        # Visualizing Rule ID: grammar_p1_r4 (Phonology)
        # "ć is an aspirate with the sound of English ch"
        
        rule_box = Rectangle(width=10, height=6, color=WHITE, stroke_width=1)
        
        # Mathematical metaphor for the rule
        t_phonology = MathTex(r"\mathcal{L}_{\text{phonology}} : \quad \text{c} \rightarrow \acute{c}", color=SPIRIT_BLUE, font_size=48)
        t_desc = Text("Aspirate Shift: Sound of 'ch' as in 'chin'", font_size=24, font="Monospace").next_to(t_phonology, DOWN)
        
        example_dak = Text("ćin", font_size=36, color=GOLDEN_PLAINS)
        example_eng = Text("(chin)", font_size=36, color=GRAY).next_to(example_dak, RIGHT)
        example_group = VGroup(example_dak, example_eng).next_to(t_desc, DOWN, buff=1)

        self.play(Write(t_phonology))
        self.play(FadeIn(t_desc))
        self.play(Write(example_group))
        self.wait(1)
        
        # Transition
        self.play(FadeOut(VGroup(t_phonology, t_desc, example_group)))

        # Visualizing Rule ID: grammar_p?_r1 (Syntax/Negation)
        # "Negation construction with 'šni'"
        
        # Equation metaphor: Loss function based on word order
        t_syntax = MathTex(
            r"\nabla \theta_{\text{syntax}} = \mathbb{E} [ \text{Verb} + \text{šni} ]", 
            color=DAKOTA_RED, font_size=48
        )
        t_rule_text = Text("Constraint: Negative particle follows the verb", font_size=24, font="Monospace").next_to(t_syntax, DOWN)
        
        # Animated flow of sentence structure
        box_verb = RoundedRectangle(width=2, height=1, corner_radius=0.2, color=BLUE)
        text_verb = Text("mde", font_size=24).move_to(box_verb) # "I go"
        
        box_neg = RoundedRectangle(width=2, height=1, corner_radius=0.2, color=RED)
        text_neg = Text("šni", font_size=24).move_to(box_neg) # "not"
        
        sentence_group = VGroup(VGroup(box_verb, text_verb), VGroup(box_neg, text_neg)).arrange(RIGHT, buff=0.5)
        sentence_group.next_to(t_rule_text, DOWN, buff=1)
        
        arrow = Arrow(start=LEFT, end=RIGHT, color=GRAY).next_to(sentence_group, DOWN)
        meaning = Text("I did not go", font_size=24, color=GRAY).next_to(arrow, DOWN)

        self.play(Write(t_syntax))
        self.play(FadeIn(t_rule_text))
        self.play(DrawBorderThenFill(box_verb), Write(text_verb))
        self.play(DrawBorderThenFill(box_neg), Write(text_neg))
        self.play(GrowArrow(arrow), Write(meaning))
        self.wait(1)

        # Transition
        self.play(FadeOut(VGroup(t_syntax, t_rule_text, sentence_group, arrow, meaning)))

        # ---------------------------------------------------------
        # PART 3: THE MANIFOLD OF CONJUGATION (Morphology)
        # ---------------------------------------------------------
        
        # Visualizing Rule: "First conjugation with pronouns inserted" (grammar_p20_r4)
        # Base: manop (to steal) -> ma-wa-nop (I steal)
        
        t_morph = Text("Morphological Embeddings: Infix Injection", font_size=32, color=SPIRIT_BLUE).to_edge(UP)
        self.play(Write(t_morph))

        base_word = Text("manóŋ", font_size=60) # to steal
        
        # Break the word apart
        part_1 = Text("ma", font_size=60)
        part_2 = Text("nóŋ", font_size=60)
        
        split_group = VGroup(part_1, part_2).arrange(RIGHT, buff=2)
        
        self.play(Transform(base_word, split_group))
        
        # The Infix (Gradient injection)
        infix = Text("wá", font_size=60, color=GOLDEN_PLAINS).move_to(split_group.get_center())
        infix_label = Text("1st Person Singular (I)", font_size=20, color=GOLDEN_PLAINS).next_to(infix, UP)
        
        arrow_down = Arrow(start=UP, end=DOWN, color=GOLDEN_PLAINS).next_to(infix, UP, buff=0.1)

        self.play(FadeIn(infix), FadeIn(infix_label), Create(arrow_down))
        self.wait(0.5)
        
        # Merge
        final_word = Text("mawánóŋ", font_size=60, color=WHITE)
        final_meaning = Text("I steal", font_size=30, color=GRAY).next_to(final_word, DOWN)
        
        self.play(
            ReplacementTransform(VGroup(part_1, infix, part_2), final_word),
            FadeOut(infix_label),
            FadeOut(arrow_down),
            FadeIn(final_meaning)
        )
        self.wait(1)
        
        self.play(FadeOut(VGroup(t_morph, final_word, final_meaning, base_word)))

        # ---------------------------------------------------------
        # PART 4: THE POETIC STRUCTURE (Complex Syntax)
        # ---------------------------------------------------------
        
        # Visualizing the "Substantive verb + descriptive element" (grammar_p53_r9)
        # "Verbs meaning 'to be' must be accompanied by descriptive elements"
        
        grid = NumberPlane(
            x_range=[-7, 7, 1],
            y_range=[-4, 4, 1],
            background_line_style={
                "stroke_color": TEAL,
                "stroke_width": 1,
                "stroke_opacity": 0.3
            }
        )
        
        self.play(Create(grid, run_time=2, lag_ratio=0.1))
        
        # Nodes in the semantic space
        node_loc = Dot(point=[-3, 1, 0], color=RED)
        label_loc = Text("ti mahen", font_size=24).next_to(node_loc, UP) # in the house
        
        node_verb = Dot(point=[3, -1, 0], color=BLUE)
        label_verb = Text("manka", font_size=24).next_to(node_verb, DOWN) # I am (sitting)
        
        line = Line(node_loc.get_center(), node_verb.get_center(), color=WHITE)
        
        formula = MathTex(r"S = \text{Locative}(\vec{x}) \oplus \text{Existential}(\vec{y})", font_size=36).to_edge(UP)
        
        self.play(
            FadeIn(node_loc), Write(label_loc),
            FadeIn(node_verb), Write(label_verb)
        )
        self.play(Create(line), Write(formula))
        
        translation = Text('"I am in the house"', font_size=36, color=GOLDEN_PLAINS).move_to(line.get_center()).shift(UP*0.5)
        self.play(Write(translation))
        
        self.wait(2)

        # ---------------------------------------------------------
        # PART 5: CONVERGENCE (Training Complete)
        # ---------------------------------------------------------
        
        self.play(
            FadeOut(grid), FadeOut(node_loc), FadeOut(label_loc), 
            FadeOut(node_verb), FadeOut(label_verb), FadeOut(line), 
            FadeOut(formula), FadeOut(translation), FadeOut(title)
        )
        
        # Final Spiral of Rules
        rules_text = [
            "Syntax: SOV", "Morphology: Agglutinative", 
            "Phonology: Guttural", "Demonstrative: Proximal/Distal",
            "Verbs: Stative/Active", "Particles: Enclitic"
        ]
        
        spiral_group = VGroup()
        for i, text in enumerate(rules_text):
            t = Text(text, font_size=24, color=random.choice([DAKOTA_RED, SPIRIT_BLUE, GOLDEN_PLAINS]))
            t.move_to(0.5 * i * RIGHT * np.cos(i) + 0.5 * i * UP * np.sin(i))
            spiral_group.add(t)
            
        self.play(SpinInFromNothing(spiral_group, run_time=3))
        
        final_statement = Text("Optimization Complete", font_size=48, font="Monospace", color=WHITE)
        sub_statement = Text("Dakota Language Model Initialized", font_size=24, color=GRAY).next_to(final_statement, DOWN)
        
        self.play(
            spiral_group.animate.scale(3).set_opacity(0),
            Write(final_statement),
            FadeIn(sub_statement)
        )
        
        self.wait(2)
        self.play(FadeOut(final_statement), FadeOut(sub_statement))