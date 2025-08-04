from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import torch
import gc
import base64
import io
import tempfile
from datetime import datetime
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS for your frontend
CORS(app, origins=[
    'https://mythiq-ui-production.up.railway.app',
    'http://localhost:5173',
    'http://localhost:3000'
])

# Global variables for models (lazy loading)
mochi_pipeline = None
cogvideo_pipeline = None
animatediff_pipeline = None
model_lock = threading.Lock()

def get_device():
    """Get the best available device"""
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"

def cleanup_memory():
    """Clean up GPU memory"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()

def load_mochi_model():
    """Load Mochi-1 model for photorealistic videos"""
    global mochi_pipeline
    
    if mochi_pipeline is not None:
        return mochi_pipeline
    
    try:
        logger.info("Loading Mochi-1 model...")
        from diffusers import MochiPipeline
        
        device = get_device()
        mochi_pipeline = MochiPipeline.from_pretrained(
            "genmo/mochi-1-preview",
            torch_dtype=torch.float16 if device != "cpu" else torch.float32,
            variant="fp16" if device != "cpu" else None
        )
        
        if device != "cpu":
            mochi_pipeline = mochi_pipeline.to(device)
            mochi_pipeline.enable_model_cpu_offload()
            mochi_pipeline.enable_vae_slicing()
        
        logger.info("Mochi-1 model loaded successfully")
        return mochi_pipeline
        
    except Exception as e:
        logger.error(f"Error loading Mochi-1 model: {str(e)}")
        return None

def load_cogvideo_model():
    """Load CogVideoX model for creative videos"""
    global cogvideo_pipeline
    
    if cogvideo_pipeline is not None:
        return cogvideo_pipeline
    
    try:
        logger.info("Loading CogVideoX model...")
        from diffusers import CogVideoXPipeline
        
        device = get_device()
        cogvideo_pipeline = CogVideoXPipeline.from_pretrained(
            "THUDM/CogVideoX-5b",
            torch_dtype=torch.float16 if device != "cpu" else torch.float32
        )
        
        if device != "cpu":
            cogvideo_pipeline = cogvideo_pipeline.to(device)
            cogvideo_pipeline.enable_model_cpu_offload()
            cogvideo_pipeline.enable_vae_slicing()
        
        logger.info("CogVideoX model loaded successfully")
        return cogvideo_pipeline
        
    except Exception as e:
        logger.error(f"Error loading CogVideoX model: {str(e)}")
        return None

def load_animatediff_model():
    """Load AnimateDiff model for animations"""
    global animatediff_pipeline
    
    if animatediff_pipeline is not None:
        return animatediff_pipeline
    
    try:
        logger.info("Loading AnimateDiff model...")
        from diffusers import AnimateDiffPipeline, MotionAdapter
        
        device = get_device()
        adapter = MotionAdapter.from_pretrained("guoyww/animatediff-motion-adapter-v1-5-2")
        
        animatediff_pipeline = AnimateDiffPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            motion_adapter=adapter,
            torch_dtype=torch.float16 if device != "cpu" else torch.float32
        )
        
        if device != "cpu":
            animatediff_pipeline = animatediff_pipeline.to(device)
            animatediff_pipeline.enable_model_cpu_offload()
            animatediff_pipeline.enable_vae_slicing()
        
        logger.info("AnimateDiff model loaded successfully")
        return animatediff_pipeline
        
    except Exception as e:
        logger.error(f"Error loading AnimateDiff model: {str(e)}")
        return None

def detect_video_style(prompt):
    """Detect the best model for the given prompt"""
    prompt_lower = prompt.lower()
    
    # Animation keywords
    animation_keywords = ['cartoon', 'anime', 'animated', 'character', 'mascot', 'illustration', 'drawing']
    if any(keyword in prompt_lower for keyword in animation_keywords):
        return 'animation'
    
    # Creative/artistic keywords
    creative_keywords = ['artistic', 'abstract', 'surreal', 'fantasy', 'magical', 'creative', 'stylized']
    if any(keyword in prompt_lower for keyword in creative_keywords):
        return 'creative'
    
    # Default to photorealistic
    return 'photorealistic'

def generate_video_with_model(prompt, model_type, duration=6):
    """Generate video using the specified model"""
    
    try:
        with model_lock:
            if model_type == 'photorealistic':
                pipeline = load_mochi_model()
                if pipeline is None:
                    raise Exception("Mochi-1 model failed to load")
                
                # Generate with Mochi-1
                video_frames = pipeline(
                    prompt=prompt,
                    num_frames=duration * 6,  # 6 fps for Mochi
                    guidance_scale=6.0,
                    num_inference_steps=64,
                    generator=torch.Generator().manual_seed(42)
                ).frames[0]
                
            elif model_type == 'creative':
                pipeline = load_cogvideo_model()
                if pipeline is None:
                    raise Exception("CogVideoX model failed to load")
                
                # Generate with CogVideoX
                video_frames = pipeline(
                    prompt=prompt,
                    num_frames=duration * 8,  # 8 fps for CogVideo
                    guidance_scale=6.0,
                    num_inference_steps=50,
                    generator=torch.Generator().manual_seed(42)
                ).frames[0]
                
            elif model_type == 'animation':
                pipeline = load_animatediff_model()
                if pipeline is None:
                    raise Exception("AnimateDiff model failed to load")
                
                # Generate with AnimateDiff
                video_frames = pipeline(
                    prompt=prompt,
                    num_frames=16,  # Fixed 16 frames for AnimateDiff
                    guidance_scale=7.5,
                    num_inference_steps=25,
                    generator=torch.Generator().manual_seed(42)
                ).frames[0]
            
            else:
                raise Exception(f"Unknown model type: {model_type}")
        
        # Clean up memory after generation
        cleanup_memory()
        
        return video_frames
        
    except Exception as e:
        cleanup_memory()
        raise e

def frames_to_video_base64(frames):
    """Convert frames to base64 encoded video"""
    try:
        import cv2
        import numpy as np
        
        # Create temporary file for video
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        # Convert PIL frames to numpy arrays
        frame_arrays = []
        for frame in frames:
            frame_array = np.array(frame)
            frame_array = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
            frame_arrays.append(frame_array)
        
        # Write video
        height, width = frame_arrays[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_path, fourcc, 8.0, (width, height))
        
        for frame in frame_arrays:
            out.write(frame)
        out.release()
        
        # Read video file and encode to base64
        with open(temp_path, 'rb') as video_file:
            video_data = video_file.read()
            video_base64 = base64.b64encode(video_data).decode('utf-8')
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return f"data:video/mp4;base64,{video_base64}"
        
    except Exception as e:
        logger.error(f"Error converting frames to video: {str(e)}")
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        device = get_device()
        return jsonify({
            "status": "online",
            "service": "mythiq-video-creator",
            "timestamp": datetime.now().isoformat(),
            "device": device,
            "cuda_available": torch.cuda.is_available(),
            "models_loaded": {
                "mochi": mochi_pipeline is not None,
                "cogvideo": cogvideo_pipeline is not None,
                "animatediff": animatediff_pipeline is not None
            },
            "message": "Video generation service ready"
        })
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/generate-video', methods=['POST'])
def generate_video():
    """Generate video from text prompt"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'prompt' in request"
            }), 400
        
        prompt = data['prompt'].strip()
        if not prompt:
            return jsonify({
                "success": False,
                "error": "Empty prompt provided"
            }), 400
        
        # Get optional parameters
        duration = min(int(data.get('duration', 6)), 10)  # Max 10 seconds
        model_type = data.get('model_type', 'auto')
        
        # Auto-detect model if not specified
        if model_type == 'auto':
            model_type = detect_video_style(prompt)
        
        logger.info(f"Generating video: '{prompt}' with {model_type} model")
        
        # Generate video
        video_frames = generate_video_with_model(prompt, model_type, duration)
        
        # Convert to base64 video
        video_base64 = frames_to_video_base64(video_frames)
        
        if video_base64:
            return jsonify({
                "success": True,
                "video_data": video_base64,
                "model_used": model_type,
                "duration": duration,
                "prompt": prompt,
                "timestamp": datetime.now().isoformat(),
                "message": f"Video generated successfully using {model_type} model"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to encode video"
            }), 500
            
    except Exception as e:
        logger.error(f"Video generation error: {str(e)}")
        cleanup_memory()
        return jsonify({
            "success": False,
            "error": f"Video generation failed: {str(e)}"
        }), 500

@app.route('/video-models', methods=['GET'])
def get_video_models():
    """Get available video generation models"""
    models = {
        "photorealistic": {
            "name": "Mochi-1",
            "description": "Best for photorealistic videos",
            "max_duration": 6,
            "quality": "Highest",
            "best_for": ["realistic", "people", "nature", "objects"]
        },
        "creative": {
            "name": "CogVideoX-5B",
            "description": "Best for creative and artistic videos",
            "max_duration": 6,
            "quality": "High",
            "best_for": ["artistic", "abstract", "fantasy", "creative"]
        },
        "animation": {
            "name": "AnimateDiff",
            "description": "Best for animated and cartoon videos",
            "max_duration": 2,
            "quality": "High",
            "best_for": ["cartoon", "anime", "character", "illustration"]
        }
    }
    
    return jsonify({
        "success": True,
        "models": models,
        "auto_detection": True,
        "message": "Available video generation models"
    })

@app.route('/generate-video-preview', methods=['POST'])
def generate_video_preview():
    """Generate a quick preview (placeholder for now)"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        model_type = detect_video_style(prompt)
        
        return jsonify({
            "success": True,
            "preview": f"Preview: {prompt[:50]}...",
            "recommended_model": model_type,
            "estimated_time": "30-60 seconds",
            "message": "Preview generated - ready for full video generation"
        })
        
    except Exception as e:
        logger.error(f"Preview generation error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Mythiq Video Creator on port {port}")
    logger.info(f"Device: {get_device()}")
    logger.info("Video models will be loaded on first request")
    
    app.run(host='0.0.0.0', port=port, debug=False)
