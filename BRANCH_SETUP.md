# 🌟 Branch Setup - Development vs Production

## 📋 **Branch Overview**

### **🔧 `normandy` Branch (Development)**
- **Purpose:** Local development and testing
- **Features:** Your current working setup with all functionality
- **API Mode:** Mixed (can include fallbacks for development)
- **Use Case:** Local development, testing, experimentation

### **🚀 `production` Branch (Real APIs Only)**
- **Purpose:** Railway deployment with real API integrations
- **Features:** Production-ready code with NO simulation
- **API Mode:** Real APIs only - no fallbacks or placeholders
- **Use Case:** Railway deployment, live production environment

## 🔄 **Current Setup**

### **Local Development (normandy branch):**
```bash
git checkout normandy
# Your current working code
# Includes all features and development tools
```

### **Production Deployment (production branch):**
```bash
git checkout production
# Real API integrations only
# No simulation or fallback code
# Strict API key validation
```

## 🚀 **Railway Deployment Instructions**

### **Step 1: Update Railway Backend**
1. Go to Railway dashboard → `upcom-backend` project
2. Go to **Settings** → **Source**
3. Change branch from `normandy` to `production`
4. Railway will automatically redeploy with real APIs

### **Step 2: Verify Environment Variables**
Ensure these are set in Railway backend:
```bash
OPENAI_API_KEY=your_key_here
HEYGEN_API_KEY=your_key_here
VIZARD_API_KEY=your_key_here
CREATOMATE_API_KEY=your_key_here
RAILWAY_ENVIRONMENT=true
```

### **Step 3: Monitor Deployment**
- Check Railway logs for "PRODUCTION MODE" messages
- Health check should show `"simulation": false`
- All API calls will be real (no example.com URLs)

## 🔍 **Key Differences**

### **Development Branch (normandy):**
- ✅ Local development friendly
- ✅ May include development helpers
- ✅ Your current working setup
- ⚠️ May have simulation code for testing

### **Production Branch (production):**
- ✅ Real API integrations only
- ✅ Strict validation and error handling
- ✅ No simulation or fallback URLs
- ✅ Production-optimized performance
- ❌ No development helpers or shortcuts

## 📊 **Verification**

### **Check if Production is Working:**
```bash
# Health check should show:
curl https://your-backend.railway.app/api/health

# Expected response:
{
  "status": "healthy",
  "mode": "PRODUCTION",
  "simulation": false,
  "environment": "production"
}
```

### **Development vs Production API Responses:**
- **Development:** May include placeholder URLs
- **Production:** Only real file paths and API responses

## 🛠️ **Maintenance**

### **Adding New Features:**
1. Develop and test in `normandy` branch
2. When ready for production, merge changes to `production` branch
3. Ensure no simulation code is included in production

### **Hotfixes:**
1. Apply fixes to both branches as needed
2. Test in `normandy` first
3. Deploy to `production` for live fixes

## 🎯 **Current Status**

- ✅ **Development Branch:** Ready for local work
- ✅ **Production Branch:** Ready for Railway deployment
- 🔄 **Next Step:** Update Railway to use `production` branch

Your local development environment remains unchanged while production gets real API integrations! 🎉
