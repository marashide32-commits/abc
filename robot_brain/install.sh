#!/bin/bash

# Robot Brain System Installation Script
# For Raspberry Pi 5 with Raspberry Pi OS

set -e  # Exit on any error

echo "🤖 Robot Brain System Installation Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Raspberry Pi
check_raspberry_pi() {
    if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
        print_warning "This script is designed for Raspberry Pi. Continue anyway? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Update system packages
update_system() {
    print_status "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    print_success "System updated successfully"
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    sudo apt install -y \
        python3-pip \
        python3-venv \
        python3-dev \
        git \
        cmake \
        build-essential \
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
        libssl-dev \
        libffi-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libv4l-dev \
        libxvidcore-dev \
        libx264-dev \
        libgtk-3-dev \
        libatlas-base-dev \
        gfortran \
        wget \
        curl \
        unzip
    
    print_success "System dependencies installed"
}

# Install Ollama
install_ollama() {
    print_status "Installing Ollama..."
    
    if ! command -v ollama &> /dev/null; then
        curl -fsSL https://ollama.ai/install.sh | sh
        print_success "Ollama installed successfully"
    else
        print_warning "Ollama already installed"
    fi
    
    # Start Ollama service
    print_status "Starting Ollama service..."
    sudo systemctl enable ollama
    sudo systemctl start ollama
    
    # Wait for service to start
    sleep 5
    
    # Download gemma:2b model
    print_status "Downloading gemma:2b model (this may take a while)..."
    ollama pull gemma:2b
    
    print_success "Ollama setup completed"
}

# Create virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    # Create virtual environment
    python3 -m venv robot_brain_env
    source robot_brain_env/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Python environment created"
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Activate virtual environment
    source robot_brain_env/bin/activate
    
    # Install requirements
    pip install -r requirements.txt
    
    print_success "Python dependencies installed"
}

# Download speech models
download_speech_models() {
    print_status "Downloading speech models..."
    
    # Create models directory
    mkdir -p data/models
    
    # Download Vosk Bangla model
    if [ ! -d "data/models/vosk-model-small-bn-0.22" ]; then
        print_status "Downloading Vosk Bangla model..."
        cd data/models
        wget -q https://alphacephei.com/vosk/models/vosk-model-small-bn-0.22.zip
        unzip -q vosk-model-small-bn-0.22.zip
        rm vosk-model-small-bn-0.22.zip
        cd ../..
        print_success "Vosk Bangla model downloaded"
    else
        print_warning "Vosk Bangla model already exists"
    fi
}

# Install Piper TTS
install_piper_tts() {
    print_status "Installing Piper TTS..."
    
    if ! command -v piper &> /dev/null; then
        # Download Piper TTS for ARM64
        cd /tmp
        wget -q https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz
        tar -xzf piper_arm64.tar.gz
        sudo mv piper /usr/local/bin/
        sudo chmod +x /usr/local/bin/piper
        rm piper_arm64.tar.gz
        cd - > /dev/null
        print_success "Piper TTS installed"
    else
        print_warning "Piper TTS already installed"
    fi
}

# Configure system
configure_system() {
    print_status "Configuring system..."
    
    # Enable camera interface
    sudo raspi-config nonint do_camera 0
    
    # Enable I2C interface
    sudo raspi-config nonint do_i2c 0
    
    # Enable SPI interface
    sudo raspi-config nonint do_spi 0
    
    # Set GPU memory split
    sudo raspi-config nonint do_memory_split 128
    
    print_success "System configured"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    source robot_brain_env/bin/activate
    python3 -c "from core.memory import MemoryManager; MemoryManager()"
    
    print_success "Database initialized"
}

# Create systemd service
create_service() {
    print_status "Creating systemd service..."
    
    sudo tee /etc/systemd/system/robot-brain.service > /dev/null <<EOF
[Unit]
Description=Robot Brain System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/robot_brain
Environment=PATH=/home/pi/robot_brain/robot_brain_env/bin
ExecStart=/home/pi/robot_brain/robot_brain_env/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable robot-brain.service
    
    print_success "Systemd service created"
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    source robot_brain_env/bin/activate
    
    # Test imports
    python3 -c "
import sys
try:
    from core.memory import MemoryManager
    from speech.stt import SpeechToText
    from vision.camera_utils import CameraManager
    from ai.ollama_client import OllamaClient
    print('✅ All modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
    
    # Test Ollama connection
    python3 -c "
from ai.ollama_client import OllamaClient
client = OllamaClient()
if client.is_available:
    print('✅ Ollama connection successful')
else:
    print('❌ Ollama connection failed')
    exit(1)
"
    
    print_success "Installation test completed"
}

# Main installation function
main() {
    echo "Starting Robot Brain System installation..."
    echo
    
    check_raspberry_pi
    update_system
    install_system_deps
    install_ollama
    setup_python_env
    install_python_deps
    download_speech_models
    install_piper_tts
    configure_system
    init_database
    create_service
    test_installation
    
    echo
    print_success "🎉 Robot Brain System installation completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Reboot your Raspberry Pi: sudo reboot"
    echo "2. Start the robot brain: sudo systemctl start robot-brain"
    echo "3. Check status: sudo systemctl status robot-brain"
    echo "4. View logs: journalctl -u robot-brain -f"
    echo
    echo "Manual start:"
    echo "  source robot_brain_env/bin/activate"
    echo "  python3 main.py"
    echo
    echo "For more information, see README.md"
}

# Run main function
main "$@"