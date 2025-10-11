# 🚀 Railway Deployment Guide

## ✅ Current Working Configuration Preserved

Your local working settings have been saved and configured for Railway deployment. All configurations will remain **exactly as they are** when deployed.

## 📁 Files Created for Railway Deployment

### Backend Configuration
- `railway_main.py` - Railway entry point (preserves your current API server)
- `requirements-railway.txt` - Railway-compatible dependencies
- `railway.toml` - Railway deployment configuration
- `Procfile` - Process configuration for Railway

### Frontend Configuration
- `frontend/env.production` - Production environment template
- Updated `frontend/next.config.js` - Handles both local and production environments

## 🔧 Environment Variables to Set in Railway

### Backend Service
Set these in your Railway backend project dashboard:

```bash
# Required API Keys (copy from your .env file)
OPENAI_API_KEY=your_openai_key_here
HEYGEN_API_KEY=your_heygen_key_here
VIZARD_API_KEY=your_vizard_key_here
CREATOMATE_API_KEY=your_creatomate_key_here

# Optional (if using Cloudinary)
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# Railway will automatically set PORT
```

### Frontend Service
Set these in your Railway frontend project dashboard:

```bash
# These will be set automatically by Railway based on your backend URL
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app/api
NEXT_PUBLIC_WS_URL=wss://your-backend-url.railway.app/ws
```

## 📋 Deployment Steps

### Step 1: Deploy Backend
1. Create new Railway project for backend
2. Connect your repository
3. Set root directory to: `/` (project root)
4. Railway will automatically detect `railway.toml`
5. Add all environment variables from your `.env` file
6. Deploy and note the backend URL

### Step 2: Deploy Frontend
1. Create new Railway project for frontend
2. Connect the same repository
3. Set root directory to: `/frontend`
4. Set environment variables with your backend URL
5. Deploy

### Step 3: Update Frontend Environment
After backend is deployed, update frontend environment variables:
```bash
NEXT_PUBLIC_API_URL=https://your-actual-backend-url.railway.app/api
NEXT_PUBLIC_WS_URL=wss://your-actual-backend-url.railway.app/ws
```

## 🔒 Settings Preservation

✅ **API Configuration**: Preserved exactly as your local setup
✅ **CORS Settings**: Updated to work with both local and Railway
✅ **WebSocket Connections**: Configured for both environments
✅ **Environment Variables**: Template created for easy Railway setup
✅ **Dependencies**: Railway-compatible versions maintained
✅ **Entry Points**: Dedicated Railway entry point preserves all settings

## 🚨 Important Notes

1. **Environment Variables**: Copy ALL your API keys from `.env` to Railway dashboard
2. **Two Services**: Deploy backend and frontend as separate Railway services
3. **URLs**: Update frontend environment variables with actual backend URL after deployment
4. **Local Development**: Your local setup remains unchanged and will continue working

## 🧪 Testing After Deployment

1. Test backend health: `https://your-backend-url.railway.app/api/health`
2. Test frontend: `https://your-frontend-url.railway.app`
3. Verify WebSocket connection in browser console
4. Test automation with a Steam App ID

Your current working configuration is now ready for Railway deployment! 🎉
