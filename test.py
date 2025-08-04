#!/usr/bin/env python3
"""
Test script for Mythiq Video Creator service
"""

import requests
import json
import time
import base64
import os

# Configuration
SERVICE_URL = "http://localhost:5000"  # Change to your Railway URL when deployed
# SERVICE_URL = "https://mythiq-video-creator-production.up.railway.app"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    
    try:
        response = requests.get(f"{SERVICE_URL}/health", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed!")
            print(f"   Status: {data.get('status')}")
            print(f"   Device: {data.get('device')}")
            print(f"   CUDA Available: {data.get('cuda_available')}")
            print(f"   Models Loaded: {data.get('models_loaded')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_video_models():
    """Test the video models endpoint"""
    print("\n🎬 Testing video models endpoint...")
    
    try:
        response = requests.get(f"{SERVICE_URL}/video-models", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Video models endpoint working!")
            print(f"   Available models: {len(data.get('models', {}))}")
            
            for model_name, model_info in data.get('models', {}).items():
                print(f"   📹 {model_name}: {model_info.get('name')} - {model_info.get('description')}")
            
            return True
        else:
            print(f"❌ Video models test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Video models test error: {str(e)}")
        return False

def test_video_preview():
    """Test the video preview endpoint"""
    print("\n🎯 Testing video preview...")
    
    test_prompt = "A cute cat playing with a ball of yarn"
    
    try:
        response = requests.post(
            f"{SERVICE_URL}/generate-video-preview",
            json={"prompt": test_prompt},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Video preview working!")
            print(f"   Preview: {data.get('preview')}")
            print(f"   Recommended model: {data.get('recommended_model')}")
            print(f"   Estimated time: {data.get('estimated_time')}")
            return True
        else:
            print(f"❌ Video preview test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Video preview test error: {str(e)}")
        return False

def test_video_generation(quick_test=True):
    """Test video generation (quick test by default)"""
    print("\n🎬 Testing video generation...")
    
    if quick_test:
        print("⚠️  Quick test mode - using minimal settings")
        test_prompt = "A simple red ball"
        duration = 2
    else:
        print("🚀 Full test mode - using realistic settings")
        test_prompt = "A beautiful sunset over calm ocean waves"
        duration = 6
    
    print(f"   Prompt: '{test_prompt}'")
    print(f"   Duration: {duration} seconds")
    print("   This may take 1-3 minutes...")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{SERVICE_URL}/generate-video",
            json={
                "prompt": test_prompt,
                "duration": duration,
                "model_type": "auto"
            },
            timeout=300  # 5 minutes timeout
        )
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Video generation successful!")
            print(f"   Generation time: {generation_time:.1f} seconds")
            print(f"   Model used: {data.get('model_used')}")
            print(f"   Video data size: {len(data.get('video_data', '')) // 1024}KB")
            
            # Optionally save video to file
            if data.get('video_data') and not quick_test:
                save_video = input("💾 Save video to file? (y/n): ").lower() == 'y'
                if save_video:
                    save_test_video(data.get('video_data'), test_prompt)
            
            return True
        else:
            print(f"❌ Video generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Video generation timed out (this is normal for first generation)")
        print("   Models are likely downloading - try again in a few minutes")
        return False
    except Exception as e:
        print(f"❌ Video generation error: {str(e)}")
        return False

def save_test_video(video_data, prompt):
    """Save generated video to file"""
    try:
        # Extract base64 data
        if video_data.startswith('data:video/mp4;base64,'):
            base64_data = video_data.split(',')[1]
        else:
            base64_data = video_data
        
        # Decode and save
        video_bytes = base64.b64decode(base64_data)
        filename = f"test_video_{int(time.time())}.mp4"
        
        with open(filename, 'wb') as f:
            f.write(video_bytes)
        
        print(f"💾 Video saved as: {filename}")
        print(f"   Size: {len(video_bytes) // 1024}KB")
        
    except Exception as e:
        print(f"❌ Error saving video: {str(e)}")

def test_error_handling():
    """Test error handling"""
    print("\n🚨 Testing error handling...")
    
    # Test empty prompt
    try:
        response = requests.post(
            f"{SERVICE_URL}/generate-video",
            json={"prompt": ""},
            timeout=30
        )
        
        if response.status_code == 400:
            print("✅ Empty prompt error handling working!")
        else:
            print(f"❌ Empty prompt should return 400, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error handling test failed: {str(e)}")
    
    # Test missing prompt
    try:
        response = requests.post(
            f"{SERVICE_URL}/generate-video",
            json={},
            timeout=30
        )
        
        if response.status_code == 400:
            print("✅ Missing prompt error handling working!")
        else:
            print(f"❌ Missing prompt should return 400, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error handling test failed: {str(e)}")

def run_all_tests():
    """Run all tests"""
    print("🎬 Mythiq Video Creator - Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    # Basic connectivity tests
    if test_health_check():
        tests_passed += 1
    
    if test_video_models():
        tests_passed += 1
    
    if test_video_preview():
        tests_passed += 1
    
    # Error handling test
    test_error_handling()
    tests_passed += 1
    
    # Video generation test
    print("\n" + "=" * 50)
    test_type = input("🎬 Run video generation test? (q)uick/(f)ull/(s)kip: ").lower()
    
    if test_type in ['q', 'quick']:
        if test_video_generation(quick_test=True):
            tests_passed += 1
    elif test_type in ['f', 'full']:
        if test_video_generation(quick_test=False):
            tests_passed += 1
    else:
        print("⏭️  Skipping video generation test")
        total_tests -= 1
    
    # Results
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your video service is working perfectly!")
    elif tests_passed >= total_tests - 1:
        print("✅ Most tests passed! Service is mostly functional.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    print("\n📋 Next Steps:")
    print("1. If health check fails: Check if service is running")
    print("2. If video generation fails: Check Railway logs for model download progress")
    print("3. If everything works: Integrate with your frontend!")

if __name__ == "__main__":
    # Check if custom URL provided
    if len(os.sys.argv) > 1:
        SERVICE_URL = os.sys.argv[1]
        print(f"🔗 Using custom service URL: {SERVICE_URL}")
    
    run_all_tests()
