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
    try:
        logger.info("Loading Mochi-1 model...")
        from diffusers import MochiPipeline
        import torch
        
        device = get_device()
        mochi_pipeline = MochiPipeline.from_pretrained(
            "genmo/mochi-1-preview", 
            variant="bf16", 
            torch_dtype=torch.bfloat16
        ).to(device)
        
        logger.info("Mochi-1 model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load Mochi-1 model: {str(e)}")
        return False

def load_cogvideo_model():
    """Load CogVideoX model for creative videos"""
    global cogvideo_pipeline
    try:
        logger.info("Loading CogVideoX model...")
        from diffusers import CogVideoXPipeline
        import torch
        
        device = get_device()
        cogvideo_pipeline = CogVideoXPipeline.from_pretrained(
            "THUDM/CogVideoX-5b", 
            torch_dtype=torch.bfloat16
        ).to(device)
        
        logger.info("CogVideoX model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load CogVideoX model: {str(e)}")
        return False

def load_animatediff_model():
    """Load AnimateDiff model for animations"""
    global animatediff_pipeline
    try:
        logger.info("Loading AnimateDiff model...")
        from diffusers import AnimateDiffPipeline, MotionAdapter
        import torch
        
        device = get_device()
        adapter = MotionAdapter.from_pretrained("guoyww/animatediff-motion-adapter-v1-5-2")
        animatediff_pipeline = AnimateDiffPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5", 
            motion_adapter=adapter,
            torch_dtype=torch.float16
        ).to(device)
        
        logger.info("AnimateDiff model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load AnimateDiff model: {str(e)}")
        return False

def detect_best_model(prompt):
    """Auto-detect the best model based on prompt content"""
    prompt_lower = prompt.lower()
    
    # Animation keywords
    animation_keywords = ['cartoon', 'anime', 'animated', 'character', 'illustration', 'drawing']
    if any(keyword in prompt_lower for keyword in animation_keywords):
        return 'animation'
    
    # Creative/artistic keywords
    creative_keywords = ['artistic', 'abstract', 'surreal', 'fantasy', 'creative', 'stylized']
    if any(keyword in prompt_lower for keyword in creative_keywords):
        return 'creative'
    
    # Default to photorealistic for everything else
    return 'photorealistic'

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        device = get_device()
        return jsonify({
            "status": "online",
            "service": "mythiq-video-creator",
            "device": device,
            "cuda_available": torch.cuda.is_available(),
            "models_loaded": {
                "mochi": mochi_pipeline is not None,
                "cogvideo": cogvideo_pipeline is not None,
                "animatediff": animatediff_pipeline is not None
            },
            "message": "Video generation service ready",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/video-models', methods=['GET'])
def get_video_models():
    """Get available video models and their capabilities"""
    models = {
        "success": True,
        "auto_detection": True,
        "models": {
            "photorealistic": {
                "name": "Mochi-1",
                "quality": "Highest",
                "max_duration": 6,
                "best_for": ["realistic", "people", "nature", "objects"]
            },
            "creative": {
                "name": "CogVideoX-5B",
                "quality": "High", 
                "max_duration": 6,
                "best_for": ["artistic", "abstract", "fantasy", "creative"]
            },
            "animation": {
                "name": "AnimateDiff",
                "quality": "High",
                "max_duration": 2,
                "best_for": ["cartoon", "anime", "character", "illustration"]
            }
        }
    }
    
    return jsonify(models)

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
        
        prompt = data['prompt']
        model_type = data.get('model', 'auto')
        duration = data.get('duration', 6)
        
        logger.info(f"Video generation request: {prompt[:50]}...")
        
        # Auto-detect model if needed
        if model_type == 'auto':
            model_type = detect_best_model(prompt)
            logger.info(f"Auto-detected model: {model_type}")
        
        # Load appropriate model
        with model_lock:
            if model_type == 'photorealistic':
                if mochi_pipeline is None:
                    logger.info("Loading Mochi-1 model for first time...")
                    if not load_mochi_model():
                        return jsonify({
                            "success": False,
                            "error": "Failed to load Mochi-1 model"
                        }), 500
                
                pipeline = mochi_pipeline
                model_name = "Mochi-1"
                
            elif model_type == 'creative':
                if cogvideo_pipeline is None:
                    logger.info("Loading CogVideoX model for first time...")
                    if not load_cogvideo_model():
                        return jsonify({
                            "success": False,
                            "error": "Failed to load CogVideoX model"
                        }), 500
                
                pipeline = cogvideo_pipeline
                model_name = "CogVideoX-5B"
                
            elif model_type == 'animation':
                if animatediff_pipeline is None:
                    logger.info("Loading AnimateDiff model for first time...")
                    if not load_animatediff_model():
                        return jsonify({
                            "success": False,
                            "error": "Failed to load AnimateDiff model"
                        }), 500
                
                pipeline = animatediff_pipeline
                model_name = "AnimateDiff"
                
            else:
                return jsonify({
                    "success": False,
                    "error": f"Unknown model type: {model_type}"
                }), 400
        
        # Generate video
        logger.info(f"Generating video with {model_name}...")
        
        try:
            if model_type == 'animation':
                # AnimateDiff uses different parameters
                video_frames = pipeline(
                    prompt=prompt,
                    num_frames=16,
                    guidance_scale=7.5,
                    num_inference_steps=25,
                    generator=torch.Generator().manual_seed(42)
                ).frames[0]
            else:
                # Mochi and CogVideoX
                video_frames = pipeline(
                    prompt=prompt,
                    num_frames=duration * 8,  # Approximate frames per second
                    guidance_scale=4.5,
                    num_inference_steps=64,
                    generator=torch.Generator().manual_seed(42)
                ).frames[0]
            
            # Convert to base64 for frontend
            # For now, return success message
            # TODO: Implement actual video encoding and base64 conversion
            
            cleanup_memory()
            
            return jsonify({
                "success": True,
                "message": f"Video generated successfully with {model_name}",
                "model_used": model_name,
                "duration": duration,
                "frames_generated": len(video_frames) if video_frames else 0,
                "video_data": "base64_video_data_placeholder",  # TODO: Implement actual encoding
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Video generation failed: {str(e)}")
            cleanup_memory()
            return jsonify({
                "success": False,
                "error": f"Video generation failed: {str(e)}"
            }), 500
            
    except Exception as e:
        logger.error(f"Request processing error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Request processing failed: {str(e)}"
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
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    app.run(host='0.0.0.0', port=port, debug=False)
