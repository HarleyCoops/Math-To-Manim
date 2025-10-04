# Video Review Toolkit Documentation

## Overview

A comprehensive solution for reviewing Manim MP4 animations without needing a GUI environment. This toolkit provides multiple methods for visual inspection of rendered videos.

## Available Tools

### 1. Video Review Toolkit (`tools/video_review_toolkit.py`)

A Python-based CLI tool providing four key capabilities:

#### Features

- **Frame Extraction** - Extract frames from MP4 using ffmpeg
- **Video Information** - Get metadata (duration, resolution, FPS, codec)
- **Web Player** - Generate HTML5 video player with advanced controls
- **Native Playback** - Launch ffplay for system-level playback

#### Usage

```bash
# Extract frames from video
python tools/video_review_toolkit.py extract media/videos/bhaskara_epic_manim/480p15/BhaskaraEpic.mp4

# Extract at specific FPS (1 frame per second)
python tools/video_review_toolkit.py extract video.mp4 --fps 1

# Extract every 10th frame
python tools/video_review_toolkit.py extract video.mp4 --every-nth 10

# Get video information
python tools/video_review_toolkit.py info video.mp4

# Create web player
python tools/video_review_toolkit.py web video.mp4 -o player.html

# Launch ffplay (native playback)
python tools/video_review_toolkit.py play video.mp4
```

### 2. Frame Viewer (`tools/frame_viewer.py`)

Interactive matplotlib-based frame viewer for stepping through extracted frames.

#### Features

- Frame-by-frame navigation
- Keyboard shortcuts for quick navigation
- Jump to specific percentages
- Large, clear display

#### Usage

```bash
# View frames from extracted directory
python tools/frame_viewer.py media/review_frames/BhaskaraEpic

# Start from specific frame
python tools/frame_viewer.py media/review_frames/BhaskaraEpic --start 42
```

#### Controls

| Key | Action |
|-----|--------|
| `->` / `Space` | Next frame |
| `←` | Previous frame |
| `Home` | First frame |
| `End` | Last frame |
| `0-9` | Jump to 0%-90% |
| `Q` / `Escape` | Quit |

## MCP Server Investigation

### Available MCP Servers Analysis

Based on the investigation of connected MCP servers, here are the findings:

#### 1. **Puppeteer MCP** (`npx -y @modelcontextprotocol/server-puppeteer`)
   - **Relevant Tools**: `puppeteer_navigate`, `puppeteer_screenshot`
   - **Use Case**: Can navigate to the HTML5 web player and capture screenshots
   - **Limitation**: Better for web interaction than video playback

#### 2. **Firecrawl MCP** (`firecrawl-mcp`)
   - **Relevant Tools**: `firecrawl_scrape`
   - **Use Case**: Could theoretically fetch video metadata from web pages
   - **Limitation**: Not designed for video playback or frame extraction

#### 3. **Filesystem MCP** (`@modelcontextprotocol/server-filesystem`)
   - **Relevant Tools**: `read_file`, `list_directory`
   - **Use Case**: Can list and manage frame directories
   - **Limitation**: Cannot read binary video files directly

#### 4. **E2B MCP** (`@e2b/mcp-server`)
   - **Relevant Tools**: `run_code`
   - **Use Case**: Can run Python scripts in sandbox for frame processing
   - **Potential**: Could execute video processing code remotely

### Recommended MCP Server Integration Strategy

#### Option 1: Build Custom Video Review MCP Server

Create a dedicated MCP server that wraps the video review toolkit:

```python
# Conceptual structure for custom MCP server
{
  "tools": [
    {
      "name": "extract_video_frames",
      "description": "Extract frames from MP4 for review",
      "inputSchema": {
        "video_path": "string",
        "fps": "number (optional)",
        "output_dir": "string (optional)"
      }
    },
    {
      "name": "get_video_info",
      "description": "Get video metadata",
      "inputSchema": {
        "video_path": "string"
      }
    },
    {
      "name": "create_video_player",
      "description": "Generate HTML5 player",
      "inputSchema": {
        "video_path": "string",
        "output_html": "string (optional)"
      }
    }
  ],
  "resources": [
    {
      "uri": "frames://{video_name}",
      "description": "Access extracted frames as resources"
    }
  ]
}
```

#### Option 2: Use E2B for Remote Execution

Leverage E2B MCP to run video processing scripts:

```python
# Example: Use E2B to extract frames
from e2b_mcp import run_code

code = """
from video_review_toolkit import VideoReviewToolkit
toolkit = VideoReviewToolkit()
frames_dir = toolkit.extract_frames('video.mp4', fps=1)
print(f"Extracted to: {frames_dir}")
"""

run_code(code)
```

#### Option 3: Enhance Puppeteer Integration

Use Puppeteer MCP with the HTML5 web player:

1. Generate web player using toolkit
2. Use Puppeteer to navigate to player
3. Capture screenshots at specific timestamps
4. Automate frame-by-frame review

## Complete Workflow Examples

### Workflow 1: Quick Frame Review

```bash
# 1. Extract frames (every 5th frame for speed)
python tools/video_review_toolkit.py extract \
  media/videos/bhaskara_epic_manim/480p15/BhaskaraEpic.mp4 \
  --every-nth 5

# 2. View frames interactively
python tools/frame_viewer.py media/review_frames/BhaskaraEpic
```

### Workflow 2: Web-Based Review

```bash
# 1. Create web player
python tools/video_review_toolkit.py web \
  media/videos/bhaskara_epic_manim/480p15/BhaskaraEpic.mp4 \
  -o bhaskara_player.html

# 2. Open in browser
# Windows:
start bhaskara_player.html

# macOS:
open bhaskara_player.html

# Linux:
xdg-open bhaskara_player.html
```

### Workflow 3: Native Playback

```bash
# Launch ffplay directly (requires ffmpeg installation)
python tools/video_review_toolkit.py play \
  media/videos/bhaskara_epic_manim/480p15/BhaskaraEpic.mp4
```

### Workflow 4: Detailed Analysis

```bash
# 1. Get video information
python tools/video_review_toolkit.py info video.mp4

# 2. Extract all frames for detailed review
python tools/video_review_toolkit.py extract video.mp4

# 3. Use frame viewer for analysis
python tools/frame_viewer.py media/review_frames/video
```

## Prerequisites

### Required

- Python 3.8+
- ffmpeg (for frame extraction and video info)

### Optional

- matplotlib (for interactive frame viewer)
- Modern web browser (for HTML5 player)

### Installation

```bash
# Install ffmpeg
# Windows (Chocolatey):
choco install ffmpeg

# macOS (Homebrew):
brew install ffmpeg

# Linux (apt):
sudo apt-get install ffmpeg

# Install Python dependencies
pip install matplotlib  # For frame viewer
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Video Review Toolkit                  │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   ffmpeg     │   │  Web Player  │   │ Frame Viewer │
│  Extraction  │   │   (HTML5)    │   │ (matplotlib) │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ PNG Frames -> │   │  Browser ->   │   │  Interactive │
│  IDE Preview │   │  Playback    │   │  Stepping    │
└──────────────┘   └──────────────┘   └──────────────┘
```

## Advanced Features

### HTML5 Web Player Features

- **Frame-by-frame stepping**: Navigate one frame at a time
- **Variable playback speed**: 0.25x to 2x
- **Precise timeline control**: Scrub to any point
- **Keyboard shortcuts**: Efficient navigation
- **Time display**: Millisecond precision
- **Jump controls**: Quick navigation (-5s, -1s, +1s, +5s)

### Frame Extraction Options

- **FPS-based**: Extract at specific frames per second
- **Nth frame**: Extract every Nth frame
- **Quality control**: Adjust JPEG/PNG quality
- **Custom output**: Specify output directory

## Troubleshooting

### Issue: "ffmpeg not found"

**Solution**: Install ffmpeg using package manager:
```bash
# Windows
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg
```

### Issue: "matplotlib not found"

**Solution**: Install matplotlib:
```bash
pip install matplotlib
```

### Issue: Web player shows black screen

**Solution**: 
1. Check file path in HTML (use absolute paths)
2. Ensure browser supports H.264 codec
3. Try a different browser (Chrome/Edge recommended)

### Issue: Frames directory empty after extraction

**Solution**:
1. Verify video file exists and is valid
2. Check ffmpeg is in PATH: `ffmpeg -version`
3. Try with verbose output to see errors

## Future Enhancements

### Potential MCP Server Development

Create `manim-video-review-mcp` with:

1. **Tools**:
   - `extract_frames` - Frame extraction
   - `get_video_info` - Metadata retrieval
   - `compare_frames` - Frame diff analysis
   - `create_preview` - Generate preview GIFs
   - `analyze_motion` - Motion vector analysis

2. **Resources**:
   - `frames://{video}` - Access frame images
   - `metadata://{video}` - Video metadata
   - `timeline://{video}` - Timeline information

3. **Integration**:
   - Real-time frame access during conversation
   - Automated quality checks
   - Performance metrics
   - Visual diff between renders

## Comparison with Other Solutions

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Frame Extraction** | Works anywhere, IDE preview | Not real-time, storage heavy | Detailed analysis |
| **Web Player** | Full playback, interactive | Needs browser | General review |
| **ffplay** | Native performance | Requires GUI | Quick playback |
| **Frame Viewer** | Interactive stepping | Needs matplotlib | Frame-by-frame |
| **MCP Server** | Integrated workflow | Development needed | Automation |

## Conclusion

The Video Review Toolkit provides comprehensive options for reviewing Manim animations:

1. **Immediate Solution**: Use frame extraction + web player for most cases
2. **Interactive Analysis**: Use frame viewer for detailed inspection
3. **Quick Playback**: Use ffplay if available
4. **Future Enhancement**: Build custom MCP server for workflow integration

All tools work without requiring a GUI in the AI environment, while providing visual review capabilities for the user.

## References

- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Manim Community](https://www.manim.community/)
- [Puppeteer MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer)
