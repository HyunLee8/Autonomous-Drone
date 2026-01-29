# Autonomous Drone Tracking
Autonomous Facial Tracking Drone using YOLO8 Nano for face tracking model and Tello SDK for controls. Manually Implementing PID controls for smoother turns and 9 Concurrent threads running in the backend to handle all requests at the same time. 

## Demo | [Link to UI](https://autonomous-drone-five.vercel.app/)
<div align="center">
  <img src="https://github.com/user-attachments/assets/a805c00e-5555-4c11-84fb-4b9a71287c0d" width="49%" />
  <img src="https://github.com/user-attachments/assets/3506e63e-b9dc-4fbf-9b1c-e51c3d74c366" width="49%" />
</div>

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
