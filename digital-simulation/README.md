# SMYGN32 Digital Simulation

## V2V-Enabled Collision and Trajectory Risk Assessment

This folder contains the digital simulation developed for **Smart India Hackathon 2026 — SIH26007**.

The simulation demonstrates how SMYGN32 can improve the safety of mine vehicles operating in fog and low-visibility conditions.

---

## Objective

The simulation demonstrates:

- Multi-vehicle mine traffic
- Simulated V2V communication
- Radar and LiDAR sensing
- GPS/DGPS positioning
- Sensor fusion
- Vehicle tracking
- Trajectory prediction
- Time-to-Collision (TTC)
- Collision-risk assessment
- Safe-speed recommendation
- Driver safety alerts
- Mine control-center monitoring
- Dense-fog operation

---

## System Flow
Vehicle Sensors
      ↓
Sensor Fusion
      ↓
Object Tracking
      ↓
Trajectory Prediction
      ↓
Time-to-Collision (TTC)
      ↓
Risk Assessment
      ↓
Safety Decision
      ↓
Driver Alert / Mine Control Center

Simulated Vehicles

The simulation contains four mine vehicles:

A01
B01
C01
D01

The vehicles exchange simulated state information and are monitored by the safety system.

Sensor Simulation

The simulation models the following sensing and communication sources:

Radar

Provides distance and relative-motion information.

LiDAR

Provides simulated environmental and object-detection information.

GPS / DGPS

Provides simulated vehicle positioning.

V2V Communication

Vehicles exchange simulated information such as:

Position
Speed
Heading
Vehicle state

The V2V communication in this Python simulation is software-simulated. The physical prototype uses wireless hardware for actual vehicle-to-vehicle communication.

Sensor Fusion

SMYGN32 combines information from multiple simulated sources and calculates a confidence value.

This allows the system to maintain situational awareness even when individual sensor confidence decreases.

Trajectory Prediction

The system predicts the future movement of vehicles using their current position, speed and heading.

The predicted trajectories are then used for collision-risk assessment.

Time-to-Collision

A simplified Time-to-Collision calculation is used to estimate how quickly two vehicles may reach a potential conflict.

The prototype uses a 2.5-second alert threshold for demonstration.

This value is a prototype parameter and is not a universal industrial safety standard.

Risk Levels

The simulation classifies vehicle situations into:

Risk Level	Meaning
SAFE	No immediate collision threat
CAUTION	Increasing collision risk
CRITICAL	Immediate or severe collision risk
Demonstration Scenarios

The simulation provides five demonstration scenarios:

1. SAFE

Vehicles operate with sufficient separation.

2. CAUTION

Vehicles approach a potential conflict and the risk level increases.

3. CRITICAL / Collision Event

A high-risk situation is demonstrated.

4. COLLISION AVOIDED

The system demonstrates a successful safety response.

5. DENSE FOG

Sensor confidence and visibility conditions are reduced to demonstrate operation under severe fog.

Controls
Key	Function
1	SAFE scenario
2	CAUTION scenario
3	CRITICAL scenario
4	COLLISION AVOIDED scenario
5	DENSE FOG scenario
R	Reset simulation
SPACE	Pause / Resume
D	Automatic demonstration mode
F11	Toggle fullscreen
ESC	Exit / fullscreen
Installation

Install Python 3 and then install the required package:

pip install -r requirements.txt
Run the Simulation

From this folder, run:

python simulation.py

The simulation opens a Pygame-based command-center interface.

Dashboard

The simulation provides a visual dashboard showing information including:

Vehicle position
Vehicle speed
Sensor confidence
V2V communication status
Fusion confidence
Predicted trajectory
TTC
Risk score
Recommended safe speed
Fleet state
Event log
Command-center information
Vehicle safety display
Prototype Scope

This simulation is a scaled proof-of-concept for SIH26007.

The sensing, V2V communication and mine environment are simulated in software.

A production implementation would require industrial-grade:

mmWave radar
LiDAR
Thermal cameras
GNSS/DGPS
Vehicle communication systems
Edge computing hardware
Certified vehicle safety interfaces
Relation to the Physical Prototype

The digital simulation represents the larger system concept, while the physical prototype demonstrates the core functionality using low-cost hardware.

Digital Simulation
        +
Physical Prototype
        ↓
SMYGN32 Proof-of-Concept
Project

SMYGN32

V2V-Enabled Collision and Trajectory Risk Assessment

Smart India Hackathon 2026

Problem Statement: SIH26007

Theme: Smart Automation

Category: Hardware
