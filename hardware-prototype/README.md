# SMYGN32 Hardware Prototype

## V2V-Enabled Collision and Trajectory Risk Assessment

This folder contains the physical hardware prototype developed as part of **SMYGN32** for **Smart India Hackathon 2026 — SIH26007**.

The prototype demonstrates the core vehicle-safety functionality using an ESP32-based miniature 4WD vehicle.

The system detects nearby obstacles using an ultrasonic sensor, monitors vehicle motion using an MPU6050, displays safety information on an OLED, provides visual and audible warnings, and controls the vehicle motors according to the detected safety condition.

---

## Hardware Objective

The physical prototype demonstrates:

- Obstacle-distance detection
- Vehicle motion sensing
- Real-time safety classification
- Visual safety indication
- Audible safety warning
- Automatic motor speed reduction
- Automatic motor stopping during critical conditions
- OLED-based vehicle status monitoring
- 4WD motor control

---

## Hardware Architecture

HC-SR04 Ultrasonic Sensor
          |
          v
        ESP32
          ^
          |
      MPU6050
          |
          v
   Safety Decision Logic
          |
     +----+----+-----------+
     |    |    |           |
     v    v    v           v
   OLED  LEDs Buzzer     L298N
                         Motor Driver
                            |
                            v
                       4WD Motors
Components Used
Component	Quantity	Purpose
ESP32	1	Main controller
HC-SR04	1	Distance / obstacle detection
MPU6050	1	Motion and orientation sensing
0.96-inch OLED	1	Vehicle status display
Green LED	1	SAFE indication
Yellow LED	1	CAUTION indication
Red LED	1	CRITICAL indication
Buzzer	1	Audible warning
L298N Motor Driver	1	Motor direction and speed control
4WD Robot Chassis	1	Vehicle platform
DC Gear Motors	4	Vehicle movement
Resistors	As required	LED current limiting / signal protection
Jumper Wires	As required	Electrical connections
Battery	1	Motor power supply
ESP32 Pin Map
ESP32 GPIO	Connection
GPIO 5	HC-SR04 TRIG
GPIO 18	HC-SR04 ECHO
GPIO 21	OLED SDA + MPU6050 SDA
GPIO 22	OLED SCL + MPU6050 SCL
GPIO 25	Green LED
GPIO 26	Yellow LED
GPIO 27	Red LED
GPIO 14	Buzzer
GPIO 16	L298N IN1
GPIO 17	L298N IN2
GPIO 19	L298N IN3
GPIO 23	L298N IN4
GPIO 13	L298N ENA
GPIO 4	L298N ENB
HC-SR04 Wiring
HC-SR04                 ESP32
--------------------------------
VCC        -----------> VIN / 5V
GND        -----------> GND
TRIG       -----------> GPIO 5
ECHO       -----------> GPIO 18
HC-SR04 ECHO Protection

The HC-SR04 ECHO signal can be 5 V, while ESP32 GPIOs are designed for 3.3 V logic.

A voltage divider is recommended:

HC-SR04 ECHO
     |
    1kΩ
     |
     +------------> GPIO 18
     |
    2kΩ
     |
    GND

The voltage divider should be used for safer long-term operation.

MPU6050 Wiring
MPU6050                 ESP32
--------------------------------
VCC        -----------> 3.3V
GND        -----------> GND
SDA        -----------> GPIO 21
SCL        -----------> GPIO 22

If the MPU6050 module provides an AD0 pin:

AD0 → GND

The MPU6050 is used to obtain acceleration and gyroscope measurements.

OLED Wiring

The OLED shares the ESP32 I²C bus with the MPU6050.

OLED                    ESP32
--------------------------------
VCC        -----------> 3.3V
GND        -----------> GND
SDA        -----------> GPIO 21
SCL        -----------> GPIO 22
Shared I²C Bus
GPIO 21 ─────┬──── OLED SDA
             |
             └──── MPU6050 SDA

GPIO 22 ─────┬──── OLED SCL
             |
             └──── MPU6050 SCL
LED Connections
Green LED — SAFE
ESP32 GPIO 25
      |
     1kΩ
      |
LED LONG (+)

LED SHORT (-)
      |
     GND
Yellow LED — CAUTION
ESP32 GPIO 26
      |
     1kΩ
      |
LED LONG (+)

LED SHORT (-)
      |
     GND
Red LED — CRITICAL
ESP32 GPIO 27
      |
     1kΩ
      |
LED LONG (+)

LED SHORT (-)
      |
     GND
Buzzer Connection
Buzzer +
    |
    +--------> ESP32 GPIO 14

Buzzer -
    |
    +--------> GND

The buzzer activates continuously during the CRITICAL safety state.

L298N Motor Driver
Control Connections
L298N             ESP32
-------------------------
IN1   ----------> GPIO 16
IN2   ----------> GPIO 17
IN3   ----------> GPIO 19
IN4   ----------> GPIO 23

ENA   ----------> GPIO 13
ENB   ----------> GPIO 4

GND   ----------> ESP32 GND
ENA / ENB

The ENA and ENB jumpers should be removed when using the ESP32 to control motor speed through PWM.

ENA → GPIO 13
ENB → GPIO 4
4WD Motor Connections

The L298N provides two motor-control channels.

Left-Side Motors

Both left-side motors are connected to the first motor channel.

L298N OUT1 ─────┬──── Left Front Motor
                |
                └──── Left Rear Motor

L298N OUT2 ─────┬──── Left Front Motor
                |
                └──── Left Rear Motor
Right-Side Motors

Both right-side motors are connected to the second motor channel.

L298N OUT3 ─────┬──── Right Front Motor
                |
                └──── Right Rear Motor

L298N OUT4 ─────┬──── Right Front Motor
                |
                └──── Right Rear Motor

If one side rotates in the opposite direction during forward movement, reverse the polarity of the motors on that side.

Motor Power

The motors are powered separately from the ESP32.

Motor Battery (+)
       |
       +--------> L298N +12V / VMS

Motor Battery (-)
       |
       +--------> L298N GND

The grounds must be common:

L298N GND
    |
    +--------> ESP32 GND
Important

The ESP32 does not directly power the four motors.

The motor power path is:

Battery
   |
   v
L298N Motor Driver
   |
   v
4WD Motors

The ESP32 provides only the motor control signals.

Complete Wiring Overview
                         +---------------+
                         |    HC-SR04    |
                         |               |
                         | TRIG → GPIO 5 |
                         | ECHO → GPIO18 |
                         +-------+-------+
                                 |
                                 |
 +--------------+        +-------v-------+
 |   MPU6050    |        |               |
 |              |        |     ESP32     |
 | SDA → GPIO21 +------->|               |
 | SCL → GPIO22 +------->|               |
 +--------------+        |               |
                         | GPIO25 → GREEN |
 +--------------+        | GPIO26 → YELLOW|
 |     OLED     |        | GPIO27 → RED   |
 | SDA → GPIO21 +------->| GPIO14 → BUZZER|
 | SCL → GPIO22 +------->|               |
 +--------------+        | GPIO16 → IN1  |
                         | GPIO17 → IN2  |
                         | GPIO19 → IN3  |
                         | GPIO23 → IN4  |
                         | GPIO13 → ENA  |
                         | GPIO4  → ENB  |
                         +-------+-------+
                                 |
                              COMMON GND
                                 |
                         +-------v-------+
                         |     L298N     |
                         |               |
                         | OUT1/OUT2 ----+-- Left motors
                         | OUT3/OUT4 ----+-- Right motors
                         |               |
                         | VMS ← Battery |
                         | GND ← Battery |
                         +---------------+
Safety Logic

The prototype uses distance-based safety thresholds.

Distance > 40 cm
       |
       v
    SAFE
       |
Green LED ON
Buzzer OFF
Motors NORMAL
15 cm ≤ Distance ≤ 40 cm
       |
       v
   CAUTION
       |
Yellow LED ON
Buzzer OFF
Motors SLOW
Distance < 15 cm
       |
       v
   CRITICAL
       |
Red LED ON
Buzzer ON
Motors STOP

If the HC-SR04 returns no valid object measurement, the prototype treats the condition as SAFE.

Motor Speed Control

The prototype uses PWM-based motor speed control.

SAFE
  |
  v
Normal Speed
PWM = 200
CAUTION
  |
  v
Reduced Speed
PWM = 100
CRITICAL
  |
  v
Motors Stopped
PWM = 0

These values are prototype parameters used for demonstration.

MPU6050 Data

The prototype reads:

X-axis acceleration
Y-axis acceleration
Z-axis acceleration
Z-axis gyroscope measurement

The sensor values are displayed through the Serial Monitor and OLED display.

OLED Display

The OLED provides real-time vehicle information including:

Distance
Safety status
X-axis acceleration
Y-axis acceleration
Z-axis gyroscope value

Example:

SMYGN32 VEHICLE
----------------
DIST: 32.5 cm
STATUS: CAUTION

AX: 0.1    AY: 0.0
GZ: 1.2 d/s
Software

The physical prototype is programmed using the Arduino development environment.

The firmware uses:

ESP32 Arduino framework
Wire library for I²C communication
Adafruit GFX library
Adafruit SSD1306 library
Hardware Safety Demonstration

The prototype demonstrates the following sequence:

Distance Measurement
        |
        v
Safety Classification
        |
+---------------+----------------+----------------+
|     SAFE      |    CAUTION     |    CRITICAL    |
+---------------+----------------+----------------+
| Green LED     | Yellow LED     | Red LED        |
| Buzzer OFF    | Buzzer OFF     | Buzzer ON      |
| Normal Speed  | Slow Speed     | Motors STOP    |
+---------------+----------------+----------------+
Relationship to SMYGN32

The physical prototype demonstrates the vehicle-level safety layer of SMYGN32.

             SMYGN32
                 |
        +--------+--------+
        |                 |
        v                 v
Digital Simulation   Physical Prototype
        |                 |
Fleet-level         Vehicle-level
risk assessment     safety demonstration
        |                 |
        +--------+--------+
                 |
                 v
        SMYGN32 Proof-of-Concept

The broader SMYGN32 architecture can be extended with V2V communication, GNSS/DGPS, industrial radar, LiDAR, thermal imaging and mine control-center integration.

These advanced components are part of the planned system architecture and are not represented as implemented in this particular low-cost hardware prototype.

Prototype Limitations

This is a scaled proof-of-concept and is not intended for direct deployment on real mine vehicles.

Current prototype limitations include:

HC-SR04 is used instead of industrial-grade radar
The physical prototype does not currently implement actual V2V communication
The physical prototype does not currently implement GNSS/DGPS
The mine environment is represented by a miniature 4WD chassis
Distance-based safety thresholds are prototype parameters
L298N is a low-cost motor driver intended for the prototype
The system is not a certified vehicle safety controller

A production implementation would require industrial-grade sensing, communication, computing and certified safety systems.

Project

SMYGN32

V2V-Enabled Collision and Trajectory Risk Assessment

Smart India Hackathon 2026

Problem Statement: SIH26007

Theme: Smart Automation

Category: Hardware
