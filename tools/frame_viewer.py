"""
Interactive Frame Viewer for Manim Video Review
===============================================

A matplotlib-based interactive frame viewer for stepping through extracted frames.

Author: Cline AI Assistant
Date: January 2025
"""

import sys
from pathlib import Path
from typing import List, Optional
import argparse


def view_frames(frames_dir: str, start_frame: int = 0):
    """
    Interactive frame-by-frame viewer using matplotlib.
    
    Args:
        frames_dir: Directory containing extracted frames
        start_frame: Frame number to start viewing from
    
    Controls:
        - Right Arrow / Space: Next frame
        - Left Arrow: Previous frame
        - Home: First frame
        - End: Last frame
        - Number keys 0-9: Jump to 0%-90% of video
        - Q / Escape: Quit
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib.image import imread
    except ImportError:
        print("✗ Error: matplotlib is required for frame viewing")
        print("  Install with: pip install matplotlib")
        sys.exit(1)
    
    frames_dir = Path(frames_dir)
    if not frames_dir.exists():
        print(f"✗ Error: Directory not found: {frames_dir}")
        sys.exit(1)
    
    # Find all frame files
    frames = sorted(frames_dir.glob("frame_*.png"))
    if not frames:
        print(f"✗ Error: No frames found in {frames_dir}")
        print("  Extract frames first using: python tools/video_review_toolkit.py extract <video>")
        sys.exit(1)
    
    print(f"📁 Found {len(frames)} frames in {frames_dir}")
    print("\nControls:")
    print("  -> / Space    : Next frame")
    print("  ←            : Previous frame")
    print("  Home         : First frame")
    print("  End          : Last frame")
    print("  0-9          : Jump to percentage (0% to 90%)")
    print("  Q / Escape   : Quit")
    print()
    
    current_idx = max(0, min(start_frame, len(frames) - 1))
    
    # Setup matplotlib
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.canvas.manager.set_window_title('Manim Frame Viewer')
    plt.subplots_adjust(left=0, right=1, top=0.95, bottom=0.05)
    
    def update_display():
        """Update the displayed frame."""
        ax.clear()
        img = imread(frames[current_idx])
        ax.imshow(img)
        ax.axis('off')
        
        # Display frame info
        frame_info = (
            f"Frame {current_idx + 1} / {len(frames)} "
            f"({(current_idx + 1) / len(frames) * 100:.1f}%)"
        )
        ax.set_title(frame_info, fontsize=14, pad=10)
        fig.canvas.draw_idle()
    
    def on_key(event):
        """Handle keyboard input."""
        nonlocal current_idx
        
        if event.key in ['q', 'escape']:
            plt.close()
            return
        
        # Navigation
        if event.key in ['right', ' ']:  # Next frame
            current_idx = min(current_idx + 1, len(frames) - 1)
        elif event.key == 'left':  # Previous frame
            current_idx = max(current_idx - 1, 0)
        elif event.key == 'home':  # First frame
            current_idx = 0
        elif event.key == 'end':  # Last frame
            current_idx = len(frames) - 1
        elif event.key in '0123456789':  # Jump to percentage
            percent = int(event.key) * 10
            current_idx = int((percent / 100) * (len(frames) - 1))
        else:
            return  # Ignore other keys
        
        update_display()
    
    # Connect event handler
    fig.canvas.mpl_connect('key_press_event', on_key)
    
    # Initial display
    update_display()
    plt.show()
    
    print("👋 Frame viewer closed")


def cli():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Interactive frame viewer for Manim video review"
    )
    parser.add_argument(
        'frames_dir',
        help='Directory containing extracted frames'
    )
    parser.add_argument(
        '-s', '--start',
        type=int,
        default=0,
        help='Starting frame number (default: 0)'
    )
    
    args = parser.parse_args()
    view_frames(args.frames_dir, args.start)


if __name__ == "__main__":
    cli()
