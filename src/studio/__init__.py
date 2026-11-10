"""Studio: one scene description, three engines, a film and a web page.

Studio is the multi-engine pipeline for Math-To-Manim. A run is a state
machine in code; agents each write one typed file; every shot is rendered,
measured and reviewed. The design is in the "Studio pipeline design" document.

This silo is being built in milestones. What exists now:

- ``studio.settings``: where runs live and where the pinned tools are
- ``studio.doctor``: checks each tool and version, renders one test shot per
  engine, and writes ``env.lock.json`` with the measured seconds per frame
- ``studio.smoke``: the test scenes the doctor renders
- ``studio.cli``: the ``math-to-manim-studio`` command

No other silo is imported here, and no other silo imports this one.
"""

__version__ = "0.1.0"
