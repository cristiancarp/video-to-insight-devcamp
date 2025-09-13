#!/usr/bin/env python3
"""Extract still frames from video using MoviePy or ffmpeg fallback."""

import os
import argparse
import subprocess
from datetime import timedelta
from pathlib import Path


def extract_frames_ffmpeg(input_path, output_dir, frame_interval=1, start_time=0, end_time=None, quality=90):
    """Extract frames using ffmpeg directly as fallback."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Get video duration first
    probe_cmd = [
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
        '-of', 'csv=p=0', input_path
    ]
    
    try:
        result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"Warning: Could not get video duration: {e}")
        duration = None
    
    if end_time is None or (duration and end_time > duration):
        end_time = duration
    
    # Build ffmpeg command
    cmd = ['ffmpeg', '-y']  # -y to overwrite files
    
    if start_time > 0:
        cmd.extend(['-ss', str(start_time)])
    
    cmd.extend(['-i', input_path])
    
    if end_time and end_time > start_time:
        cmd.extend(['-t', str(end_time - start_time)])
    
    # Extract every N seconds: -vf fps=1/N
    fps_filter = f'fps=1/{frame_interval}'
    cmd.extend(['-vf', fps_filter])
    
    # Quality and format (convert 1-100 to ffmpeg's 31-1 scale)
    ffmpeg_quality = max(1, min(31, 32 - quality//3))
    cmd.extend(['-q:v', str(ffmpeg_quality)])
    
    # Output pattern with frame number
    output_pattern = os.path.join(output_dir, 'frame_%06d.jpg')
    cmd.append(output_pattern)
    
    print(f"Running ffmpeg: {' '.join(cmd[:6])}... (frame extraction)")
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Count and rename frames with timestamps
        frame_files = sorted(Path(output_dir).glob('frame_*.jpg'))
        extracted = 0
        
        for i, frame_file in enumerate(frame_files):
            current_time = start_time + (i * frame_interval)
            hms = str(timedelta(seconds=int(current_time)))
            sec_int = int(current_time)
            new_name = f"frame_{sec_int:06d}s_{hms.replace(':','-')}.jpg"
            new_path = frame_file.parent / new_name
            frame_file.rename(new_path)
            extracted += 1
            
        return extracted
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        return 0


def split_clip_moviepy(input_path, output_dir, frame_interval=1, start_time=0, end_time=None, jpeg_quality=90, overwrite=False):
    """Original MoviePy implementation."""
    try:
        from moviepy.editor import VideoFileClip
        from PIL import Image
    except ImportError as e:
        raise ImportError(f"MoviePy dependencies not available: {e}")
    
    clip = VideoFileClip(input_path)
    duration = clip.duration

    if end_time is None or end_time > duration:
        end_time = duration
    if start_time < 0:
        start_time = 0
    if frame_interval <= 0:
        raise ValueError("frame_interval must be > 0")

    os.makedirs(output_dir, exist_ok=True)

    current = start_time
    extracted = 0
    while current <= end_time + 1e-6:  # small epsilon
        frame = clip.get_frame(current)
        img = Image.fromarray(frame)
        # Build filename with seconds and HMS
        hms = str(timedelta(seconds=int(current)))
        sec_int = int(current)
        filename = f"frame_{sec_int:06d}s_{hms.replace(':','-')}.jpg"
        out_path = os.path.join(output_dir, filename)
        if not overwrite and os.path.exists(out_path):
            current += frame_interval
            continue
        img.save(out_path, quality=jpeg_quality, optimize=True)
        extracted += 1
        current += frame_interval
    clip.close()
    return extracted


def split_clip_to_still_frames(input_path, output_dir, frame_interval=1, start_time=0, end_time=None, jpeg_quality=90, overwrite=False):
    """Extract still frames every frame_interval seconds."""
    # Try MoviePy first, fall back to ffmpeg if import fails
    try:
        return split_clip_moviepy(input_path, output_dir, frame_interval, start_time, end_time, jpeg_quality, overwrite)
    except (ImportError, ModuleNotFoundError, RuntimeError) as e:
        print(f"MoviePy failed ({e}), trying ffmpeg fallback...")
        return extract_frames_ffmpeg(input_path, output_dir, frame_interval, start_time, end_time, jpeg_quality)


def main():
    parser = argparse.ArgumentParser(description="Extract still frames every N seconds from a video.")
    parser.add_argument("input", help="Path to input video (e.g. IMG_0343.MOV)")
    parser.add_argument("output", help="Output directory for frames")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between frames (default 1)")
    parser.add_argument("--start", type=float, default=0.0, help="Start time in seconds (default 0)")
    parser.add_argument("--end", type=float, default=None, help="End time in seconds (default video end)")
    parser.add_argument("--quality", type=int, default=90, help="JPEG quality 1-100 (default 90)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing frames")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        return 1

    count = split_clip_to_still_frames(
        input_path=args.input,
        output_dir=args.output,
        frame_interval=args.interval,
        start_time=args.start,
        end_time=args.end,
        jpeg_quality=args.quality,
        overwrite=args.overwrite,
    )
    print(f"Extracted {count} frames to {args.output}")
    return 0


if __name__ == "__main__":
    exit(main())

# Example usage:
# python video_to_stills.py IMG_0343.MOV frames_IMG_0343 --interval 1
# python video_to_stills.py IMG_0343.MOV frames_2sec --interval 2 --start 5 --end 15
