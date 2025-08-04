🚀 Mythiq Video Creator - Deployment Guide

Complete step-by-step guide to deploy your advanced video generation service.

📋 Pre-Deployment Checklist

✅ Files Required

•
app.py - Main Flask application

•
requirements.txt - Python dependencies

•
railway.json - Railway configuration

•
README.md - Documentation

•
.gitignore - Git ignore file

•
test.py - Testing script

✅ Accounts Required

•
GitHub account (for repository)

•
Railway account (for deployment)

🎬 Step 1: Create GitHub Repository

1.1 Create Repository

Bash


# Go to GitHub and create new repository
Repository name: mythiq-video-creator
Description: Advanced AI video generation service
Visibility: Public or Private


1.2 Upload Files

Upload all provided files to your repository:

•
Rename mythiq_video_creator_gitignore.txt to .gitignore

•
Rename mythiq_video_creator_railway.json to railway.json

•
Rename mythiq_video_creator_app.py to app.py

•
Keep other files as provided

1.3 Verify Repository Structure

Plain Text


mythiq-video-creator/
├── app.py
├── requirements.txt
├── railway.json
├── README.md
├── .gitignore
└── test.py


🚂 Step 2: Deploy to Railway

2.1 Create Railway Project

1.
Go to Railway.app

2.
Click "New Project"

3.
Select "Deploy from GitHub repo"

4.
Choose your mythiq-video-creator repository

2.2 Configure Railway Settings

Railway will automatically:

•
✅ Detect Python project (from requirements.txt)

•
✅ Use configuration from railway.json

•
✅ Start build process

2.3 Monitor Deployment

Expected timeline:

•
Build: 10-15 minutes (installing dependencies)

•
Model Download: 20-30 minutes (first startup)

•
Total: 30-45 minutes for first deployment

Check deployment logs for:

Plain Text


✅ Installing dependencies...
✅ Starting Mythiq Video Creator...
✅ Device: cuda (or cpu)
✅ Video models will be loaded on first request


⚙️ Step 3: Configure Railway Resources

3.1 Upgrade Railway Plan

For optimal performance:

•
Plan: Pro ($20/month base)

•
Memory: 16GB+ recommended

•
CPU: High-performance plan

•
Storage: 32GB+ for models

3.2 Set Environment Variables (Optional)

Plain Text


CUDA_VISIBLE_DEVICES=0  # For multi-GPU systems


3.3 Monitor Resource Usage

•
Memory: 8-16GB during generation

•
CPU: High during model loading

•
Storage: 25GB for all models

•
Network: High during model downloads

🧪 Step 4: Test Your Deployment

4.1 Get Your Service URL

Railway will provide a URL like:

Plain Text


https://mythiq-video-creator-production.up.railway.app


4.2 Test Health Check

Bash


curl https://your-service-url.up.railway.app/health


Expected response:

JSON


{
  "status": "online",
  "service": "mythiq-video-creator",
  "device": "cuda",
  "cuda_available": true,
  "models_loaded": {
    "mochi": false,
    "cogvideo": false,
    "animatediff": false
  },
  "message": "Video generation service ready"
}


4.3 Run Test Script

Bash


# Update test.py with your Railway URL
python test.py https://your-service-url.up.railway.app


4.4 Test Video Generation

Bash


curl -X POST https://your-service-url.up.railway.app/generate-video \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cat playing with a ball", "duration": 6}'


🎯 Step 5: Frontend Integration

5.1 Add Environment Variable

In your mythiq-ui Railway service:

•
Variable: VITE_VIDEO_API

•
Value: https://mythiq-video-creator-production.up.railway.app

5.2 Update Frontend Code

Add Video Studio tab to your App.jsx:

JSX


// Add to your tab navigation
<button
  onClick={() => setActiveTab('video')}
  className={`px-6 py-3 rounded-lg font-medium transition-all ${
    activeTab === 'video'
      ? 'bg-red-600 text-white shadow-lg'
      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
  }`}
>
  🎬 Video Studio
</button>

// Add Video Studio component
{activeTab === 'video' && (
  <div className="space-y-6">
    <div className="text-center">
      <h2 className="text-2xl font-bold text-white mb-2">🎬 Video Studio</h2>
      <p className="text-gray-400">Generate videos with AI</p>
    </div>
    
    <div className="bg-gray-800 rounded-lg p-6">
      <h3 className="text-xl font-semibold text-white mb-4">🎥 Video Generation</h3>
      <textarea
        placeholder="Describe the video you want to create..."
        className="w-full p-3 bg-gray-700 text-white rounded-lg resize-none"
        rows="3"
      />
      <div className="mt-3 flex gap-3">
        <select className="p-2 bg-gray-700 text-white rounded">
          <option value="auto">Auto-detect</option>
          <option value="photorealistic">Photorealistic</option>
          <option value="creative">Creative</option>
          <option value="animation">Animation</option>
        </select>
        <select className="p-2 bg-gray-700 text-white rounded">
          <option value="6">6 seconds</option>
          <option value="4">4 seconds</option>
          <option value="2">2 seconds</option>
        </select>
        <button className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
          Generate Video
        </button>
      </div>
    </div>
  </div>
)}


🔍 Step 6: Troubleshooting

Common Issues & Solutions

❌ Build Failed

Symptoms: Railway build fails during dependency installation
Solutions:

•
Check requirements.txt for typos

•
Verify Python version compatibility

•
Check Railway build logs for specific errors

❌ Health Check Timeout

Symptoms: Service shows "Unhealthy" status
Solutions:

•
Increase healthcheck timeout in railway.json

•
Check if service is binding to 0.0.0.0:PORT

•
Monitor memory usage (may need more RAM)

❌ Model Loading Failed

Symptoms: Video generation returns errors
Solutions:

•
Check internet connectivity for model downloads

•
Verify sufficient storage space (25GB+)

•
Monitor Railway logs during first model load

❌ Out of Memory

Symptoms: Service crashes during video generation
Solutions:

•
Upgrade Railway plan to higher memory

•
Reduce video duration

•
Enable CPU offloading (already configured)

❌ Slow Generation

Symptoms: Video generation takes very long
Solutions:

•
Upgrade to GPU-enabled Railway plan

•
Reduce inference steps in code

•
Use shorter video durations

Performance Optimization

Memory Usage

Python


# Already implemented in app.py
- CPU offloading for models
- VAE slicing for memory efficiency
- Automatic memory cleanup
- Garbage collection after generation


Speed Optimization

Python


# Model-specific optimizations
- Mochi-1: 64 steps (highest quality)
- CogVideoX: 50 steps (balanced)
- AnimateDiff: 25 steps (fastest)


📊 Step 7: Monitor Performance

Railway Metrics

Monitor in Railway dashboard:

•
CPU Usage: Should spike during generation

•
Memory Usage: 8-16GB during active generation

•
Network: High during model downloads

•
Storage: 25GB+ for all models

Service Metrics

Check via /health endpoint:

•
Models Loaded: Track which models are ready

•
Device: Verify GPU availability

•
Response Times: Monitor generation speed

Cost Monitoring

Expected Railway costs:

•
Base Service: $20/month (Pro plan)

•
Memory (16GB): $30-50/month

•
CPU (High-performance): $20-40/month

•
Storage (32GB): $10-15/month

•
Total: $80-125/month

🎉 Step 8: Go Live!

Final Checklist

•
✅ Service deployed and healthy

•
✅ All models loading successfully

•
✅ Video generation working

•
✅ Frontend integration complete

•
✅ Error handling tested

•
✅ Performance monitoring setup

Launch Announcement

Your video service is now ready! Features include:

•
3 AI models for different video styles

•
Auto-detection of best model for prompts

•
High-quality generation up to 6 seconds

•
Professional API with comprehensive error handling

•
Seamless integration with your Mythiq platform

🚀 Next Steps

Immediate

1.
Test all video generation models

2.
Integrate with your frontend

3.
Monitor performance and costs

4.
Gather user feedback

Future Enhancements

1.
Video upscaling for higher resolution

2.
Batch processing for multiple videos

3.
Custom model fine-tuning

4.
Video editing capabilities

5.
Advanced style controls

📞 Support Resources

Railway Support

•
Railway documentation: docs.railway.app

•
Railway Discord: Community support

•
Railway status: status.railway.app

Model Documentation

•
Mochi-1: Genmo documentation

•
CogVideoX: THUDM GitHub

•
AnimateDiff: Diffusers documentation

Debugging

1.
Check Railway logs for detailed error messages

2.
Monitor resource usage in Railway dashboard

3.
Test locally if possible for faster debugging

4.
Use test script for systematic testing





🎬 Congratulations! You now have a world-cl

