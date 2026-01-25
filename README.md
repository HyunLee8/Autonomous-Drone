# Gazer
Gazer 🚁
An autonomous drone system that secures the chain of custody for digital forensic investigators.
Overview
Gazer is an intelligent drone platform designed to solve a critical problem in digital forensics: maintaining proper chain of custody documentation when investigators work solo. By acting as an autonomous visual witness, Gazer enables a single investigator to secure digital evidence while the drone automatically records their actions, ensuring legal admissibility of seized materials.
Unlike traditional follow-me drones that produce shaky, unusable footage, Gazer employs advanced computer vision and control theory to deliver smooth, professional-grade documentation of evidence collection procedures.
Key Features

🎯 Autonomous Subject Tracking - Uses YOLO-based computer vision to identify and follow the investigator without manual piloting
📹 Forensic-Grade Recording - Captures stable, third-person footage suitable for legal proceedings
🎮 Smart Stabilization - Dynamic "Dead Zone" filtering ignores micro-movements to eliminate footage jitter
🌐 Web Control Interface - Clean Next.js dashboard for launching, monitoring, and landing operations
⚡ Real-Time Processing - High-concurrency architecture handles video streaming, CV analysis, and flight control simultaneously

How It Works
Gazer combines several technologies to create a fully autonomous tracking system:

Computer Vision: YOLO (You Only Look Once) object detection identifies and tracks the user in real-time
Flight Control: PID (Proportional-Integral-Derivative) controller maintains smooth movement by calculating positional error and adjusting yaw/throttle
Smart Filtering: Dead zone logic prevents the drone from reacting to minor movements, creating cinematic-quality footage
Multi-threaded Architecture: 10 concurrent threads manage video feed, CV processing, and drone commands without race conditions

The control system follows the PID equation:
u(t) = Kₚe(t) + Kᵢ∫e(τ)dτ + Kd(de(t)/dt)
Where error e(t) is calculated from the offset between the subject's position and frame center.
Use Cases

Digital Forensics: Solo investigators documenting evidence seizure from servers, computers, and digital devices
Crime Scene Documentation: Hands-free recording of evidence collection procedures
Legal Compliance: Creating objective third-party video records for chain of custody requirements
Content Creation: Vloggers and streamers who need automated camera operation

Technical Stack

Backend: Python with DJI Tello SDK
Frontend: Next.js web application
Computer Vision: YOLO object detection
Hardware: DJI Tello drone

Future Roadmap

🔍 Object Search: Train YOLO to detect specific evidence types (laptops, hard drives, servers) for automated room scanning
🤚 Gesture Controls: Hand signal recognition for intuitive drone commands (e.g., palm up to pause)
🎤 Voice Commands: Natural language instructions for launch, landing, and repositioning
🔄 Swarm Coordination: Multiple drones working together to document scenes from multiple angles