# GIF Rendering Workflow

This document explains how to render animations as GIFs for repository previews.

## Why GIFs?

GIFs allow users to preview animations directly in GitHub without downloading or rendering files. They make the repository more engaging and help users quickly find examples relevant to their needs.

## Quick Start

### Render a Single Animation as GIF

```bash
# Simple usage
python scripts/render_gif.py examples/physics/quantum/QED.py QEDJourney

# With quality setting (l=low, m=medium, h=high)
python scripts/render_gif.py examples/mathematics/geometry/pythagorean.py PythagoreanScene l
```

### Batch Render All Examples

```bash
# Render all examples in low quality (fast)
python scripts/render_examples_as_gifs.py --quality l

# Render only physics examples
python scripts/render_examples_as_gifs.py --category physics

# Dry run to see what would be rendered
python scripts/render_examples_as_gifs.py --dry-run
```

## Workflow Steps

### 1. Render Animations as GIFs

Use the batch script to render multiple animations:

```bash
# Render low quality GIFs for all examples
python scripts/render_examples_as_gifs.py -q l

# Render specific category
python scripts/render_examples_as_gifs.py -c mathematics/geometry -q l

# Limit to first scene per file
python scripts/render_examples_as_gifs.py --max-scenes 1
```

**Quality Recommendations:**
- **Low (`-q l`)**: 480p, 15fps - Fast, small files (~500KB-2MB) [DONE] Recommended for previews
- **Medium (`-q m`)**: 720p, 30fps - Balanced (~2-5MB)
- **High (`-q h`)**: 1080p, 60fps - Large files (>5MB) [WARNING] Not recommended for GitHub

### 2. Verify GIF Placement

After rendering, GIFs should be copied to the same directory as the source files:

```
examples/
├── physics/
│   ├── quantum/
│   │   ├── QED.py
│   │   ├── QED.gif              ← Generated GIF
│   │   ├── SpacetimeQEDScene.py
│   │   └── SpacetimeQEDScene.gif
```

### 3. Update Category READMEs

Add GIF previews to category README files:

```bash
# Update all category READMEs with GIF links
python scripts/add_gif_previews.py

# Update specific category
python scripts/add_gif_previews.py --category physics/quantum

# Dry run to preview changes
python scripts/add_gif_previews.py --dry-run
```

This automatically generates README content like:

```markdown
### QED

**Source**: [`QED.py`](QED.py)

![QED](QED.gif)
```

### 4. Commit and Push

```bash
# Add GIFs and updated READMEs
git add examples/

# Commit
git commit -m "docs: Add GIF previews for [category] examples"

# Push
git push origin main
```

## Script Reference

### `render_gif.py`

Render a single animation as GIF.

**Usage:**
```bash
python scripts/render_gif.py <file.py> <SceneName> [quality]
```

**Arguments:**
- `file.py`: Path to Python file
- `SceneName`: Name of Scene class to render
- `quality`: Optional quality (l, m, h) [default: l]

**Example:**
```bash
python scripts/render_gif.py examples/physics/quantum/QED.py QEDJourney l
```

### `render_examples_as_gifs.py`

Batch render multiple animations as GIFs.

**Usage:**
```bash
python scripts/render_examples_as_gifs.py [options]
```

**Options:**
- `--quality, -q`: Quality level (l, m, h) [default: l]
- `--category, -c`: Only render specific category
- `--dry-run`: Preview without rendering
- `--max-scenes`: Max scenes per file [default: 1]

**Examples:**
```bash
# All examples, low quality
python scripts/render_examples_as_gifs.py -q l

# Only mathematics, medium quality
python scripts/render_examples_as_gifs.py -c mathematics -q m

# Dry run
python scripts/render_examples_as_gifs.py --dry-run
```

### `add_gif_previews.py`

Update category README files with GIF previews.

**Usage:**
```bash
python scripts/add_gif_previews.py [options]
```

**Options:**
- `--category, -c`: Only update specific category
- `--dry-run`: Preview without updating

**Examples:**
```bash
# Update all categories
python scripts/add_gif_previews.py

# Update specific category
python scripts/add_gif_previews.py -c physics/quantum

# Preview changes
python scripts/add_gif_previews.py --dry-run
```

## Best Practices

### File Size

Keep GIF file sizes reasonable for GitHub:
- **Target**: <2MB per GIF
- **Maximum**: 5MB (GitHub soft limit)
- **Use low quality** (`-q l`) for most previews

### Organization

1. Keep GIFs in the same directory as source files
2. Use descriptive scene names that match the GIF
3. Update category READMEs after adding GIFs
4. Test GIFs display correctly in GitHub before pushing

### Selective Rendering

Don't render everything - focus on:
- **Beginner examples**: Help new users get started
- **Showcase pieces**: Your best/most interesting animations
- **Category highlights**: 1-2 representative examples per category

### Git Considerations

GIFs are binary files that increase repository size:
- Be selective about what you render
- Use `.gitattributes` to handle binary files properly
- Consider Git LFS for very large files (though not necessary for <5MB GIFs)

## Troubleshooting

### "Scene not found" Error

**Problem**: Manim can't find the scene class.

**Solution**: Check the class name matches exactly:
```python
# In your Python file
class MyScene(Scene):  # ← Use this exact name
    def construct(self):
        pass
```

### GIF Too Large

**Problem**: GIF file >5MB.

**Solution**: Use lower quality:
```bash
# Use low quality instead of high
python scripts/render_gif.py file.py SceneName l
```

### Rendering Timeout

**Problem**: Scene takes >5 minutes to render.

**Solution**:
1. Use lower quality (`-q l`)
2. Simplify the animation
3. Increase timeout in `render_examples_as_gifs.py` (line 99)

### GIF Not Displaying on GitHub

**Problem**: GIF shows as broken image on GitHub.

**Checklist**:
1. File size <10MB (GitHub hard limit)
2. Path is correct in markdown
3. File is committed and pushed
4. GitHub cache issue (wait a few minutes)

## Example Workflow

Complete workflow for adding GIF previews to a new category:

```bash
# 1. Render animations as GIFs
python scripts/render_examples_as_gifs.py -c physics/quantum -q l --max-scenes 1

# 2. Verify GIFs were created
ls examples/physics/quantum/*.gif

# 3. Update category README with GIF previews
python scripts/add_gif_previews.py -c physics/quantum

# 4. Preview the README
cat examples/physics/quantum/README.md

# 5. Commit and push
git add examples/physics/quantum/
git commit -m "docs: Add GIF previews for quantum physics examples"
git push origin main
```

## Tips for Quality GIFs

### Optimization

- **Keep animations short**: 5-10 seconds ideal
- **Simple scenes render better**: Complex 3D may not display well
- **Test on GitHub**: Preview locally then verify on GitHub

### Manual Optimization

If GIFs are too large, use external tools:

```bash
# Using gifsicle (install: apt-get install gifsicle / brew install gifsicle)
gifsicle -O3 --lossy=80 input.gif -o output.gif

# Using ffmpeg
ffmpeg -i input.gif -vf "fps=10,scale=480:-1:flags=lanczos" output.gif
```

## Future Enhancements

Potential improvements to the workflow:

1. **Parallel rendering**: Render multiple GIFs concurrently
2. **Auto-optimization**: Automatically compress GIFs >2MB
3. **Progress tracking**: Better progress indicators for batch jobs
4. **Resume capability**: Skip already-rendered GIFs
5. **Quality presets**: Category-specific quality settings
6. **GitHub Actions**: Automate GIF generation on push

---

**Need help?** Open an issue or check [CONTRIBUTING.md](CONTRIBUTING.md)
