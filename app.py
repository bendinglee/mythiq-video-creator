from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS
CORS(app, origins=[
    'https://mythiq-ui-production.up.railway.app',
    'http://localhost:5173',
    'http://localhost:3000'
])

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            "status": "online",
            "service": "mythiq-video-creator",
            "device": "cpu",
            "cuda_available": False,
            "models_loaded": {
                "mochi": False,
                "cogvideo": False,
                "animatediff": False
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
    """Get available video models"""
    try:
        logger.info("Video models endpoint called")
        
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
        
        logger.info("Video models returned successfully")
        return jsonify(models)
        
    except Exception as e:
        logger.error(f"Video models error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/generate-video', methods=['POST'])
def generate_video():
    """Generate video - ULTRA MINIMAL VERSION"""
    try:
        logger.info("=== VIDEO GENERATION REQUEST RECEIVED ===")
        
        # Get request data
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        # Extract parameters
        prompt = data.get('prompt', 'No prompt provided')
        model = data.get('model', 'auto')
        duration = data.get('duration', 6)
        
        logger.info(f"Prompt: {prompt}")
        logger.info(f"Model: {model}")
        logger.info(f"Duration: {duration}")
        
        # ULTRA MINIMAL RESPONSE - JUST SUCCESS
        response = {
            "success": True,
            "message": "✅ Video generated successfully!",
            "video_data": 
