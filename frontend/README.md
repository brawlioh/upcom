# 🎬 YouTube Reels Automation - Complete Setup Guide

A comprehensive guide to run the YouTube Reels automation pipeline using both the **Web UI** and **Command Line**.

## 🚀 Quick Start Options

### Option 1: Web UI (Recommended for Beginners)
**Easy-to-use web interface with real-time progress tracking**
- Start API server → Start frontend → Use browser interface

### Option 2: Command Line (Advanced Users)
**Direct Python script execution with full control**
- Start webhook → Run main.py → Follow prompts

## ⚡ **TL;DR - Fastest Setup**

```bash
# Terminal 1: Start webhook (optional but recommended)
python3 start_webhook.py

# Terminal 2: Run automation directly
python3 main.py
# OR start web UI:
python3 api_server.py  # Backend
cd frontend && npm run dev  # Frontend
```

---

## 🌐 **METHOD 1: Using the Web UI**

### **Step 1: Start the Backend API Server**
```bash
# Navigate to project root
cd /Users/brawlioh/Documents/_9_30_upcom

# Start the API server (handles automation requests)
python3 api_server.py
```
**✅ Server will start on:** `http://localhost:8000`

### **Step 2: Start the Webhook System (Optional but Recommended)**
```bash
# In a new terminal window
python3 start_webhook.py
```
**✅ This enables faster Vizard processing via webhooks**

### **Step 3: Start the Frontend UI**
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start the web interface
npm run dev
```
**✅ Web UI will open at:** `http://localhost:3000`

### **Step 4: Use the Web Interface**

1. **Open your browser** → `http://localhost:3000`
2. **Enter Steam App ID:**
   - 🆔 **Steam App ID**: Enter Steam ID (e.g., `1962700`)
3. **Optional: Custom Video URL**
   - Provide YouTube/Steam video URL
   - System auto-converts YouTube Shorts
4. **Click "Start Automation"**
5. **Watch real-time progress** through 4 modules:
   - 📹 Module 1: Intro Generation
   - 🎮 Module 2: Gameplay Clips  
   - 🎬 Module 3: Outro Generation
   - 🎞️ Module 4: Final Compilation

---

## 💻 **METHOD 2: Using Command Line**

### **Step 1: Start Webhook System (Recommended)**
```bash
# Terminal 1: Start webhook for faster processing
python3 start_webhook.py
```

### **Step 2: Run the Main Script**
```bash
# Terminal 2: Run automation
python3 main.py
```

### **Step 3: Follow Interactive Prompts**

**Steam App ID Mode:**
```
🎬 YOUTUBE REELS AUTOMATION SYSTEM
Steam App ID Mode - Enter a Steam App ID to create a reel
```

**Enter Steam App ID:**
```
🎯 Enter Steam App ID (numbers only, e.g., '1962700'): 1962700
✅ Found: Subnautica 2
📅 Release Date: 2026
👨‍💻 Developer: Unknown Worlds Entertainment
```

**Choose Video Source:**
```
📹 Video Source Options:
1. Use Steam videos (automatic)
2. Provide custom video URL
Choose video source (1 or 2, default=1): 2

📝 Supported video platforms:
   • YouTube: https://www.youtube.com/watch?v=...
   • YouTube Shorts: https://www.youtube.com/shorts/... (auto-converted)

🔗 Enter video URL: https://www.youtube.com/watch?v=example
❓ Does this video contain 'Subnautica 2' gameplay? (y/n, default=y): y
```

---

## 📋 **Pipeline Overview**

The automation creates YouTube Shorts through 4 modules:

| Module | Process | Duration | Output |
|--------|---------|----------|---------|
| **1. Intro** | AI avatar + script generation | ~2-3 min | Intro video with release date |
| **2. Gameplay** | Video processing with Vizard | ~5-10 min | Gameplay clips (30-60s) |
| **3. Outro** | AI avatar + call-to-action | ~2-3 min | Outro with subscribe prompt |
| **4. Compilation** | Final video assembly | ~1-2 min | Complete YouTube Short |

**Total Time:** ~10-18 minutes per reel

---

## 🔧 **Configuration & Requirements**

### **Required API Keys** (in `.env` file):
```bash
OPENAI_API_KEY=your_openai_key
HEYGEN_API_KEY=your_heygen_key  
VIZARD_API_KEY=your_vizard_key
CREATOMATE_API_KEY=your_creatomate_key
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_key
CLOUDINARY_API_SECRET=your_cloudinary_secret
```

### **Python Dependencies:**
```bash
pip install -r requirements.txt
```

### **Node.js Dependencies:**
```bash
cd frontend && npm install
```

---

## 📁 **Output Locations**

**Generated Files:**
- **Final Reels:** `docker_volumes/outputs/final_reels/`
- **Intro Videos:** `docker_volumes/assets/intros/`
- **Gameplay Clips:** `docker_volumes/assets/vizard/`
- **Outro Videos:** `docker_volumes/assets/outros/`
- **Logs:** `logs/automation_*.log`

---

## 🚨 **Troubleshooting**

### **Common Issues:**

**1. "Invalid video link" Error:**
- ✅ Use regular YouTube URLs: `https://www.youtube.com/watch?v=...`
- ❌ Avoid YouTube Shorts: `https://www.youtube.com/shorts/...` (auto-converted)

**2. Webhook Timeout:**
- Start webhook system: `python3 start_webhook.py`
- System auto-falls back to polling if webhook fails

**3. API Rate Limits:**
- Check API key quotas (OpenAI, HeyGen, Vizard)
- Wait between requests if hitting limits

**4. Missing Dependencies:**
- Run: `pip install -r requirements.txt`
- For frontend: `cd frontend && npm install`

---

## 🎯 **Best Practices**

### **For Best Results:**
1. **Use Steam App IDs** for accurate game data
2. **Verify custom video URLs** match the game content
3. **Start webhook system** for faster processing
4. **Check API quotas** before bulk processing
5. **Monitor logs** for detailed error information

### **Recommended Workflow:**
1. Start webhook system (`python3 start_webhook.py`)
2. Use Web UI for ease or CLI for control
3. Verify video content matches game
4. Monitor progress through real-time updates
5. Check output in `docker_volumes/outputs/final_reels/`

---

## 📞 **Support**

**Log Files:** Check `logs/automation_*.log` for detailed error information
**Configuration:** Verify `.env` file has all required API keys
**Updates:** Pull latest changes from repository before running
