# Gazer
Gazer

**An autonomous drone system that secures the chain of custody for digital forensic investigators.**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-13%2B-black)](https://nextjs.org/)

## Overview

Gazer is an intelligent drone platform designed to solve a critical problem in digital forensics: maintaining proper chain of custody documentation when investigators work solo. By acting as an autonomous visual witness, Gazer enables a single investigator to secure digital evidence while the drone automatically records their actions, ensuring legal admissibility of seized materials.

Unlike traditional follow-me drones that produce shaky, unusable footage, Gazer employs advanced computer vision and PID control theory to deliver smooth, professional-grade documentation of evidence collection procedures.

## Inspiration

Our initial spark came from the world of content creation and removing the need for a cameraman for vloggers and streamers. However, when looking at the Cipher Tech Digital Forensics challenge, we realized this technology had a much more critical application: **Chain of Custody Assurance**.

In forensic investigations, securing digital evidence often requires a two-person team: one to handle the evidence and one to record the process. We wanted to build a tool that empowers a solo investigator to enter a scene and secure evidence while an autonomous "eye" documents their every move, hands-free.

## Key Features

- **🎯 Autonomous Tracking** - Uses YOLO computer vision to identify the user and keep them centered in the frame without any manual piloting
- **📹 Forensic Documentation** - Records stable, third-person footage of evidence seizure suitable for legal proceedings
- **🎮 Smart Stabilization** - Dynamic "Dead Zone" filters out micro-movements, ensuring smooth and professional footage
- **🌐 Web Control Interface** - Clean Next.js dashboard for launching, monitoring, and landing operations
- **⚡ Real-Time Processing** - High-concurrency architecture with 10 threads managing video streaming, CV analysis, and flight control

## How It Works

### Vision Stack
We utilize **YOLO (You Only Look Once)** for object detection. We initially tested MediaPipe, but found YOLO offered superior tracking reliability when the subject was further from the drone.

### Drone Control
We use the **DJI Tello SDK** to send UDP commands to the hardware.

### Flight Logic (PID)
To ensure smooth movement, we implemented a **PID (Proportional-Integral-Derivative) controller**. This calculates the error between the user's face coordinates (x,y) and the center of the frame (xc,yc) to adjust the drone's yaw and throttle smoothly:

```
u(t) = Kₚe(t) + Kᵢ∫₀ᵗe(τ)dτ + Kd(de(t)/dt)
```

### Dead Zone Logic
To prevent jittery footage, we programmed a "Dead Zone" - a tolerance radius in the center of the frame:

```
If |Face_pos - Center_frame| < DeadZone → Speed = 0
```

This makes the drone feel "cinematic" rather than robotic, ignoring small movements and only adjusting when the subject actually moves.

## Technical Stack

- **Backend**: Python 3.8+ with DJI Tello SDK
- **Frontend**: Next.js 13+ web application
- **Computer Vision**: YOLO (Ultralytics)
- **Control System**: Custom PID controller with dead zone filtering
- **Hardware**: DJI Tello drone

## Prerequisites

- **Python** 3.8 or higher
- **Node.js** 16.0 or higher
- **DJI Tello Drone** (fully charged)
- **WiFi capability** (to connect to drone network)
- **Recommended**: 8GB+ RAM, multi-core processor

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/gazer.git
cd gazer
```

### 2. Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download YOLO model
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 4. Configuration

Create a `.env` file in the root directory:

```env
# Backend Configuration
FLASK_PORT=5000
DRONE_IP=192.168.10.1

# PID Tuning
PID_KP=0.5
PID_KI=0.1
PID_KD=0.2
DEAD_ZONE_RADIUS=50

# Video Settings
VIDEO_SAVE_PATH=./recordings
```

## Running Gazer

### Hardware Setup

1. Fully charge your DJI Tello drone
2. Power on the drone
3. Connect your computer to the drone's WiFi network (`TELLO-XXXXXX`)

### Start the Application

**Option 1: Quick Start**
```bash
./launch.sh
```

**Option 2: Manual Start**

Terminal 1 - Backend:
```bash
source venv/bin/activate
python src/main.py
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### Access the Dashboard

Open your browser to `http://localhost:3000`

## Usage

1. **Pre-Flight Check**: Ensure drone is charged, WiFi connected, and flight area is clear
2. **Launch**: Click "Launch" button on the dashboard
3. **Documentation**: Position yourself 2-4 meters from the drone and move naturally
4. **Monitor**: Watch real-time battery, tracking status, and video feed
5. **Land**: Click "Land" button to safely land and save recording

Recordings are automatically saved to `recordings/` with timestamps.

## Troubleshooting

**Drone won't connect**: Ensure you're connected to drone WiFi and restart the backend server

**Tracking is jittery**: Increase `DEAD_ZONE_RADIUS` in `.env` configuration

**Low frame rate**: Close unnecessary applications, use `yolov8n.pt` (nano) model instead of larger models

**Video not saving**: Check disk space and write permissions on `recordings/` directory

## What We Learned

- **Control Theory**: Tuning the Kₚ, Kᵢ, and Kd values is like an art form - a slightly wrong value means the drone oscillates out of control
- **Architecture Matters**: You cannot just "throw more threads" at a problem without a solid plan for shared state and resource locking
- **Hardware Limitations**: Working with real hardware (batteries, flight time, physical drift) is infinitely harder than software simulation

## Future Roadmap

- **🔍 Object Search**: Adapt YOLO to detect specific objects (laptops, hard drives) to autonomously scan a room for evidence
- **🤚 Gesture Controls**: Hand signals to command the drone (palm up to pause)
- **🎤 Voice Commands**: Verbal instructions for launch and movement
- **🔄 Swarm Capabilities**: Multiple Gazers documenting a crime scene from multiple angles simultaneously

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

Built for the **Cipher Tech Digital Forensics Challenge**. Special thanks to the forensic investigation community for inspiring this critical application of autonomous drone technology.

---

⚠️ **Safety Notice**: This system is designed to complement, not replace, proper forensic procedures. Always follow local drone regulations and your jurisdiction's legal requirements for evidence handling and documentation.