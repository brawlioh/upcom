# 🚀 Fresh Railway Deployment Setup

## 📋 **Step-by-Step Guide for New Railway Projects**

### **🔧 Step 1: Create New Backend Project**

1. **Go to Railway Dashboard** → **New Project**
2. **Project Name:** `upcom-backend-v2` (or similar)
3. **Connect GitHub Repository:**
   - Repository: `brawlioh/upcom`
   - Branch: `production`
   - Root Directory: `/` (leave empty for root)

4. **Environment Variables to Set:**
```bash
# Required API Keys
OPENAI_API_KEY=your_openai_key_here
HEYGEN_API_KEY=your_heygen_key_here
VIZARD_API_KEY=your_vizard_key_here
CREATOMATE_API_KEY=your_creatomate_key_here

# Optional Cloud Storage
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# Railway Environment
RAILWAY_ENVIRONMENT=true
```

5. **Deploy Settings:**
   - Railway will auto-detect Python and use `railway.toml`
   - Start Command: `python railway_main.py`
   - Health Check: `/api/health`

### **🎨 Step 2: Create New Frontend Project**

1. **Go to Railway Dashboard** → **New Project**
2. **Project Name:** `upcom-frontend-v2` (or similar)
3. **Connect GitHub Repository:**
   - Repository: `brawlioh/upcom`
   - Branch: `production`
   - Root Directory: `frontend`

4. **Environment Variables to Set:**
```bash
# API URLs (update with your NEW backend URL)
NEXT_PUBLIC_API_URL=https://your-new-backend-url.railway.app/api
NEXT_PUBLIC_WS_URL=wss://your-new-backend-url.railway.app/ws

# App Configuration
NEXT_PUBLIC_APP_NAME="YouTube Reels Automation"
NEXT_PUBLIC_APP_VERSION="1.0.0"
```

### **🔄 Step 3: Update Frontend Environment After Backend Deploy**

1. **Wait for backend to deploy** and get the new URL
2. **Update frontend environment variables** with the actual backend URL
3. **Redeploy frontend**

### **✅ Step 4: Verification**

**Backend Health Check:**
```bash
curl https://your-new-backend-url.railway.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "mode": "PRODUCTION",
  "simulation": false,
  "environment": "production"
}
```

**Frontend Test:**
- Visit your new frontend URL
- Should show "Connected" status
- Try running an automation job

### **🗑️ Step 5: Clean Up Old Projects (Optional)**

Once new projects are working:
1. Delete old `upcom-backend` project
2. Delete old `upcom-frontend` project
3. Update any bookmarks/links

## 🎯 **Benefits of Fresh Projects**

- ✅ **Clean Environment** - No cached configurations
- ✅ **Latest Code** - Uses production branch with all fixes
- ✅ **Fresh Build** - No old dependencies or conflicts
- ✅ **Better Debugging** - Clear logs from start
- ✅ **Proper Configuration** - All settings applied correctly

## 🚨 **Important Notes**

1. **API Keys:** Make sure to copy all your API keys to the new projects
2. **Branch:** Both projects should use `production` branch
3. **Root Directory:** Backend uses `/`, Frontend uses `/frontend`
4. **Environment Variables:** Frontend URLs must match actual backend URL

## 📊 **Expected Timeline**

- Backend deployment: ~5-10 minutes
- Frontend deployment: ~3-5 minutes
- Total setup time: ~15-20 minutes

This fresh start should resolve any persistent configuration or caching issues! 🎉
