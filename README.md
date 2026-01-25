# Gazer
🚁 Gazer
Gazer is an autonomous drone system designed to secure the chain of custody for digital forensic investigations. Acting as a self-directing visual witness, Gazer enables a single investigator to document evidence seizure hands-free—ensuring transparency, accountability, and legal admissibility.
🧠 Inspiration
Gazer began as an exploration into autonomous camera systems for content creators—eliminating the need for a cameraman for vloggers and streamers.
However, while evaluating the Cipher Tech Digital Forensics challenge, we recognized a far more impactful use case: Chain of Custody Assurance.
In real-world forensic investigations, securing digital evidence (servers, laptops, storage devices) typically requires two people:
One to handle the evidence
One to visually document every step for legal verification
Gazer reimagines this workflow. It empowers a solo investigator to enter a scene while an autonomous “eye” follows, records, and documents every action objectively—without distraction or bias.
🔍 What It Does
Gazer is an autonomous drone platform built to act as a third-person forensic witness.
Key Features
Autonomous User Tracking
Uses computer vision to detect and track the investigator, keeping them centered in frame without manual piloting.
Forensic-Grade Documentation
Records stable, third-person footage of evidence handling, creating a verifiable visual record of the chain of custody.
Smart Stabilization (Dead Zone Logic)
Unlike traditional “follow-me” drones that jitter constantly, Gazer ignores micro-movements to produce smooth, cinematic footage.
Web-Based Control Interface
A clean Next.js dashboard allows investigators to launch, land, and monitor the drone in real time.
🛠 How We Built It
Gazer is powered by a high-concurrency Python backend paired with a modern web frontend.
1. Vision Stack
YOLO (You Only Look Once) for real-time object and face detection
Initially tested MediaPipe, but YOLO proved far more reliable at longer distances and wider angles
2. Drone Control
Controlled via the DJI Tello SDK
Commands are sent over UDP for low-latency response
3. Flight Logic (PID Controller)
To ensure smooth and natural movement, we implemented a PID controller that minimizes the error between the detected face position 
(
x
,
y
)
(x,y) and the frame center 
(
x
c
,
y
c
)
(x 
c
​	
 ,y 
c
​	
 ).
u
(
t
)
=
K
p
e
(
t
)
+
K
i
∫
0
t
e
(
τ
)
 
d
τ
+
K
d
d
e
(
t
)
d
t
u(t)=K 
p
​	
 e(t)+K 
i
​	
 ∫ 
0
t
​	
 e(τ)dτ+K 
d
​	
  
dt
de(t)
​	
 
This allows Gazer to adjust yaw and throttle smoothly rather than snapping toward the subject.
4. Frontend
Built with Next.js
Displays the live video feed
Provides simple Launch and Land controls
⚠️ Challenges We Ran Into
This project became a deep dive into concurrency, architecture, and real-time systems.
🧵 Thread Safety & Race Conditions
Running live video streaming, computer vision inference, and drone control simultaneously required 10 concurrent threads
Early versions suffered from race conditions where the drone received conflicting commands
Solved with strict locking, shared state control, and command prioritization
🔄 Circular Imports
Separating vision logic, drone control, and the web server introduced circular dependencies
Required a full refactor of the module hierarchy and dependency tree
🤢 The “Jitter” Problem
The drone initially reacted to every pixel of movement
Introduced a Dead Zone—a tolerance radius at the center of the frame:
If 
∣
F
a
c
e
p
o
s
−
C
e
n
t
e
r
f
r
a
m
e
∣
<
D
e
a
d
Z
o
n
e
⇒
Speed
=
0
If ∣Face 
pos
​	
 −Center 
frame
​	
 ∣<DeadZone⇒Speed=0
This single change transformed the footage from robotic to cinematic.
🏆 Accomplishments We’re Proud Of
Dead Zone Stabilization
Successfully tuned tracking behavior so the drone feels intentional, not twitchy.
System Stability
Managing 10 concurrent threads without crashes or command conflicts.
The Pivot
Transforming a fun autonomous camera idea into a serious forensic technology solution aligned perfectly with the challenge prompt.
📚 What We Learned
Control Theory Is an Art
PID tuning is delicate—slightly wrong values lead to oscillation or instability.
Architecture Matters
Concurrency without proper state management quickly becomes chaos.
Hardware Is Unforgiving
Battery limits, physical drift, and real-world latency make hardware projects far more complex than simulations.
🚀 What’s Next for Gazer
Autonomous Object Search
Train YOLO to detect specific evidence (e.g., laptops, hard drives) and scan rooms automatically.
Gesture & Voice Commands
Hands-free control using gestures (pause tracking) and voice prompts.
Swarm Capabilities
Multiple Gazers coordinating to document a scene from several angles simultaneously.