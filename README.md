# SMYGN32

## V2V-Enabled Collision and Trajectory Risk Assessment

**Smart India Hackathon 2026 — SIH26007**

> Safe and Efficient Operation of Mine Vehicles in Fog and Low-Visibility Conditions in Open Cast Iron Ore Mines.

---

## 🚨 Problem

Open-cast iron ore mines can experience extremely poor visibility during severe monsoon and fog conditions. Visibility can fall to only a few metres, making it difficult for operators of heavy dumpers and haul vehicles to detect nearby vehicles and obstacles.

This can lead to:

- Increased collision and road-accident risk
- Reduced vehicle speed
- Longer haul cycles
- Reduced fleet utilization
- Production and ore-evacuation losses
- Difficulty maintaining safe operations during low visibility

---

## 💡 Our Solution

**SMYGN32** is a predictive mine-vehicle safety system designed to improve situational awareness and reduce collision risk during fog and low-visibility conditions.

The system combines:

**Sense → Share → Fuse → Predict → Assess → Warn**

SMYGN32 combines local sensor information with vehicle-state information to estimate potential conflicts between vehicles and provide appropriate safety alerts and speed recommendations.

---

## 🧠 Core Technology

- Multi-sensor perception
- Radar-based distance awareness
- LiDAR-based environment perception
- GNSS / DGPS positioning
- IMU-based vehicle motion sensing
- Vehicle-to-Vehicle (V2V) communication
- Vehicle-to-Infrastructure (V2I) communication
- Sensor fusion
- Trajectory prediction
- Time-to-Collision (TTC)
- Collision-risk assessment
- Dynamic safe-speed recommendation
- Driver alerts
- Mine control-center monitoring
- Digital twin / fleet visualization

---

## 🔬 Prototype

SMYGN32 is developed using two complementary prototypes.

### 1. Physical Hardware Prototype

A scaled vehicle prototype demonstrates:

- Vehicle movement using a 4WD chassis
- HC-SR04 distance sensing
- MPU6050 motion sensing
- OLED status display
- Green / Yellow / Red safety indicators
- Buzzer-based warning
- L298N motor control
- Automatic motor-speed reduction and stopping based on detected risk

The current physical prototype is a scaled proof-of-concept. Industrial-grade sensing, positioning and V2V communication are part of the extended system architecture.

### 2. Digital Simulation

The digital simulation demonstrates:

- Multi-vehicle traffic
- Simulated Radar and LiDAR
- GPS / DGPS positioning
- Simulated V2V communication
- Sensor-fusion confidence
- Vehicle trajectory prediction
- Time-to-Collision (TTC)
- Collision-risk assessment
- Safe-speed recommendation
- Fleet monitoring
- Command-center visualization
- Collision-avoidance scenarios
- Dense-fog conditions

---

## 🏗️ System Architecture

Radar + LiDAR + Camera/Thermal
             +
       GNSS / DGPS + IMU
             +
          V2V / V2I
             ↓
       Sensor Fusion
             ↓
     Environment Analysis
             ↓
       Object Tracking
             ↓
     Trajectory Prediction
             ↓
       TTC + Risk Engine
             ↓
   Safe Speed / Alert Decision
             ↓
    Driver / Vehicle Safety
             ↓
      Mine Control Center
🚦 Safety Decision Concept

The prototype uses three safety states:

State	Meaning	Prototype Response
🟢 SAFE	Low collision risk	Normal operation
🟡 CAUTION	Increased risk	Reduce speed / warning
🔴 CRITICAL	High collision risk	Stop / emergency warning

The thresholds used in the prototypes are demonstration parameters and are not industrial safety standards.

🎥 Demonstrations

Complete hardware and digital-simulation demonstrations are available in:

View Demonstration Videos

📁 Repository Structure
SMYGN32/
│
├── digital-simulation/
│   ├── simulation.py
│   ├── requirements.txt
│   └── README.md
│
├── hardware-prototype/
│   ├── firmware/
│   │   └── SMYGN32_Hardware.ino
│   └── README.md
│
├── documentation/
│   ├── demonstrations/
│   │   ├── README.md
│   │   ├── SMYGN32_Digital_Simulation_Demonstration.mp4
│   │   └── SMYGN32_Hardware_Demonstration.mp4
│   │
│   ├── diagrams/
│   │   └── SMYGN32_Circuit_Diagram.png
│   │
│   └── presentation/
│       └── SMYGN32_SIH_Presentation.pptx
│
├── LICENSE
├── .gitignore
└── README.md
⚙️ Current Project Status

Prototype Stage — Proof of Concept

The project currently includes a working physical prototype and a digital predictive-safety simulation.

The architecture is designed to support future integration of industrial-grade radar, LiDAR, thermal imaging, GNSS/DGPS and real V2V/V2I communication systems.

🎯 Expected Impact

SMYGN32 aims to:

Improve mine-vehicle situational awareness
Reduce collision risk in low visibility
Support safer vehicle speeds
Reduce unnecessary vehicle stoppages
Improve fleet utilization
Maintain safer haulage during monsoon conditions
Provide real-time fleet visibility to mine operators
Create a scalable foundation for intelligent mine-vehicle safety
🏆 Smart India Hackathon 2026

Problem Statement: SIH26007
Organization: Ministry of Steel
Department: NMDC
Category: Hardware
Theme: Smart Automation

👥 Team
Team SMYGN32

Smart India Hackathon 2026

V2V-Enabled Collision and Trajectory Risk Assessment

📌 Disclaimer

SMYGN32 is a scaled proof-of-concept developed for Smart India Hackathon 2026.

The physical prototype and digital simulation are intended to demonstrate the proposed safety architecture and decision-making concept. Deployment in an operational mine would require industrial-grade sensors, certified vehicle interfaces, validated communication systems, rigorous field testing and appropriate safety certification.
