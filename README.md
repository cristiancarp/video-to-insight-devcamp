# Video to Stills Extractor

A robust Python script to extract still frames from video files at specified intervals, with automatic fallback from MoviePy to ffmpeg.

## Features

- **Smart Fallback**: Tries MoviePy first, automatically falls back to ffmpeg if unavailable
- **Flexible Intervals**: Extract frames at any interval (e.g., every 1s, 2s, 0.5s)
- **Time Range Support**: Extract from specific start/end times
- **Quality Control**: Adjustable JPEG quality (1-100)
- **Timestamped Filenames**: Clear naming with seconds and HH-MM-SS format
- **Cross-Platform**: Works on macOS, Linux, and Windows

## Requirements

**Option 1: MoviePy (recommended)**
```bash
pip install moviepy pillow
```

**Option 2: ffmpeg (fallback)**
- Install ffmpeg: `brew install ffmpeg` (macOS) or equivalent for your OS
- The script will automatically detect and use ffmpeg if MoviePy is unavailable

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/video-to-stills.git
cd video-to-stills
```

2. Install dependencies (optional - script works with just ffmpeg):
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Extract frames at 1-second intervals (default):
```bash
python video_to_stills.py input_video.mov output_frames/
```

### Advanced Usage

```bash
# Extract every 2 seconds
python video_to_stills.py video.mp4 frames_2sec/ --interval 2

# Extract segment from 10s to 30s at 0.5s intervals
python video_to_stills.py video.mp4 frames_segment/ --interval 0.5 --start 10 --end 30

# Lower quality for smaller files
python video_to_stills.py video.mp4 frames_compressed/ --quality 70

# Overwrite existing frames
python video_to_stills.py video.mp4 frames/ --overwrite
```

## Output Format

Frames are saved with timestamped filenames:
- `frame_000001s_0-00-01.jpg` (1 second mark)
- `frame_000010s_0-00-10.jpg` (10 second mark)
- `frame_000065s_0-01-05.jpg` (1 minute 5 seconds)

## Supported Formats

- **Input**: MP4, MOV, AVI, MKV, WEBM, and most video formats supported by ffmpeg
- **Output**: JPEG images with adjustable quality

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
