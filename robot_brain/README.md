# 🤖 Humanoid Robot Brain System

A comprehensive AI-powered robot brain system designed for Raspberry Pi 5, featuring Bangla and English language support, face recognition, and intelligent conversation capabilities.

## 🌟 Features

- **Multilingual Support**: Natural conversation in Bangla and English
- **Face Recognition**: Advanced face detection and recognition with OpenCV
- **AI Integration**: Powered by Ollama with gemma:2b model
- **Speech Processing**: High-quality TTS and STT for both languages
- **Visual Interface**: Real-time display with spectrum visualization
- **School Integration**: Role-based access and educational features
- **Internet Search**: Web search fallback for complex queries
- **Modular Design**: Extensible architecture for custom features

## 🏗️ System Architecture

```
robot_brain/
├── main.py                 # Main entry point
├── core/                   # Core brain modules
│   ├── intent.py          # Intent recognition
│   ├── memory.py          # Memory management
│   ├── task_manager.py    # Task routing
│   └── config.py          # Configuration
├── speech/                 # Speech processing
│   ├── stt.py             # Speech-to-text
│   ├── tts_bangla.py      # Bangla TTS
│   ├── tts_english.py     # English TTS
│   └── audio_player.py    # Audio playback
├── vision/                 # Computer vision
│   ├── face_recognition.py # Face recognition
│   ├── camera_utils.py    # Camera management
│   └── vision_tasks.py    # Vision tasks
├── ai/                     # AI integration
│   ├── ollama_client.py   # Ollama interface
│   ├── response_router.py # Response routing
│   └── web_search.py      # Web search
├── ui/                     # User interface
│   ├── display_manager.py # Display management
│   ├── visualizer.py      # Spectrum visualization
│   └── camera_view.py     # Camera view
├── actions/                # Robot actions
│   ├── entertainment.py   # Entertainment module
│   ├── school_roles.py    # School functions
│   └── motion.py          # Motion control
└── data/                   # Data storage
    ├── faces/             # Face images
    ├── memory.db          # SQLite database
    └── logs/              # System logs
```

## 📋 Requirements

### Hardware Requirements
- **Raspberry Pi 5** (8GB RAM recommended)
- **Pi Camera Module** or USB camera
- **Microphone** (USB or built-in)
- **Speaker** or audio output
- **Display** (optional, for visual feedback)
- **SD Card** (64GB+ recommended)

### Software Requirements
- **Raspberry Pi OS** (64-bit recommended)
- **Python 3.8+**
- **OpenCV 4.5+**
- **Ollama** with gemma:2b model
- **Various Python packages** (see installation guide)

## 🚀 Installation Guide

### Step 1: System Setup

1. **Install Raspberry Pi OS**:
   ```bash
   # Download and flash Raspberry Pi OS 64-bit to SD card
   # Enable SSH, camera, and audio interfaces
   ```

2. **Update system**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3-pip python3-venv git
   ```

### Step 2: Install Dependencies

1. **Create virtual environment**:
   ```bash
   cd /home/pi
   python3 -m venv robot_brain_env
   source robot_brain_env/bin/activate
   ```

2. **Install system packages**:
   ```bash
   sudo apt install -y \
     libopencv-dev \
     python3-opencv \
     libportaudio2 \
     portaudio19-dev \
     libasound2-dev \
     espeak \
     espeak-data \
     libespeak1 \
     libespeak-dev \
     festival \
     festvox-kallpc16k \
     cmake \
     build-essential \
     libssl-dev \
     libffi-dev \
     libxml2-dev \
     libxslt1-dev \
     zlib1g-dev
   ```

3. **Install Python packages**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Step 3: Install Ollama

1. **Install Ollama**:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Start Ollama service**:
   ```bash
   ollama serve
   ```

3. **Download gemma:2b model**:
   ```bash
   ollama pull gemma:2b
   ```

### Step 4: Install Speech Models

1. **Download Vosk Bangla model**:
   ```bash
   mkdir -p data/models
   cd data/models
   wget https://alphacephei.com/vosk/models/vosk-model-small-bn-0.22.zip
   unzip vosk-model-small-bn-0.22.zip
   ```

2. **Install Coqui TTS**:
   ```bash
   pip install TTS
   ```

3. **Install Piper TTS**:
   ```bash
   # Download and install Piper TTS
   wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz
   tar -xzf piper_arm64.tar.gz
   sudo mv piper /usr/local/bin/
   ```

### Step 5: Configure System

1. **Set up camera**:
   ```bash
   sudo raspi-config
   # Enable Camera Interface
   # Enable I2C Interface
   ```

2. **Configure audio**:
   ```bash
   # Test microphone
   arecord -l
   # Test speaker
   aplay /usr/share/sounds/alsa/Front_Left.wav
   ```

3. **Set up display** (if using):
   ```bash
   # Configure display resolution
   sudo raspi-config
   # Advanced Options > Resolution
   ```

### Step 6: Clone and Setup Project

1. **Clone repository**:
   ```bash
   cd /home/pi
   git clone <repository-url> robot_brain
   cd robot_brain
   ```

2. **Install project dependencies**:
   ```bash
   pip install -e .
   ```

3. **Initialize database**:
   ```bash
   python3 -c "from core.memory import MemoryManager; MemoryManager()"
   ```

## 🧪 Testing the System

### Basic System Test

1. **Test camera**:
   ```bash
   python3 -c "from vision.camera_utils import CameraManager; cm = CameraManager(); print('Camera test:', cm.test_camera())"
   ```

2. **Test speech recognition**:
   ```bash
   python3 -c "from speech.stt import SpeechToText; stt = SpeechToText(); print('STT test:', stt.test_microphone())"
   ```

3. **Test AI model**:
   ```bash
   python3 -c "from ai.ollama_client import OllamaClient; client = OllamaClient(); print('AI test:', client.test_model())"
   ```

### Full System Test

1. **Run main system**:
   ```bash
   python3 main.py
   ```

2. **Test interactions**:
   - Say "Hello" in English or "আসসালামু আলাইকুম" in Bangla
   - Try "Take a picture" or "ছবি তুলো"
   - Ask questions like "What is AI?" or "কৃত্রিম বুদ্ধিমত্তা কি?"

## 🎮 Usage Guide

### Starting the Robot

1. **Activate environment**:
   ```bash
   source robot_brain_env/bin/activate
   cd robot_brain
   ```

2. **Start the system**:
   ```bash
   python3 main.py
   ```

### Basic Commands

#### English Commands
- "Hello" - Greeting
- "Take a picture" - Capture photo
- "Tell me a joke" - Entertainment
- "What is [topic]?" - Knowledge questions
- "Move forward" - Robot movement
- "Search for [query]" - Web search

#### Bangla Commands
- "আসসালামু আলাইকুম" - Greeting
- "ছবি তুলো" - Capture photo
- "কৌতুক বলো" - Entertainment
- "[বিষয়] কি?" - Knowledge questions
- "এগিয়ে যাও" - Robot movement
- "[বিষয়] খুঁজে বের করো" - Web search

### Face Recognition

1. **Register new face**:
   - Look at camera
   - Say "Register my face" or "আমার মুখ চিনে রাখো"
   - Provide name when prompted

2. **Automatic recognition**:
   - Robot will automatically recognize registered faces
   - Personalized greetings based on role

### School Functions

1. **Student registration**:
   ```python
   from actions.school_roles import SchoolRoleManager
   sm = SchoolRoleManager()
   sm.register_student("John Doe", "S001", "Grade 5", "5A", "parent@email.com")
   ```

2. **Attendance tracking**:
   - Automatic face recognition for attendance
   - Manual attendance recording

3. **Patrol functions**:
   - Start patrol: "Start patrol" or "পেট্রোল শুরু করো"
   - End patrol: "End patrol" or "পেট্রোল শেষ করো"

## ⚙️ Configuration

### Environment Variables

Create `.env` file:
```bash
# Ollama settings
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=gemma:2b

# Search API (optional)
SEARCH_API_KEY=your_google_api_key
SEARCH_ENGINE_ID=your_search_engine_id

# Audio settings
SAMPLE_RATE=16000
CHUNK_SIZE=4000

# Camera settings
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
CAMERA_FPS=30
```

### Customization

1. **Modify system prompts** in `ai/response_router.py`
2. **Add new entertainment content** in `actions/entertainment.py`
3. **Configure school settings** in `actions/school_roles.py`
4. **Adjust display settings** in `ui/display_manager.py`

## 🔧 Troubleshooting

### Common Issues

1. **Camera not working**:
   ```bash
   # Check camera connection
   lsusb
   # Test camera
   libcamera-hello --list-cameras
   ```

2. **Audio issues**:
   ```bash
   # Check audio devices
   arecord -l
   aplay -l
   # Test microphone
   arecord -d 5 test.wav
   ```

3. **Ollama connection failed**:
   ```bash
   # Check Ollama status
   systemctl status ollama
   # Restart Ollama
   sudo systemctl restart ollama
   ```

4. **Face recognition not working**:
   ```bash
   # Check OpenCV installation
   python3 -c "import cv2; print(cv2.__version__)"
   # Test face detection
   python3 -c "from vision.face_recognition import FaceRecognizer; fr = FaceRecognizer(); print('Face recognition test:', fr.test_face_recognition('test_image.jpg'))"
   ```

### Performance Optimization

1. **Reduce camera resolution** for better performance
2. **Lower AI model temperature** for faster responses
3. **Use SSD storage** for better database performance
4. **Increase swap space** if running out of memory

## 📊 Monitoring and Logs

### System Monitoring

1. **Check system status**:
   ```bash
   # CPU and memory usage
   htop
   # Disk usage
   df -h
   # Temperature
   vcgencmd measure_temp
   ```

2. **View logs**:
   ```bash
   tail -f data/logs/system.log
   ```

### Database Management

1. **Backup database**:
   ```bash
   cp data/memory.db data/backup_$(date +%Y%m%d).db
   ```

2. **View database**:
   ```bash
   sqlite3 data/memory.db
   .tables
   SELECT * FROM people;
   ```

## 🔒 Security Considerations

1. **Change default passwords**
2. **Enable firewall**:
   ```bash
   sudo ufw enable
   sudo ufw allow ssh
   ```

3. **Regular updates**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **Secure API keys** in environment variables

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Ollama** for AI model hosting
- **OpenCV** for computer vision
- **Vosk** for speech recognition
- **Coqui TTS** for Bangla speech synthesis
- **Piper TTS** for English speech synthesis
- **Raspberry Pi Foundation** for hardware platform

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**Happy Robot Building! 🤖✨**