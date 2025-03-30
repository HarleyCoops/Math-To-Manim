from manim import Scene, Dot, VGroup, Line, RoundedRectangle, Tex, FadeIn, FadeOut, Write, Transform, Create, ORIGIN, RIGHT, LEFT, UP, DOWN, BLACK, WHITE, GRAY_B, YELLOW, BLUE, GREEN, PI, rush_into, smooth

class AlexNetIntro(Scene):
    def construct(self):
        # Set dark background
        self.camera.background_color = BLACK

        # Initial spark of innovation
        spark = Dot(ORIGIN, color=YELLOW).scale(0.05)
        self.play(spark.animate.scale(20), rate_func=rush_into, run_time=1.5)
        self.wait(0.2)

        # Transform spark into abstract network architecture
        lines = VGroup(*[Line(ORIGIN, 3*RIGHT).rotate(i*PI/6, about_point=ORIGIN)
                         for i in range(12)]).set_color(BLUE)
        blocks = VGroup(*[RoundedRectangle(height=0.6, width=1.2, corner_radius=0.1)
                          .set_fill(GREEN, opacity=0.6)
                          .move_to(3.5*RIGHT)
                          .rotate(i*PI/3, about_point=ORIGIN)
                          for i in range(6)])

        self.play(Transform(spark, lines), run_time=2, rate_func=smooth)
        self.play(Create(blocks), run_time=1.5, rate_func=smooth)

        # AlexNet (2012) materializing text
        alexnet_text = VGroup(
            Tex("AlexNet", color=WHITE).scale(2),
            Tex("(2012)", color=GRAY_B).scale(1.2)
        ).arrange(DOWN, aligned_edge=LEFT).move_to(UP*0.5+LEFT*2)

        self.play(FadeIn(alexnet_text, shift=UP), run_time=1.5)

        # Impact keywords flashing briefly
        keywords = ["Groundbreaking", "ImageNet", "Deep Learning"]
        flashes = VGroup(*[Tex(word, color=YELLOW).scale(1.2) for word in keywords])
        flashes.arrange(RIGHT, buff=1).to_edge(DOWN)

        for flash in flashes:
            self.play(FadeIn(flash, scale=1.2), run_time=0.5)
            self.wait(0.4)
            self.play(FadeOut(flash, scale=0.8), run_time=0.4)

        # Main title appears
        main_title = Tex("Understanding the Original AlexNet Source Code (2012)",
                         color=WHITE).scale(0.9).to_edge(UP)
        self.play(Write(main_title), run_time=2)

        # Short pause to absorb visual
        self.wait(2)

        # Clean fade out to transition to next scene
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1.5)
        self.wait(1)

# Add this execution block to run the scene when the file is executed directly
if __name__ == "__main__":
    from manim import config
    config.quality = "high_quality"  # You can adjust quality here
    scene = AlexNetIntro()
    scene.render()
