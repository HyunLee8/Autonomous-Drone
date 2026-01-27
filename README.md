# Gazer
Gazer

## Overview

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

## Running Gazer

### Hardware Setup

1. Fully charge your DJI Tello drone
2. Power on the drone
3. Connect your computer to the drone's WiFi network (`TELLO-XXXXXX`)

### Start the Application

Terminal 1 - Backend:
```bash
cd drone_backend
python3 main.py
```

Terminal 2 - Frontend:
```bash
cd next-app
npm run dev
```


## What We Learned

- **Control Theory**: Tuning the Kₚ, Kᵢ, and Kd values is like an art form - a slightly wrong value means the drone oscillates out of control
- **Architecture Matters**: You cannot just "throw more threads" at a problem without a solid plan for shared state and resource locking
- **Hardware Limitations**: Working with real hardware (batteries, flight time, physical drift) is infinitely harder than software simulation

## Future Roadmap

- *** Object Search**: Adapt YOLO to detect specific objects (laptops, hard drives) to autonomously scan a room for evidence
- *** Gesture Controls**: Hand signals to command the drone (palm up to pause)
- *** Swarm Capabilities**: Multiple Gazers documenting a crime scene from multiple angles simultaneously
