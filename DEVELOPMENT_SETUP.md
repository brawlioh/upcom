# Development vs Production Setup Guide

This guide ensures clear separation between local development and Railway production environments.

## 🔧 Local Development Setup

### 1. Environment Configuration
```bash
# Copy the development template
cp env.development.template .env.development

# Edit with your local settings
nano .env.development
```

### 2. Start Development Server
```bash
# Option 1: Use the development startup script
python3 start_development.py

# Option 2: Traditional method
python3 api_server.py
```

### 3. Start Frontend (Development)
```bash
cd frontend
npm run dev
```

**Development URLs:**
- Backend API: `http://localhost:8001`
- Frontend: `http://localhost:3000`
- API Docs: `http://localhost:8001/docs`

## 🚀 Railway Production

### Current Working Configuration
- **Entry Point**: `railway_main.py`
- **API Server**: `api_server_production.py`
- **Environment**: Production variables set in Railway dashboard
- **Validation**: ✅ Comprehensive Steam App ID validation
- **Error Handling**: ✅ User-friendly error messages

### Production URLs
- Backend: `https://your-railway-backend.railway.app`
- Frontend: `https://your-railway-frontend.railway.app`

## 📋 Development Workflow

### Testing New Features Locally

1. **Make changes** to your code
2. **Test locally** using development setup:
   ```bash
   python3 start_development.py
   ```
3. **Verify everything works** with validation, error handling, etc.
4. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: your new feature description"
   ```
5. **Push to production** when ready:
   ```bash
   git push origin production
   ```

### Key Differences

| Aspect | Development | Production |
|--------|-------------|------------|
| **API Server** | `api_server.py` | `api_server_production.py` |
| **Entry Point** | `start_development.py` | `railway_main.py` |
| **Host** | `127.0.0.1` (local only) | `0.0.0.0` (public) |
| **Reload** | ✅ Auto-reload | ❌ No reload |
| **Debug** | ✅ Debug mode | ❌ Production mode |
| **Environment** | `.env.development` | Railway env vars |

## 🔍 Validation System Status

Both environments now have:
- ✅ **Steam App ID validation** with real-time API checks
- ✅ **YouTube URL validation** for custom videos
- ✅ **Enhanced error handling** with user-friendly messages
- ✅ **Request validation** at multiple levels
- ✅ **Validation endpoint** for testing Steam App IDs

## 🚨 Important Notes

1. **Never mix environments** - always use the correct startup method
2. **Test locally first** - verify all features work before pushing to production
3. **Keep API keys secure** - use different keys for development if possible
4. **Railway auto-deploys** - pushing to `production` branch triggers deployment
5. **Both environments validated** - same validation features in dev and prod

## 🛠️ Troubleshooting

### If validation doesn't work locally:
- Ensure you're using `api_server.py` (not production version)
- Check that all validation functions are present
- Verify environment variables are loaded

### If Railway deployment fails:
- Check Railway build logs
- Ensure `api_server_production.py` has all latest features
- Verify all environment variables are set in Railway dashboard

## 📞 Quick Commands

```bash
# Start local development
python3 start_development.py

# Start local frontend  
cd frontend && npm run dev

# Deploy to Railway
git push origin production

# Check Railway logs
# (Use Railway dashboard)
```
