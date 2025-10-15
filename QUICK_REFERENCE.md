# 🚀 Quick Reference - Development vs Production

## 🔧 Local Development (Testing New Features)

```bash
# 1. Start backend (development)
python3 start_development.py

# 2. Start frontend (in new terminal)
cd frontend
npm run dev

# 3. Test at:
# - Backend: http://localhost:8001
# - Frontend: http://localhost:3000
# - API Docs: http://localhost:8001/docs
```

## 🚀 Deploy to Railway Production

```bash
# When local testing is successful:
git add .
git commit -m "feat: your feature description"
git push origin production

# Railway auto-deploys from production branch
```

## 📋 Current Production Status

✅ **Railway is working perfectly with:**
- Comprehensive Steam App ID validation
- Real-time API verification  
- Enhanced error handling
- Smart template selection for Vizard
- All validation features active

## 🔍 Key Files

| Purpose | Development | Production |
|---------|-------------|------------|
| **API Server** | `api_server.py` | `api_server_production.py` |
| **Startup** | `start_development.py` | `railway_main.py` |
| **Environment** | `.env.development` | Railway dashboard |

## ⚠️ Important

- **Always test locally first** using development setup
- **Never confuse environments** - use correct startup scripts
- **Railway auto-deploys** when you push to production branch
- **Both environments have same validation features**

## 🎯 Validation Working Status

Both development and production now reject invalid Steam App IDs like "sdsdsd" with proper error messages instead of starting automation jobs.

**Current deployment is stable and production-ready! 🎉**
