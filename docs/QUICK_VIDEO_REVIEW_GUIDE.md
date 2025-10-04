# Quick Video Review Guide

**Get started reviewing your Manim animations in under 2 minutes!**

## [LAUNCH] Quick Start

### Option 1: Web Player (Recommended)

Create an interactive HTML5 player with frame-by-frame controls:

```bash
python tools/video_review_toolkit.py web <path-to-video.mp4>
```

Then open the generated `video_player.html` in your browser.

**Example:**
```bash
python tools/video_review_toolkit.py web media/videos/ULTRAQED/480p15/ULTRAQEDComplete.mp4 -o my_player.html
start my_player.html  # Windows
```

### Option 2: Frame Extraction + IDE Preview

Extract frames as PNG images to view in your IDE:

```bash
# Extract all frames
python tools/video_review_toolkit.py extract <path-to-video.mp4>

# Extract every 5th frame (faster)
python tools/video_review_toolkit.py extract <path-to-video.mp4> --every-nth 5
```

Frames are saved to `media/review_frames/` and can be viewed directly in Cursor/VSCode.

### Option 3: Interactive Frame Viewer

Step through frames interactively using matplotlib:

```bash
# First extract frames
python tools/video_review_toolkit.py extract <video.mp4>

# Then view them
python tools/frame_viewer.py media/review_frames/<video_name>
```

**Controls:** Arrow keys, Space, Home, End, 0-9 for jumping

### Option 4: Native Playback (if ffmpeg installed)

```bash
python tools/video_review_toolkit.py play <path-to-video.mp4>
```

## [TODO] Common Commands

```bash
# Get video information (duration, resolution, FPS)
python tools/video_review_toolkit.py info <video.mp4>

# Extract 1 frame per second
python tools/video_review_toolkit.py extract <video.mp4> --fps 1

# Create custom-named web player
python tools/video_review_toolkit.py web <video.mp4> -o my_review.html
```

## [TARGET] Which Method Should I Use?

| Method | When to Use |
|--------|-------------|
| **Web Player** | General review, need playback controls |
| **Frame Extraction** | Detailed analysis, compare specific frames |
| **Frame Viewer** | Interactive stepping, need keyboard control |
| **Native Playback** | Quick check, ffmpeg available |

## 🛠️ Setup

### Requirements

- Python 3.8+ (already have [OK])
- ffmpeg (for extraction/info)
- matplotlib (for frame viewer)

### Install ffmpeg (Windows)

```bash
choco install ffmpeg
```

Or download from: https://www.gyan.dev/ffmpeg/builds/

### Install matplotlib (optional)

```bash
pip install matplotlib
```

## [TIP] Tips

1. **Web player doesn't need ffmpeg** - works immediately for playback
2. **Use `--every-nth` flag** when extracting frames to save disk space
3. **Frame viewer requires matplotlib** - install if using this method
4. **Web player has best UX** - frame-by-frame, speed control, scrubbing

## [DOCS] Full Documentation

See `docs/VIDEO_REVIEW_TOOLKIT.md` for comprehensive documentation including:
- MCP server integration options
- Advanced features
- Troubleshooting
- Architecture details
- Future enhancement plans

## 🎬 Example Workflow

```bash
# 1. Create web player for general review
python tools/video_review_toolkit.py web media/videos/ULTRAQED/480p15/ULTRAQEDComplete.mp4

# 2. Extract specific frames for detailed analysis
python tools/video_review_toolkit.py extract media/videos/ULTRAQED/480p15/ULTRAQEDComplete.mp4 --fps 2

# 3. View frames interactively
python tools/frame_viewer.py media/review_frames/ULTRAQEDComplete

# 4. Get video metadata
python tools/video_review_toolkit.py info media/videos/ULTRAQED/480p15/ULTRAQEDComplete.mp4
```

## [?] Troubleshooting

**"ffmpeg not found"** -> Install ffmpeg (see Setup section)

**Web player shows black screen** -> Try different browser (Chrome/Edge)

**matplotlib not found** -> Run `pip install matplotlib`

**Video file not found** -> Check path with `ls media/videos/`

## 🔗 Related Tools

- `tools/video_review_toolkit.py` - Main toolkit
- `tools/frame_viewer.py` - Interactive viewer
- `docs/VIDEO_REVIEW_TOOLKIT.md` - Full documentation
- `media/review_frames/` - Extracted frames directory

---

**Need help?** See full documentation in `docs/VIDEO_REVIEW_TOOLKIT.md`
