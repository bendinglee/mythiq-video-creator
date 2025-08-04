🎬 Mythiq Video Creator

Advanced AI video generation service using multiple state-of-the-art models for maximum quality and variety.

🚀 Features

Multi-Model Architecture

•
Mochi-1: Photorealistic videos (6 seconds, highest quality)

•
CogVideoX-5B: Creative and artistic videos (6 seconds, high quality)

•
AnimateDiff: Animated and cartoon videos (2 seconds, high quality)

Smart Model Selection

•
Auto-detection: Automatically chooses the best model based on prompt

•
Manual selection: Users can specify which model to use

•
Optimized quality: Each model optimized for its strengths

Advanced Features

•
Memory optimization: Efficient GPU memory management

•
CPU fallback: Works on systems without GPU

•
Base64 encoding: Videos returned as data URLs for easy frontend integration

•
Error handling: Comprehensive error handling and logging

📋 API Endpoints

POST /generate-video

Generate video from text prompt.

Request:

JSON


{
  "prompt": "A cat playing with a ball of yarn",
  "duration": 6,
  "model_type": "auto"
}


Response:

JSON


{
  "success": true,
  "video_data": "data:video/mp4;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...",
  "model_used": "photorealistic",
  "duration": 6,
  "prompt": "A cat playing with a ball of yarn",
  "timestamp": "2024-01-01T12:00:00",
  "message": "Video generated successfully using photorealistic model"
}


GET /video-models

Get available video generation models and their capabilities.

POST /generate-video-preview

Generate a quick preview and model recommendation.

GET /health

Health check endpoint with system status.

🎯 Model Selection Guide

Photorealistic (Mochi-1)

Best for:

•
Real people and objects

•
Nature scenes

•
Product demonstrations

•
Documentary-style content

Example prompts:

•
"A person walking through a forest"

•
"Ocean waves crashing on rocks"

•
"A chef preparing food in a kitchen"

Creative (CogVideoX-5B)

Best for:

•
Artistic and abstract content

•
Fantasy and surreal scenes

•
Creative interpretations

•
Stylized visuals

Example prompts:

•
"Abstract flowing colors in space"

•
"A magical forest with glowing trees"

•
"Surreal landscape with floating islands"

Animation (AnimateDiff)

Best for:

•
Cartoon and anime style

•
Character animations

•
Illustrated content

•
Mascot videos

Example prompts:

•
"Cartoon cat dancing happily"

•
"Anime character waving hello"

•
"Illustrated bird flying through clouds"

🛠️ Installation

Local Development

Bash


# Clone repository
git clone <repository-url>
cd mythiq-video-creator

# Install dependencies
pip install -r requirements.txt

# Run the service
python app.py


Railway Deployment

1.
Create new Railway project

2.
Connect to GitHub repository

3.
Railway will auto-detect and deploy

4.
Service will be available at your Railway URL

⚙️ Configuration

Environment Variables

•
PORT: Service port (default: 5000)

•
CUDA_VISIBLE_DEVICES: GPU selection (optional)

Model Configuration

Models are automatically downloaded on first use:

•
Mochi-1: ~8GB download

•
CogVideoX-5B: ~10GB download

•
AnimateDiff: ~4GB download

🔧 Performance Optimization

Memory Management

•
Models use CPU offloading to reduce GPU memory usage

•
VAE slicing enabled for memory efficiency

•
Automatic memory cleanup after generation

Quality Settings

•
Mochi-1: 64 inference steps for maximum quality

•
CogVideoX: 50 inference steps for balanced speed/quality

•
AnimateDiff: 25 inference steps for fast generation

📊 System Requirements

Minimum

•
RAM: 16GB

•
Storage: 25GB free space

•
CPU: 8 cores recommended

Recommended

•
GPU: NVIDIA RTX 4090 or better

•
VRAM: 24GB+

•
RAM: 32GB+

•
Storage: SSD with 50GB+ free space

Railway Deployment

•
Memory: 16GB+ plan recommended

•
CPU: High-performance plan

•
Storage: 25GB+ for models

🎬 Usage Examples

Basic Video Generation

Python


import requests

response = requests.post('https://your-service.railway.app/generate-video', json={
    'prompt': 'A beautiful sunset over mountains',
    'duration': 6
})

data = response.json()
if data['success']:
    video_data = data['video_data']  # Base64 encoded video


Model-Specific Generation

Python


# Force photorealistic model
response = requests.post('https://your-service.railway.app/generate-video', json={
    'prompt': 'A realistic cat playing',
    'model_type': 'photorealistic',
    'duration': 6
})

# Force animation model
response = requests.post('https://your-service.railway.app/generate-video', json={
    'prompt': 'Cartoon cat dancing',
    'model_type': 'animation',
    'duration': 2
})


🔍 Troubleshooting

Common Issues

Out of Memory Error:

•
Reduce duration

•
Use CPU mode

•
Restart service to clear memory

Model Loading Failed:

•
Check internet connection

•
Verify sufficient storage space

•
Check Railway logs for specific errors

Slow Generation:

•
Use GPU-enabled Railway plan

•
Reduce inference steps in code

•
Use shorter durations

📈 Performance Metrics

Generation Times (GPU)

•
Mochi-1: 60-120 seconds for 6-second video

•
CogVideoX: 45-90 seconds for 6-second video

•
AnimateDiff: 30-60 seconds for 2-second video

Quality Comparison

•
Mochi-1: 9.5/10 (photorealistic)

•
CogVideoX: 9.0/10 (creative)

•
AnimateDiff: 8.5/10 (animation)

🌟 Advanced Features

Batch Processing

Service supports multiple concurrent requests with proper memory management.

Custom Styling

Each model can be fine-tuned with additional parameters for specific styles.

Integration Ready

Designed for seamless integration with Mythiq AI Platform frontend.

📞 Support

For issues and questions:

1.
Check Railway deployment logs

2.
Verify model downloads completed

3.
Monitor memory usage

4.
Check GPU availability

🎯 Roadmap




Video upscaling integration




Custom model fine-tuning




Batch video generation




Video editing capabilities




Advanced style controls

