# YouTube Reels Automation for Gaming Content

An automated system that creates engaging YouTube Reels for upcoming games using AI-powered content generation.

## 🎯 Overview

This system automatically generates YouTube Reels (9:16 vertical format) for upcoming games by:

1. **Module 1 - Intro**: Generates engaging intro scripts with OpenAI and creates voice-over videos with HeyGen
2. **Module 2 - Vizard**: Processes gameplay footage using Vizard AI for highlights and clips
3. **Module 3 - Outro**: Creates compelling outro with call-to-actions using OpenAI + HeyGen
4. **Module 4 - Compilation**: Combines all elements into a final reel using CreatorMate/Creatomate

## 🚀 Features

- **Automated Game Discovery**: Scrapes Steam for upcoming and most-wished games
- **AI Script Generation**: Uses OpenAI GPT-4 for engaging intro/outro scripts
- **Professional Voice-Over**: HeyGen AI avatars and voices
- **Smart Video Processing**: Vizard AI for gameplay highlight extraction
- **Professional Compilation**: CreatorMate for seamless video assembly
- **Vertical Format**: Optimized 1080x1920 for YouTube Shorts/Reels
- **Batch Processing**: Create multiple reels automatically
- **Fallback Systems**: Robust error handling with backup options

## 📋 Prerequisites

### API Keys Required
- **OpenAI API Key**: For script generation
- **HeyGen API Key**: For avatar and voice-over generation
- **Vizard API Key**: For gameplay video processing
- **Creatomate API Key**: For final video compilation

### System Requirements
- Python 3.8+
- Chrome/Chromium browser (for web scraping)
- FFmpeg (for video processing)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd youtube-reels-automation
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   Copy the `.env` file and update with your API keys:
   ```bash
   cp .env.example .env
   ```
   
   Update the following in `.env`:
   ```env
   OPENAI_API_KEY=your_openai_key_here
   HEYGEN_API_KEY=your_heygen_key_here
   VIZARD_API_KEY=your_vizard_key_here
   CREATOMATE_API_KEY=your_creatomate_key_here
   ```

4. **Create directories**:
   ```bash
   python -c "from config import Config; Config.ensure_directories()"
   ```

## 🎮 Usage

### Basic Usage

**Create reels for trending games**:
```bash
python main.py
```
This will create 3 reels for the most popular upcoming games.

**Create reel for specific game**:
```bash
python main.py "Cyberpunk 2077"
python main.py "The Elder Scrolls VI"
```

### Advanced Usage

**Create multiple reels programmatically**:
```python
import asyncio
from main import YouTubeReelsAutomation

async def create_custom_reels():
    automation = YouTubeReelsAutomation()
    
    # Create 5 reels from trending games
    reels = await automation.run_automation(count=5)
    
    # Create reel for specific game
    specific_reel = await automation.run_automation(game_title="Starfield")
    
    automation.print_summary(reels + [specific_reel])

asyncio.run(create_custom_reels())
```

## 📁 Project Structure

```
youtube-reels-automation/
├── main.py                 # Main orchestrator script
├── config.py              # Configuration and settings
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API keys)
├── README.md             # This file
├── utils/
│   └── steam_scraper.py  # Steam data scraping utilities
├── modules/
│   ├── module1_intro.py      # Intro generation (OpenAI + HeyGen)
│   ├── module2_vizard.py     # Vizard gameplay processing
│   ├── module3_outro.py      # Outro generation (OpenAI + HeyGen)
│   └── module4_compilation.py # CreatorMate compilation
├── data/
│   ├── assets/
│   │   ├── intros/       # Generated intro videos
│   │   ├── vizard/       # Processed gameplay clips
│   │   └── outros/       # Generated outro videos
│   └── outputs/
│       └── final_reels/  # Final compiled reels
└── logs/                 # Application logs
```

## 🔧 Configuration

### Video Settings
- **Resolution**: 1080x1920 (9:16 aspect ratio)
- **Frame Rate**: 30 FPS
- **Format**: MP4

### Timing Structure
- **Intro**: ~15 seconds
- **Gameplay**: ~30 seconds  
- **Outro**: ~10 seconds
- **Total**: ~55 seconds (perfect for YouTube Shorts)

### API Endpoints
All API configurations are in `config.py`:
- OpenAI: GPT-4 for script generation
- HeyGen: Avatar and voice synthesis
- Vizard: AI video processing
- Creatomate: Professional video compilation

## 📊 Output

Generated reels will be saved in:
```
data/outputs/final_reels/
├── Game_Title_final_reel.mp4
├── Another_Game_simple_reel.mp4
└── ...
```

Each reel includes:
- ✅ Engaging intro with AI-generated script
- ✅ Highlight gameplay footage
- ✅ Call-to-action outro
- ✅ Professional transitions
- ✅ Optimized for mobile viewing

## 🎯 Workflow

1. **Game Discovery**: Scrapes Steam for trending upcoming games
2. **Content Planning**: Extracts game details, descriptions, and metadata
3. **Script Generation**: Creates engaging intro/outro scripts with OpenAI
4. **Voice Generation**: Produces professional voice-overs with HeyGen
5. **Video Processing**: Extracts gameplay highlights with Vizard AI
6. **Compilation**: Assembles final reel with CreatorMate
7. **Output**: Delivers ready-to-upload YouTube Reel

## 🚨 Error Handling

The system includes robust fallback mechanisms:
- **HeyGen Failure**: Falls back to text-based videos
- **Vizard Failure**: Creates placeholder gameplay clips
- **Creatomate Failure**: Uses simple concatenation
- **API Limits**: Implements rate limiting and retry logic

## 📈 Optimization Tips

1. **API Credits**: Monitor usage to avoid unexpected costs
2. **Batch Processing**: Run multiple games at once for efficiency
3. **Quality Control**: Review generated content before uploading
4. **Scheduling**: Use during off-peak hours for better API performance

## 🔍 Troubleshooting

**Common Issues**:

1. **Chrome Driver Issues**:
   ```bash
   pip install --upgrade webdriver-manager
   ```

2. **API Key Errors**:
   - Verify all API keys in `.env`
   - Check API credit balances
   - Ensure proper permissions

3. **Video Processing Failures**:
   - Check FFmpeg installation
   - Verify input video formats
   - Monitor disk space

4. **Steam Scraping Issues**:
   - Check internet connection
   - Verify Steam website accessibility
   - Update scraping selectors if needed

## 📝 Logging

All operations are logged to:
- Console output (real-time)
- `logs/automation_YYYY-MM-DD_HH-MM-SS.log`

Log levels: INFO, WARNING, ERROR

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error details
3. Open an issue with detailed description
4. Include relevant log snippets

---

**Happy Reel Creating! 🎬🎮**
# Force Railway redeploy with validation fixes - Wed Oct 15 18:01:05 PST 2025
