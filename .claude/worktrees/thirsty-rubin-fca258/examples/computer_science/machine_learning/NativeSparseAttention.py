from manim import *
import numpy as np
import math
# Scene 1: Introduction to vanilla self-attention and its complexity
class Scene1_Introduction(Scene):
    def construct(self):
        # Title text
        title = Text("Vanilla Self-Attention", font_size=48)
        title.to_edge(UP)
        # Attention formula with colored Q, K, V
        formula = MathTex(r"\text{Attention}(Q, K, V) = \text{softmax}\!\Big(\frac{QK^T}{\sqrt{d_k}}\Big)\,V",
                          font_size=36)
        formula.set_color_by_tex("Q", BLUE)   # Q in blue
        formula.set_color_by_tex("K", RED)    # K in red
        formula.set_color_by_tex("V", GREEN)  # V in green
        formula.next_to(title, DOWN)
        # Token representations (as small dots or circles)
        tokens = VGroup(*[Dot(radius=0.08) for _ in range(6)]).arrange(RIGHT, buff=0.6)
        tokens.set_color(GRAY)
        tokens.shift(DOWN*1.0)
        # Highlight one token as the query in blue
        query_token = tokens[2]
        query_token.set_color(BLUE)
        # Draw arrows from query token to all other tokens (fully connected attention)
        arrows = VGroup()
        for j, token in enumerate(tokens):
            if token != query_token:
                # Arrow from query_token to token
                arrow = Arrow(query_token.get_center(), token.get_center(), buff=0.1, stroke_width=2)
                arrow.set_color(YELLOW)  # use a neutral highlight for attention links
                arrows.add(arrow)
        # Complexity text
        complexity = Text("Interactions: $n \\times n$ (quadratic)", font_size=30)
        complexity.next_to(tokens, DOWN*1.5)
        complexity.set_color(WHITE)
        
        # Animate: title, formula, tokens, attention connections, and complexity note
        self.play(FadeIn(title), Write(formula))
        self.play(FadeIn(tokens))
        self.play(AnimationGroup(*[GrowArrow(arr) for arr in arrows], lag_ratio=0.1))
        self.play(FadeIn(complexity))
        # Emphasize quadratic complexity (e.g., highlight the text)
        self.play(Indicate(complexity, scale_factor=1.1, color=RED))
        # Hold briefly, then fade out everything to transition
        self.play(FadeOut(title), FadeOut(formula), FadeOut(tokens), FadeOut(arrows), FadeOut(complexity))


# Scene 2: Detailed breakdown of Query, Key, and Value roles in attention
class Scene2_QKVBreakdown(Scene):
    def construct(self):
        # Single token representation
        token = Dot(radius=0.1, color=WHITE)
        token_label = Text("Token", font_size=30).next_to(token, DOWN, buff=0.2)
        token_group = VGroup(token, token_label)
        token_group.shift(LEFT*3)
        # Q, K, V vector representations as small colored arrows or lines
        Q_vec = Arrow(token.get_right(), token.get_right() + RIGHT*1.5, buff=0, stroke_width=5, color=BLUE)
        K_vec = Arrow(token.get_right(), token.get_right() + RIGHT*1.5, buff=0, stroke_width=5, color=RED)
        V_vec = Arrow(token.get_right(), token.get_right() + RIGHT*1.5, buff=0, stroke_width=5, color=GREEN)
        # Position Q, K, V arrows at slight offsets (stack them vertically)
        Q_vec.shift(UP*0.6)
        V_vec.shift(DOWN*0.6)
        # Labels for Q, K, V
        Q_label = Text("Q (query)", color=BLUE, font_size=28).next_to(Q_vec, UP*0.5)
        K_label = Text("K (key)", color=RED, font_size=28).next_to(K_vec, DOWN*0.5)
        V_label = Text("V (value)", color=GREEN, font_size=28).next_to(V_vec, DOWN*0.5)
        # Group Q, K, V vectors and labels
        qkv_group = VGroup(Q_vec, K_vec, V_vec, Q_label, K_label, V_label)
        qkv_group.shift(RIGHT*0.5)
        # Duplicates of key and value vectors to represent other tokens' K and V
        other_keys = VGroup(*[Circle(radius=0.1, color=RED, fill_opacity=1) for _ in range(3)]).arrange(DOWN, buff=0.4)
        other_vals = VGroup(*[Circle(radius=0.1, color=GREEN, fill_opacity=1) for _ in range(3)]).arrange(DOWN, buff=0.4)
        other_kv = VGroup(other_keys, other_vals).arrange(RIGHT, buff=1).to_edge(RIGHT, buff=2)
        # Labels for other tokens' keys and values
        ok_label = Text("Other Keys", font_size=24, color=RED).next_to(other_keys, UP, buff=0.2)
        ov_label = Text("Other Values", font_size=24, color=GREEN).next_to(other_vals, UP, buff=0.2)
        # Arrow from our token's Q to each other key (dot product computation)
        connectors = VGroup()
        for ok in other_keys:
            conn = Arrow(Q_vec.get_end(), ok.get_left(), buff=0.1, stroke_width=2, color=YELLOW)
            connectors.add(conn)
        # Example attention weight text near one connector
        weight_text = MathTex("w = Q\\cdot K", font_size=30).next_to(connectors[1], UP, buff=0.1)
        weight_text.set_color(YELLOW)
        # Arrow from one of the values to an output (demonstrate weighted sum)
        output_circle = Circle(radius=0.12, color=GREEN, fill_opacity=0.8).to_edge(RIGHT, buff=0.5)
        output_label = Text("Weighted sum of Values", font_size=24).next_to(output_circle, DOWN)
        apply_arrow = Arrow(other_vals[1].get_right(), output_circle.get_left(), buff=0.1, stroke_width=4, color=GREEN)
        
        # Animate token and its Q,K,V vectors
        self.play(FadeIn(token_group))
        self.play(GrowArrow(Q_vec), FadeIn(Q_label))
        self.play(GrowArrow(K_vec), FadeIn(K_label))
        self.play(GrowArrow(V_vec), FadeIn(V_label))
        # Show other tokens' K and V and connect query to keys
        self.play(FadeIn(other_keys, ok_label), FadeIn(other_vals, ov_label))
        self.play(*[GrowArrow(conn) for conn in connectors])
        self.play(FadeIn(weight_text))
        # Apply weight to a value (illustrative single weight * value to output)
        self.play(GrowArrow(apply_arrow))
        self.play(FadeIn(output_circle), FadeIn(output_label))
        # Brief pause, then fade out everything
        self.wait(0.5)
        self.play(*[FadeOut(mob) for mob in [token_group, qkv_group, other_kv, ok_label, ov_label, connectors, weight_text, apply_arrow, output_circle, output_label]])
# Scene 3: Highlight the quadratic complexity issue for long sequences
class Scene3_ComplexityProblem(Scene):
    def construct(self):
        # Text illustrating scaling problem
        problem_text = Text("Long Sequence = Explosive Attention Cost", font_size=40)
        problem_text.to_edge(UP)
        # Example: n = 1000, interactions = 1,000,000
        example_text = Text("e.g.,  n = 1000 tokens  ->  1000 x 1000 = 1,000,000 interactions", font_size=30)
        example_text.next_to(problem_text, DOWN, buff=0.5)
        example_text.set_color(RED)
        # Represent attention matrix growth (small -> large)
        small_matrix = Integer(16)  # just showing a number of interactions or a small grid
        small_matrix_text = Text("4x4 = 16", font_size=24).next_to(small_matrix, DOWN, buff=0.1)
        small_matrix_group = VGroup(small_matrix, small_matrix_text).move_to(LEFT*3 + DOWN*1)
        big_matrix = Integer(1000000)
        big_matrix_text = Text("1000x1000 = 1,000,000", font_size=24).next_to(big_matrix, DOWN, buff=0.1)
        big_matrix_group = VGroup(big_matrix, big_matrix_text).move_to(RIGHT*3 + DOWN*1)
        # Arrows pointing from small to big to show growth
        arrow_growth = Arrow(small_matrix_group.get_right(), big_matrix_group.get_left(), buff=0.5, color=YELLOW)
        growth_label = Text("n\u2191 => n^2\u2191\u2191", font_size=30, color=YELLOW).next_to(arrow_growth, UP)
        
        # Animate the explanation of scaling
        self.play(Write(problem_text))
        self.play(FadeIn(example_text))
        self.play(FadeIn(small_matrix_group))
        self.play(GrowArrow(arrow_growth), FadeIn(growth_label))
        self.play(FadeIn(big_matrix_group))
        # Emphasize the large number in red
        self.play(Indicate(big_matrix, scale_factor=1.2, color=RED))
        self.wait(0.5)
        # Fade out all elements
        self.play(FadeOut(problem_text), FadeOut(example_text), FadeOut(small_matrix_group),
                  FadeOut(big_matrix_group), FadeOut(arrow_growth), FadeOut(growth_label))
# Scene 4: Overview of the optimized attention mechanism (key ideas)
class Scene4_OptimizedOverview(Scene):
    def construct(self):
        title = Text("Optimized Attention: Key Ideas", font_size=44)
        title.to_edge(UP)
        idea1 = Text("1. Sliding Window (local neighbors)", font_size=32, color=BLUE)
        idea2 = Text("2. Compression (summarize segments)", font_size=32, color=RED)
        idea3 = Text("3. Selection (important tokens)", font_size=32, color=YELLOW)
        ideas = VGroup(idea1, idea2, idea3).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        ideas.next_to(title, DOWN, buff=0.8).align_to(title, LEFT)
        # Small subtext for each idea (optional for clarity)
        sub1 = Text("Limit attention to a fixed window [linear complexity]&#8203;:contentReference[oaicite:10]{index=10}", font_size=24, color=BLUE).next_to(idea1, RIGHT, buff=0.3)
        sub2 = Text("Compress long-range context [LongT5 blocks]&#8203;:contentReference[oaicite:11]{index=11}", font_size=24, color=RED).next_to(idea2, RIGHT, buff=0.3)
        sub3 = Text("Attend to key tokens globally [Longformer]&#8203;:contentReference[oaicite:12]{index=12}", font_size=24, color=YELLOW).next_to(idea3, RIGHT, buff=0.3)
        subs = VGroup(sub1, sub2, sub3)
        
        # Animate the ideas one by one
        self.play(FadeIn(title))
        self.play(FadeIn(idea1))
        self.play(FadeIn(sub1))
        self.play(FadeIn(idea2))
        self.play(FadeIn(sub2))
        self.play(FadeIn(idea3))
        self.play(FadeIn(sub3))
        self.wait(1)
        # Fade out overview text
        self.play(FadeOut(title), FadeOut(ideas), FadeOut(subs))
# Scene 5: Sliding window attention for local context
class Scene5_SlidingWindow(Scene):
    def construct(self):
        title = Text("Sliding Window Attention (Local)", font_size=40, color=BLUE).to_edge(UP)
        # Create a row of tokens (e.g., 12 tokens)
        n = 12
        tokens = VGroup(*[Square(side_length=0.3, fill_opacity=1) for _ in range(n)]).arrange(RIGHT, buff=0.2)
        tokens.set_fill(GRAY)
        tokens.set_color(WHITE)
        tokens.to_edge(DOWN, buff=1.5)
        # Define window size (e.g., 2 on each side)
        w = 2
        # Initial query index to highlight
        query_index = 6
        query_square = tokens[query_index]
        # Highlight query and its window neighbors
        window_indices = list(range(max(0, query_index - w), min(n, query_index + w + 1)))
        # Create a highlight rectangle around the window region
        left_idx, right_idx = window_indices[0], window_indices[-1]
        window_rect = SurroundingRectangle(VGroup(*tokens[left_idx:right_idx+1]), color=BLUE, buff=0.05)
        window_rect.set_fill(color=BLUE, opacity=0.1)
        # Mark the query token in blue
        query_marker = SurroundingRectangle(query_square, color=BLUE, buff=0.0)
        query_marker.set_fill(color=BLUE, opacity=0.2)
        # Arrows from query to each token in window (except itself)
        arrows = VGroup()
        for j in window_indices:
            if j == query_index:
                continue
            arrow = Arrow(query_square.get_top(), tokens[j].get_top(), buff=0.2, stroke_width=3, color=BLUE)
            arrows.add(arrow)
        # Complexity text
        complexity_note = Text("Local attention: O(n \u00d7 w)", font_size=30, color=BLUE)
        complexity_note.next_to(tokens, UP, buff=0.5)
        
        # Animate sliding window for one token
        self.play(FadeIn(title))
        self.play(FadeIn(tokens))
        self.play(Create(window_rect), FadeIn(query_marker))
        self.play(*[GrowArrow(arr) for arr in arrows])
        self.play(FadeIn(complexity_note))
        # Slide the window to another query (move highlight and arrows)
        for new_index in [7, 8]:
            new_window_indices = list(range(max(0, new_index - w), min(n, new_index + w + 1)))
            new_left, new_right = new_window_indices[0], new_window_indices[-1]
            # Animate the window rectangle shifting
            new_rect = SurroundingRectangle(VGroup(*tokens[new_left:new_right+1]), color=BLUE, buff=0.05)
            new_rect.set_fill(color=BLUE, opacity=0.1)
            new_query_marker = SurroundingRectangle(tokens[new_index], color=BLUE, buff=0.0)
            new_query_marker.set_fill(color=BLUE, opacity=0.2)
            # Update arrows for new query
            new_arrows = VGroup()
            for j in new_window_indices:
                if j == new_index: continue
                new_arrow = Arrow(tokens[new_index].get_top(), tokens[j].get_top(), buff=0.2, stroke_width=3, color=BLUE)
                new_arrows.add(new_arrow)
            # Transition animations
            self.play(Transform(window_rect, new_rect), Transform(query_marker, new_query_marker))
            # Remove old arrows, show new arrows
            self.play(FadeOut(arrows), *[GrowArrow(na) for na in new_arrows])
            arrows = new_arrows
            # Short wait to illustrate the slide
            self.wait(0.3)
        # Fade out everything
        self.play(FadeOut(title), FadeOut(tokens), FadeOut(window_rect), FadeOut(query_marker),
                  FadeOut(arrows), FadeOut(complexity_note))
# Scene 6: Compression of distant tokens into summary representations
class Scene6_Compression(Scene):
    def construct(self):
        title = Text("Compression: Summarize Distant Tokens", font_size=40, color=RED).to_edge(UP)
        # Sequence of tokens (e.g., 12 tokens as before)
        n = 12
        tokens = VGroup(*[Square(side_length=0.3, fill_opacity=1) for _ in range(n)]).arrange(RIGHT, buff=0.2)
        tokens.set_fill(GRAY)
        tokens.set_color(WHITE)
        tokens.to_edge(DOWN, buff=1.8)
        # Segment the sequence into blocks (e.g., 3 tokens per block)
        block_size = 3
        num_blocks = math.ceil(n / block_size)
        summary_tokens = VGroup()
        braces = VGroup()
        brace_texts = VGroup()
        for b in range(num_blocks):
            start = b * block_size
            end = min(n, (b+1) * block_size) - 1
            block_group = VGroup(*tokens[start:end+1])
            # Create brace for this block
            brace = Brace(block_group, UP, buff=0.1, color=RED)
            brace_text = Text("Compress", font_size=24, color=RED).next_to(brace, UP, buff=0.1)
            braces.add(brace)
            brace_texts.add(brace_text)
            # Summary token (purple circle or square) representing this block
            summary = Circle(radius=0.15, color=RED, fill_opacity=1)
            # Place summary token above the block (aligned to block center)
            summary.move_to(brace.get_center() + UP*0.6)
            summary_tokens.add(summary)
        # Animate the initial sequence and first block compression step
        self.play(FadeIn(title))
        self.play(FadeIn(tokens))
        # Focus on first block compression as example
        if len(braces) > 0:
            self.play(braces[0].animate.set_color(RED), FadeIn(brace_texts[0]))
            self.play(GrowFromCenter(summary_tokens[0]))  # create first summary token
            # Fade out brace after creating summary
            self.play(FadeOut(braces[0]), FadeOut(brace_texts[0]))
        # Quickly generate the remaining summary tokens
        if num_blocks > 1:
            # Show the rest of summaries appearing (without individual braces for brevity)
            self.play(*[GrowFromCenter(summary_tokens[i]) for i in range(1, num_blocks)])
        # All summary tokens now represent the blocks
        summary_label = Text("Summaries", font_size=30, color=RED).next_to(summary_tokens, UP, buff=0.5)
        self.play(FadeIn(summary_label))
        self.wait(1)
        # Fade out original tokens and keep summaries (to imply compression of detail)
        self.play(FadeOut(tokens), FadeOut(title))
        # Keep summary tokens for context in next scene, then remove (if not carrying over)
        self.play(FadeOut(summary_tokens), FadeOut(summary_label))
# Scene 7: Selection of important tokens for global attention
class Scene7_Selection(Scene):
    def construct(self):
        title = Text("Selection: Important Global Tokens", font_size=40, color=YELLOW).to_edge(UP)
        # Sequence of tokens (reuse 12 tokens row)
        n = 12
        tokens = VGroup(*[Square(side_length=0.3, fill_opacity=1) for _ in range(n)]).arrange(RIGHT, buff=0.2)
        tokens.set_fill(GRAY)
        tokens.set_color(WHITE)
        tokens.to_edge(DOWN, buff=1.5)
        # Choose a couple of indices as "important"
        important_indices = [2, 6, 10]  # Example indices of important tokens (within range 0-11)
        important_marks = VGroup()
        for idx in important_indices:
            glow = Circle(radius=0.4, color=YELLOW, fill_opacity=0.3)
            glow.move_to(tokens[idx])
            important_marks.add(glow)
        # Label for important tokens
        label = Text("Globally important tokens", font_size=30, color=YELLOW)
        label.next_to(tokens[important_indices[0]], UP, buff=0.8)
        
        # Animate tokens and highlight important ones
        self.play(FadeIn(title))
        self.play(FadeIn(tokens))
        self.play(*[Create(mark) for mark in important_marks])
        self.play(FadeIn(label))
        # Emphasize the important tokens (flash or indicate)
        for glow in important_marks:
            self.play(Indicate(glow, color=YELLOW, scale_factor=1.1))
        # (Optional) Show that these tokens broadcast information globally
        broadcast_arrows = VGroup()
        for i, glow in enumerate(important_marks):
            # draw a few example arrows from an important token to distant tokens
            token_idx = important_indices[i]
            imp_token = tokens[token_idx]
            # Connect to a couple of far tokens to illustrate global reach
            targets = [0, n-1] if token_idx not in [0, n-1] else [n//2]  # choose endpoints or middle
            for t in targets:
                if t == token_idx: 
                    continue
                arr = Arrow(imp_token.get_top(), tokens[t].get_top(), buff=0.1, stroke_width=2, color=YELLOW, tip_length=0.15)
                broadcast_arrows.add(arr)
        self.play(*[GrowArrow(arr) for arr in broadcast_arrows])
        self.wait(1)
        # Fade out scene elements
        self.play(FadeOut(title), FadeOut(tokens), FadeOut(important_marks), FadeOut(label), FadeOut(broadcast_arrows))
# Scene 8: A query attending via both local window and selected global tokens
class Scene8_CombineLocalGlobal(Scene):
    def construct(self):
        title = Text("Combined Local + Global Attention", font_size=40).to_edge(UP)
        # Use a smaller sequence for clarity, say 8 tokens
        n = 8
        tokens = VGroup(*[Circle(radius=0.15, fill_opacity=1) for _ in range(n)]).arrange(RIGHT, buff=0.5)
        tokens.set_fill(GRAY)
        tokens.set_color(WHITE)
        tokens.shift(DOWN*1)
        # Mark one token as query (blue)
        query_idx = 3
        query_token = tokens[query_idx]
        query_token.set_fill(BLUE)
        query_label = Text("Query", font_size=24, color=BLUE).next_to(query_token, DOWN, buff=0.1)
        # Define local window range (e.g., 1 on each side)
        w = 1
        local_neighbors = [i for i in range(max(0, query_idx-w), min(n, query_idx+w+1)) if i != query_idx]
        # Mark local neighbors by cyan outline
        local_highlights = VGroup(*[
            SurroundingRectangle(tokens[i], color=BLUE, buff=0.02).set_stroke(width=3) 
            for i in local_neighbors
        ])
        # Define a couple of global tokens (could be important tokens or summaries)
        # For illustration, take two tokens far away as "global" (or create separate global nodes)
        global_indices = [0, 7]  # e.g., first and last token serve as global info
        global_highlights = VGroup()
        for gi in global_indices:
            tokens[gi].set_fill(YELLOW)
            glow = SurroundingRectangle(tokens[gi], color=YELLOW, buff=0.05).set_stroke(width=4, color=YELLOW)
            global_highlights.add(glow)
        global_label = Text("Global info", font_size=24, color=YELLOW)
        global_label.next_to(tokens[global_indices[1]], UP, buff=0.2)
        # Arrows from query to local neighbors (cyan)
        local_arrows = VGroup(*[
            Arrow(query_token.get_top(), tokens[i].get_top(), buff=0.1, stroke_width=3, color=BLUE, tip_length=0.15)
            for i in local_neighbors
        ])
        # Arrows from query to global tokens (gold)
        global_arrows = VGroup(*[
            Arrow(query_token.get_top(), tokens[i].get_top(), buff=0.1, stroke_width=3, color=YELLOW, tip_length=0.15)
            for i in global_indices
        ])
        # Combine label (to indicate merging attention)
        combine_text = Text("Combine local + global attention", font_size=30)
        combine_text.next_to(query_token, UP, buff=1.0)
        
        # Animate elements
        self.play(FadeIn(title))
        self.play(FadeIn(tokens), FadeIn(query_label))
        # Highlight local window and global tokens
        self.play(Create(local_highlights), Create(global_highlights))
        self.play(FadeIn(global_label))
        # Show arrows from query to local neighbors and global tokens
        self.play(*[GrowArrow(arr) for arr in local_arrows], *[GrowArrow(arr) for arr in global_arrows])
        # Indicate combining of information
        self.play(Write(combine_text, run_time=1.5))
        # Emphasize query token gathering info (maybe a pulse on query)
        self.play(Indicate(query_token, color=BLUE, scale_factor=1.2))
        self.wait(1)
        # Fade out all elements
        self.play(FadeOut(title), FadeOut(tokens), FadeOut(query_label), FadeOut(local_highlights),
                  FadeOut(global_highlights), FadeOut(global_label), FadeOut(local_arrows),
                  FadeOut(global_arrows), FadeOut(combine_text))
# Scene 9: Resulting sparse attention pattern and efficiency gains
class Scene9_EfficientPattern(Scene):
    def construct(self):
        title = Text("Result: Sparse Attention Pattern", font_size=40).to_edge(UP)
        # Parameters for illustrating a small attention matrix (e.g., 12x12)
        n = 12
        w = 2  # window size (each token attends 2 on each side)
        global_cols = [3, 9]  # example indices of global-attended tokens
        # Create a grid of squares to represent an attention matrix
        size = 0.2
        matrix = VGroup()
        for i in range(n):
            for j in range(n):
                square = Square(side_length=size, stroke_width=1, stroke_color=GRAY, fill_opacity=0)
                # position square such that (0,0) is top-left of matrix
                square.move_to(np.array([(j - (n-1)/2) * size, -(i - (n-1)/2) * size, 0]))
                matrix.add(square)
        matrix.scale(1.2)  # scale up for visibility
        matrix.shift(DOWN*0.5)
        # Create highlights for band (cyan) and global columns (gold)
        band_highlights = VGroup()
        global_highlights = VGroup()
        for i in range(n):
            for j in range(n):
                # condition for being in local window band
                if abs(i - j) <= w:
                    band_sq = Square(side_length=size, fill_color=BLUE, fill_opacity=0.7, stroke_width=0)
                    band_sq.move_to(np.array([(j - (n-1)/2) * size, -(i - (n-1)/2) * size, 0]))
                    band_highlights.add(band_sq)
                # condition for global columns
                if j in global_cols:
                    global_sq = Square(side_length=size, fill_color=YELLOW, fill_opacity=0.7, stroke_width=0)
                    global_sq.move_to(np.array([(j - (n-1)/2) * size, -(i - (n-1)/2) * size, 0]))
                    global_highlights.add(global_sq)
        # Group highlights by type
        band_group = band_highlights
        global_group = global_highlights
        # Efficiency text
        complexity_text = Text("Complexity ~ O(n * (w + g))", font_size=30, color=GREEN)
        complexity_text.to_edge(DOWN)
        note_text = Text("Most of the matrix is empty (no computation)", font_size=24).next_to(complexity_text, UP)
        
        # Animate: show title and an outline of matrix then fill highlights
        self.play(FadeIn(title))
        self.play(FadeIn(matrix, lag_ratio=0.1, run_time=1))
        # Reveal band and then global highlights
        self.play(FadeIn(band_group))
        self.play(FadeIn(global_group))
        self.play(Write(note_text))
        self.play(FadeIn(complexity_text))
        # Emphasize sparse pattern (maybe by flashing the nonzero cells)
        self.play(Indicate(band_group, scale_factor=1.05), Indicate(global_group, scale_factor=1.05))
        self.wait(1)
        # Fade out everything
        self.play(FadeOut(title), FadeOut(matrix), FadeOut(band_group), FadeOut(global_group),
                  FadeOut(note_text), FadeOut(complexity_text))
# Scene 10: Conclusion and recap of optimized attention mechanism
class Scene10_Conclusion(Scene):
    def construct(self):
        # Recap bullet points
        recap1 = Text("Local sliding window (blue): linear-time local context", font_size=28, color=BLUE)
        recap2 = Text("Compressed summaries (red): fewer tokens to attend", font_size=28, color=RED)
        recap3 = Text("Selected key tokens (yellow): preserve global info", font_size=28, color=YELLOW)
        recaps = VGroup(recap1, recap2, recap3).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        recaps.to_edge(LEFT, buff=1).shift(UP*1)
        # Final statement
        final_statement = Text("Result: Efficient attention (near-linear) with long-range coverage", 
                                font_size=30, color=WHITE)
        final_statement.to_edge(DOWN)
        
        # Animate recap and conclusion
        self.play(FadeIn(recap1))
        self.play(FadeIn(recap2))
        self.play(FadeIn(recap3))
        self.play(FadeIn(final_statement))
        # Highlight the conclusion
        self.play(Indicate(final_statement, color=GREEN, scale_factor=1.1))
        self.wait(2)
        # Fade out everything to end
        self.play(FadeOut(recaps), FadeOut(final_statement))
