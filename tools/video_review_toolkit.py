"""
Video Review Toolkit for Manim MP4 Output
==========================================

A comprehensive toolkit for reviewing Manim-generated MP4 animations without a GUI.
Provides frame extraction, Python-based preview, and web-based playback options.

Author: Cline AI Assistant
Date: January 2025
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import Optional, List
import json


class VideoReviewToolkit:
    """Main class for video review operations."""
    
    def __init__(self, media_dir: str = "media"):
        """
        Initialize the toolkit.
        
        Args:
            media_dir: Base media directory (default: "media")
        """
        self.media_dir = Path(media_dir)
        self.videos_dir = self.media_dir / "videos"
        self.frames_dir = self.media_dir / "review_frames"
        self.frames_dir.mkdir(exist_ok=True, parents=True)
    
    def extract_frames(
        self,
        video_path: str,
        output_dir: Optional[str] = None,
        fps: Optional[float] = None,
        every_nth_frame: Optional[int] = None,
        quality: int = 2
    ) -> Path:
        """
        Extract frames from MP4 video using ffmpeg.
        
        Args:
            video_path: Path to MP4 file
            output_dir: Output directory (default: media/review_frames)
            fps: Extract at specific FPS (e.g., 1 for 1 frame/second)
            every_nth_frame: Extract every Nth frame (alternative to fps)
            quality: JPEG quality 2-31, lower is better (default: 2)
        
        Returns:
            Path to output directory
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        # Determine output directory
        if output_dir is None:
            output_dir = self.frames_dir / video_path.stem
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Build ffmpeg command
        output_pattern = str(output_dir / "frame_%04d.png")
        cmd = ["ffmpeg", "-i", str(video_path)]
        
        # Add frame selection filter
        if fps is not None:
            cmd.extend(["-vf", f"fps={fps}"])
        elif every_nth_frame is not None:
            cmd.extend(["-vf", f"select='not(mod(n\\,{every_nth_frame}))'", "-vsync", "0"])
        
        # Output settings
        cmd.extend(["-q:v", str(quality), output_pattern])
        
        print(f"Extracting frames from: {video_path}")
        print(f"Output directory: {output_dir}")
        print(f"Command: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            frames = sorted(output_dir.glob("frame_*.png"))
            print(f"[OK] Extracted {len(frames)} frames")
            return output_dir
        except subprocess.CalledProcessError as e:
            print(f"Error extracting frames: {e.stderr.decode()}")
            raise
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Get video metadata using ffprobe.
        
        Args:
            video_path: Path to MP4 file
        
        Returns:
            Dictionary with video information
        """
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(video_path)
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True)
            info = json.loads(result.stdout)
            
            # Extract relevant info
            video_stream = next(
                (s for s in info.get("streams", []) if s["codec_type"] == "video"),
                None
            )
            
            if video_stream:
                return {
                    "duration": float(info["format"].get("duration", 0)),
                    "width": video_stream.get("width"),
                    "height": video_stream.get("height"),
                    "fps": eval(video_stream.get("r_frame_rate", "0/1")),
                    "codec": video_stream.get("codec_name"),
                    "size_mb": float(info["format"].get("size", 0)) / (1024 * 1024)
                }
            return {}
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {}
    
    def create_web_player(self, video_path: str, output_html: str = "video_player.html"):
        """
        Create an HTML5 video player with frame-by-frame controls.
        
        Args:
            video_path: Path to MP4 file
            output_html: Output HTML filename
        """
        video_path = Path(video_path).resolve()
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Review Player - {video_path.name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: #4CAF50;
            margin-bottom: 20px;
            font-size: 24px;
        }}
        .video-info {{
            background: #252525;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        .video-wrapper {{
            position: relative;
            background: #000;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 20px;
        }}
        video {{
            width: 100%;
            display: block;
        }}
        .controls {{
            background: #252525;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .control-group {{
            margin-bottom: 15px;
        }}
        .control-group label {{
            display: block;
            margin-bottom: 5px;
            color: #4CAF50;
            font-weight: bold;
        }}
        .button-row {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        button {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }}
        button:hover {{
            background: #45a049;
        }}
        button:active {{
            transform: scale(0.98);
        }}
        button.secondary {{
            background: #2196F3;
        }}
        button.secondary:hover {{
            background: #0b7dda;
        }}
        input[type="range"] {{
            width: 100%;
            margin: 10px 0;
        }}
        .playback-rate {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .playback-rate button {{
            padding: 8px 15px;
            font-size: 12px;
        }}
        .time-display {{
            font-family: monospace;
            font-size: 16px;
            color: #4CAF50;
            margin: 10px 0;
        }}
        .shortcuts {{
            background: #252525;
            padding: 15px;
            border-radius: 8px;
            font-size: 13px;
        }}
        .shortcuts h2 {{
            color: #4CAF50;
            margin-bottom: 10px;
            font-size: 16px;
        }}
        .shortcuts ul {{
            list-style: none;
            padding-left: 0;
        }}
        .shortcuts li {{
            padding: 5px 0;
            border-bottom: 1px solid #333;
        }}
        .shortcuts li:last-child {{
            border-bottom: none;
        }}
        .shortcut-key {{
            display: inline-block;
            background: #333;
            padding: 2px 8px;
            border-radius: 3px;
            font-family: monospace;
            margin-right: 10px;
            min-width: 60px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 Video Review Player</h1>
        
        <div class="video-info">
            <strong>File:</strong> {video_path.name}<br>
            <strong>Path:</strong> {video_path}
        </div>

        <div class="video-wrapper">
            <video id="videoPlayer" preload="metadata">
                <source src="file:///{video_path.as_posix()}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>

        <div class="controls">
            <div class="control-group">
                <label>Playback Controls</label>
                <div class="button-row">
                    <button id="playPause">>️ Play / Pause</button>
                    <button id="stepBack" class="secondary">⏮️ -1 Frame</button>
                    <button id="stepForward" class="secondary">[SKIP] +1 Frame</button>
                    <button id="restart" class="secondary">🔄 Restart</button>
                </div>
            </div>

            <div class="control-group">
                <label>Timeline</label>
                <input type="range" id="timeline" value="0" min="0" max="100" step="0.1">
                <div class="time-display">
                    <span id="currentTime">0:00.000</span> / <span id="duration">0:00.000</span>
                </div>
            </div>

            <div class="control-group">
                <label>Playback Speed</label>
                <div class="playback-rate">
                    <button onclick="setPlaybackRate(0.25)">0.25x</button>
                    <button onclick="setPlaybackRate(0.5)">0.5x</button>
                    <button onclick="setPlaybackRate(1.0)">1x</button>
                    <button onclick="setPlaybackRate(1.5)">1.5x</button>
                    <button onclick="setPlaybackRate(2.0)">2x</button>
                    <span id="currentRate" style="margin-left: 10px;">1.0x</span>
                </div>
            </div>

            <div class="control-group">
                <label>Volume</label>
                <input type="range" id="volume" value="100" min="0" max="100" step="1">
            </div>

            <div class="control-group">
                <label>Jump Controls</label>
                <div class="button-row">
                    <button onclick="skipTime(-5)" class="secondary">⏪ -5s</button>
                    <button onclick="skipTime(-1)" class="secondary">⏪ -1s</button>
                    <button onclick="skipTime(1)" class="secondary">⏩ +1s</button>
                    <button onclick="skipTime(5)" class="secondary">⏩ +5s</button>
                </div>
            </div>
        </div>

        <div class="shortcuts">
            <h2>⌨️ Keyboard Shortcuts</h2>
            <ul>
                <li><span class="shortcut-key">Space</span> Play / Pause</li>
                <li><span class="shortcut-key">← -></span> Step backward / forward (1 frame)</li>
                <li><span class="shortcut-key">Shift + ←</span> Jump back 5 seconds</li>
                <li><span class="shortcut-key">Shift + -></span> Jump forward 5 seconds</li>
                <li><span class="shortcut-key">0-9</span> Jump to 0%-90% of video</li>
                <li><span class="shortcut-key">Home</span> Jump to start</li>
                <li><span class="shortcut-key">End</span> Jump to end</li>
                <li><span class="shortcut-key">+ -</span> Increase / decrease speed</li>
            </ul>
        </div>
    </div>

    <script>
        const video = document.getElementById('videoPlayer');
        const timeline = document.getElementById('timeline');
        const playPauseBtn = document.getElementById('playPause');
        const volumeSlider = document.getElementById('volume');
        const currentTimeDisplay = document.getElementById('currentTime');
        const durationDisplay = document.getElementById('duration');
        const currentRateDisplay = document.getElementById('currentRate');

        // Format time as M:SS.mmm
        function formatTime(seconds) {{
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            const ms = Math.floor((seconds % 1) * 1000);
            return `${{mins}}:${{secs.toString().padStart(2, '0')}}.${{ms.toString().padStart(3, '0')}}`;
        }}

        // Update timeline and time display
        video.addEventListener('timeupdate', () => {{
            const percent = (video.currentTime / video.duration) * 100;
            timeline.value = percent;
            currentTimeDisplay.textContent = formatTime(video.currentTime);
        }});

        // Set duration when metadata loads
        video.addEventListener('loadedmetadata', () => {{
            durationDisplay.textContent = formatTime(video.duration);
        }});

        // Timeline scrubbing
        timeline.addEventListener('input', () => {{
            const time = (timeline.value / 100) * video.duration;
            video.currentTime = time;
        }});

        // Play/Pause
        playPauseBtn.addEventListener('click', () => {{
            if (video.paused) {{
                video.play();
            }} else {{
                video.pause();
            }}
        }});

        // Step frame by frame (approximate)
        document.getElementById('stepForward').addEventListener('click', () => {{
            video.pause();
            video.currentTime += 1/30; // Assumes ~30fps
        }});

        document.getElementById('stepBack').addEventListener('click', () => {{
            video.pause();
            video.currentTime -= 1/30;
        }});

        // Restart
        document.getElementById('restart').addEventListener('click', () => {{
            video.currentTime = 0;
        }});

        // Volume control
        volumeSlider.addEventListener('input', () => {{
            video.volume = volumeSlider.value / 100;
        }});

        // Playback rate
        function setPlaybackRate(rate) {{
            video.playbackRate = rate;
            currentRateDisplay.textContent = rate.toFixed(2) + 'x';
        }}

        // Skip time
        function skipTime(seconds) {{
            video.currentTime += seconds;
        }}

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {{
            switch(e.key) {{
                case ' ':
                    e.preventDefault();
                    playPauseBtn.click();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    if (e.shiftKey) {{
                        skipTime(-5);
                    }} else {{
                        document.getElementById('stepBack').click();
                    }}
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    if (e.shiftKey) {{
                        skipTime(5);
                    }} else {{
                        document.getElementById('stepForward').click();
                    }}
                    break;
                case 'Home':
                    e.preventDefault();
                    video.currentTime = 0;
                    break;
                case 'End':
                    e.preventDefault();
                    video.currentTime = video.duration;
                    break;
                case '+':
                case '=':
                    e.preventDefault();
                    setPlaybackRate(Math.min(video.playbackRate + 0.25, 4));
                    break;
                case '-':
                    e.preventDefault();
                    setPlaybackRate(Math.max(video.playbackRate - 0.25, 0.25));
                    break;
                default:
                    // Number keys for jumping
                    if (e.key >= '0' && e.key <= '9') {{
                        e.preventDefault();
                        const percent = parseInt(e.key) * 10;
                        video.currentTime = (percent / 100) * video.duration;
                    }}
            }}
        }});
    </script>
</body>
</html>"""
        
        output_path = Path(output_html)
        output_path.write_text(html_content, encoding='utf-8')
        print(f"[OK] Created web player: {output_path.resolve()}")
        return output_path
    
    def launch_ffplay(self, video_path: str):
        """
        Launch ffplay for native video playback (if available).
        
        Args:
            video_path: Path to MP4 file
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        try:
            print(f"Launching ffplay for: {video_path}")
            subprocess.Popen(["ffplay", "-autoexit", str(video_path)])
            print("[OK] ffplay launched (separate window)")
        except FileNotFoundError:
            print("✗ ffplay not found. Install ffmpeg with: choco install ffmpeg")
            raise


def cli():
    """Command-line interface for the video review toolkit."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Video Review Toolkit for Manim MP4 Output"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Extract frames command
    extract = subparsers.add_parser('extract', help='Extract frames from video')
    extract.add_argument('video', help='Path to MP4 file')
    extract.add_argument('-o', '--output', help='Output directory')
    extract.add_argument('-f', '--fps', type=float, help='Extract at specific FPS')
    extract.add_argument('-n', '--every-nth', type=int, help='Extract every Nth frame')
    extract.add_argument('-q', '--quality', type=int, default=2, help='Quality (2-31)')
    
    # Video info command
    info = subparsers.add_parser('info', help='Get video information')
    info.add_argument('video', help='Path to MP4 file')
    
    # Create web player command
    web = subparsers.add_parser('web', help='Create HTML5 web player')
    web.add_argument('video', help='Path to MP4 file')
    web.add_argument('-o', '--output', default='video_player.html', help='Output HTML file')
    
    # Launch ffplay command
    play = subparsers.add_parser('play', help='Launch ffplay (if available)')
    play.add_argument('video', help='Path to MP4 file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    toolkit = VideoReviewToolkit()
    
    try:
        if args.command == 'extract':
            toolkit.extract_frames(
                args.video,
                output_dir=args.output,
                fps=args.fps,
                every_nth_frame=args.every_nth,
                quality=args.quality
            )
        
        elif args.command == 'info':
            info = toolkit.get_video_info(args.video)
            print("\n📹 Video Information:")
            print("=" * 50)
            for key, value in info.items():
                print(f"  {key:12}: {value}")
            print("=" * 50)
        
        elif args.command == 'web':
            toolkit.create_web_player(args.video, args.output)
            print(f"\n[TIP] Open in browser: file:///{Path(args.output).resolve()}")
        
        elif args.command == 'play':
            toolkit.launch_ffplay(args.video)
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
