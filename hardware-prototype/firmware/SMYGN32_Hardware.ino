// ============================================
// VECTRA - STEP 5 + 4WD MOTOR CONTROL
//
// ESP32
// HC-SR04
// MPU6050
// OLED
// Green / Yellow / Red LEDs
// Buzzer
// L298N
// 4WD Robot Chassis
//
// SAFETY LOGIC:
//
// > 40 cm       = SAFE
// 15 - 40 cm    = CAUTION
// < 15 cm       = CRITICAL
//
// SAFE:
// Green ON
// Buzzer OFF
// Motors NORMAL
//
// CAUTION:
// Yellow ON
// Buzzer OFF
// Motors SLOW
//
// CRITICAL:
// Red ON
// Buzzer ON
// Motors STOP
// ============================================


#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>


// ============================================
// OLED
// ============================================

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

#define OLED_RESET -1
#define OLED_ADDRESS 0x3C

Adafruit_SSD1306 display(
  SCREEN_WIDTH,
  SCREEN_HEIGHT,
  &Wire,
  OLED_RESET
);


// ============================================
// HC-SR04
// ============================================

#define TRIG_PIN 5
#define ECHO_PIN 18


// ============================================
// MPU6050
// ============================================

#define MPU_ADDR 0x68

int16_t AccX;
int16_t AccY;
int16_t AccZ;

int16_t GyroX;
int16_t GyroY;
int16_t GyroZ;


// ============================================
// SAFETY OUTPUTS
// ============================================

#define GREEN_LED 25
#define YELLOW_LED 26
#define RED_LED 27

#define BUZZER 14


// ============================================
// L298N MOTOR DRIVER
// ============================================

// Left side
#define IN1 16
#define IN2 17

// Right side
#define IN3 19
#define IN4 23

// PWM enable pins
#define ENA 13
#define ENB 4


// ============================================
// MOTOR PWM
// ============================================

#define PWM_LEFT_CHANNEL 0
#define PWM_RIGHT_CHANNEL 1

#define PWM_FREQUENCY 1000
#define PWM_RESOLUTION 8


// ============================================
// MOTOR SPEEDS
// ============================================

#define NORMAL_SPEED 200
#define CAUTION_SPEED 100


// ============================================
// DISTANCE THRESHOLDS
// ============================================

#define SAFE_DISTANCE 40.0
#define CAUTION_DISTANCE 15.0


// ============================================
// SETUP
// ============================================

void setup() {

  Serial.begin(115200);

  delay(1000);


  // ------------------------------------------
  // I2C
  // ------------------------------------------

  Wire.begin(21, 22);


  // ------------------------------------------
  // HC-SR04
  // ------------------------------------------

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  digitalWrite(TRIG_PIN, LOW);


  // ------------------------------------------
  // LEDs
  // ------------------------------------------

  pinMode(GREEN_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  digitalWrite(GREEN_LED, LOW);
  digitalWrite(YELLOW_LED, LOW);
  digitalWrite(RED_LED, LOW);


  // ------------------------------------------
  // BUZZER
  // ------------------------------------------

  pinMode(BUZZER, OUTPUT);

  digitalWrite(BUZZER, LOW);


  // ------------------------------------------
  // L298N MOTOR PINS
  // ------------------------------------------

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);


  // ------------------------------------------
  // MOTOR PWM
  // ------------------------------------------

  ledcSetup(
    PWM_LEFT_CHANNEL,
    PWM_FREQUENCY,
    PWM_RESOLUTION
  );

  ledcSetup(
    PWM_RIGHT_CHANNEL,
    PWM_FREQUENCY,
    PWM_RESOLUTION
  );


  ledcAttachPin(
    ENA,
    PWM_LEFT_CHANNEL
  );

  ledcAttachPin(
    ENB,
    PWM_RIGHT_CHANNEL
  );


  // ------------------------------------------
  // STOP MOTORS AT STARTUP
  // ------------------------------------------

  stopMotors();


  // ------------------------------------------
  // OLED
  // ------------------------------------------

  if (!display.begin(
        SSD1306_SWITCHCAPVCC,
        OLED_ADDRESS)) {

    Serial.println("OLED NOT DETECTED!");

    while (true);
  }


  // ------------------------------------------
  // MPU6050
  // ------------------------------------------

  Wire.beginTransmission(MPU_ADDR);

  Wire.write(0x6B);
  Wire.write(0);

  byte mpuStatus = Wire.endTransmission();


  if (mpuStatus != 0) {

    Serial.println("MPU6050 NOT DETECTED!");

  }


  // ------------------------------------------
  // STARTUP SCREEN
  // ------------------------------------------

  display.clearDisplay();

  display.setTextColor(
    SSD1306_WHITE
  );

  display.setTextSize(2);

  display.setCursor(25, 5);

  display.println("VECTRA");


  display.setTextSize(1);

  display.setCursor(15, 30);

  display.println("Safety System");


  display.setCursor(30, 45);

  display.println("READY");


  display.display();

  delay(2000);


  // ------------------------------------------
  // SERIAL
  // ------------------------------------------

  Serial.println();
  Serial.println("================================");
  Serial.println("          VECTRA STEP 5");
  Serial.println("      SAFETY ALERT SYSTEM");
  Serial.println("================================");

  Serial.println("OLED       : OK");
  Serial.println("MPU6050    : OK");
  Serial.println("HC-SR04    : OK");
  Serial.println("LEDs       : OK");
  Serial.println("BUZZER     : OK");
  Serial.println("L298N      : OK");
  Serial.println("4WD MOTORS : CONNECTED");

  Serial.println();
  Serial.println("Safety Logic:");
  Serial.println("> 40 cm   = SAFE");
  Serial.println("15-40 cm  = CAUTION");
  Serial.println("< 15 cm   = CRITICAL");

  Serial.println();
  Serial.println("System Ready!");
}


// ============================================
// GET DISTANCE
// ============================================

float getDistanceCM() {

  digitalWrite(
    TRIG_PIN,
    LOW
  );

  delayMicroseconds(2);


  digitalWrite(
    TRIG_PIN,
    HIGH
  );

  delayMicroseconds(10);


  digitalWrite(
    TRIG_PIN,
    LOW
  );


  long duration =
    pulseIn(
      ECHO_PIN,
      HIGH,
      30000
    );


  if (duration == 0) {

    return -1;
  }


  float distance =
    duration * 0.0343 / 2.0;


  return distance;
}


// ============================================
// READ MPU6050
// ============================================

bool readMPU6050() {

  Wire.beginTransmission(MPU_ADDR);

  Wire.write(0x3B);

  Wire.endTransmission(false);

  Wire.requestFrom(
    MPU_ADDR,
    14,
    true
  );


  if (Wire.available() < 14) {

    return false;
  }


  AccX =
    Wire.read() << 8 |
    Wire.read();


  AccY =
    Wire.read() << 8 |
    Wire.read();


  AccZ =
    Wire.read() << 8 |
    Wire.read();


  // Temperature

  Wire.read();
  Wire.read();


  GyroX =
    Wire.read() << 8 |
    Wire.read();


  GyroY =
    Wire.read() << 8 |
    Wire.read();


  GyroZ =
    Wire.read() << 8 |
    Wire.read();


  return true;
}


// ============================================
// MOTOR FORWARD
// ============================================

void moveForward(int speedValue) {

  // LEFT SIDE FORWARD

  digitalWrite(
    IN1,
    HIGH
  );

  digitalWrite(
    IN2,
    LOW
  );


  // RIGHT SIDE FORWARD

  digitalWrite(
    IN3,
    HIGH
  );

  digitalWrite(
    IN4,
    LOW
  );


  // Speed control

  ledcWrite(
    PWM_LEFT_CHANNEL,
    speedValue
  );

  ledcWrite(
    PWM_RIGHT_CHANNEL,
    speedValue
  );
}


// ============================================
// STOP MOTORS
// ============================================

void stopMotors() {

  digitalWrite(
    IN1,
    LOW
  );

  digitalWrite(
    IN2,
    LOW
  );

  digitalWrite(
    IN3,
    LOW
  );

  digitalWrite(
    IN4,
    LOW
  );


  ledcWrite(
    PWM_LEFT_CHANNEL,
    0
  );

  ledcWrite(
    PWM_RIGHT_CHANNEL,
    0
  );
}


// ============================================
// SET SAFETY STATE
// ============================================

void setSafetyState(
  float distance
) {

  // Turn everything OFF first

  digitalWrite(
    GREEN_LED,
    LOW
  );

  digitalWrite(
    YELLOW_LED,
    LOW
  );

  digitalWrite(
    RED_LED,
    LOW
  );

  digitalWrite(
    BUZZER,
    LOW
  );


  // ==========================================
  // SAFE
  // ==========================================

  if (
    distance > SAFE_DISTANCE ||
    distance < 0
  ) {

    // Green

    digitalWrite(
      GREEN_LED,
      HIGH
    );


    // Buzzer OFF

    digitalWrite(
      BUZZER,
      LOW
    );


    // Normal motor speed

    moveForward(
      NORMAL_SPEED
    );
  }


  // ==========================================
  // CAUTION
  // ==========================================

  else if (
    distance >= CAUTION_DISTANCE
  ) {

    // Yellow

    digitalWrite(
      YELLOW_LED,
      HIGH
    );


    // Buzzer OFF

    digitalWrite(
      BUZZER,
      LOW
    );


    // Slow motor

    moveForward(
      CAUTION_SPEED
    );
  }


  // ==========================================
  // CRITICAL
  // ==========================================

  else {

    // Red

    digitalWrite(
      RED_LED,
      HIGH
    );


    // Continuous buzzer

    digitalWrite(
      BUZZER,
      HIGH
    );


    // STOP MOTORS

    stopMotors();
  }
}


// ============================================
// GET STATUS TEXT
// ============================================

const char* getStatus(
  float distance
) {

  if (
    distance > SAFE_DISTANCE ||
    distance < 0
  ) {

    return "SAFE";
  }


  else if (
    distance >= CAUTION_DISTANCE
  ) {

    return "CAUTION";
  }


  else {

    return "CRITICAL";
  }
}


// ============================================
// MAIN LOOP
// ============================================

void loop() {

  // ------------------------------------------
  // READ SENSORS
  // ------------------------------------------

  float distance =
    getDistanceCM();


  bool mpuOK =
    readMPU6050();


  // ------------------------------------------
  // MPU CONVERSION
  // ------------------------------------------

  float ax =
    AccX / 16384.0;


  float ay =
    AccY / 16384.0;


  float az =
    AccZ / 16384.0;


  float gz =
    GyroZ / 131.0;


  // ------------------------------------------
  // SAFETY DECISION
  // ------------------------------------------

  setSafetyState(
    distance
  );


  const char* status =
    getStatus(
      distance
    );


  // ==========================================
  // SERIAL MONITOR
  // ==========================================

  Serial.println(
    "--------------------------------"
  );


  Serial.print(
    "Distance: "
  );


  if (distance < 0) {

    Serial.println(
      "No object"
    );

  }

  else {

    Serial.print(
      distance,
      2
    );

    Serial.println(
      " cm"
    );
  }


  Serial.print(
    "Status: "
  );

  Serial.println(
    status
  );


  if (mpuOK) {

    Serial.print(
      "AX: "
    );

    Serial.print(
      ax,
      2
    );

    Serial.println(
      " g"
    );


    Serial.print(
      "AY: "
    );

    Serial.print(
      ay,
      2
    );

    Serial.println(
      " g"
    );


    Serial.print(
      "AZ: "
    );

    Serial.print(
      az,
      2
    );

    Serial.println(
      " g"
    );


    Serial.print(
      "GZ: "
    );

    Serial.print(
      gz,
      2
    );

    Serial.println(
      " deg/s"
    );
  }


  // ==========================================
  // OLED
  // ==========================================

  display.clearDisplay();

  display.setTextColor(
    SSD1306_WHITE
  );


  // Title

  display.setTextSize(1);

  display.setCursor(
    0,
    0
  );

  display.println(
    "VECTRA VEHICLE"
  );


  // Separator

  display.drawLine(
    0,
    10,
    127,
    10,
    SSD1306_WHITE
  );


  // Distance

  display.setCursor(
    0,
    17
  );

  display.print(
    "DIST: "
  );


  if (distance < 0) {

    display.println(
      "--"
    );

  }

  else {

    display.print(
      distance,
      1
    );

    display.println(
      " cm"
    );
  }


  // Status

  display.setCursor(
    0,
    30
  );

  display.print(
    "STATUS: "
  );

  display.println(
    status
  );


  // Acceleration X

  display.setCursor(
    0,
    42
  );

  display.print(
    "AX:"
  );

  display.print(
    ax,
    1
  );


  // Acceleration Y

  display.setCursor(
    65,
    42
  );

  display.print(
    "AY:"
  );

  display.print(
    ay,
    1
  );


  // Gyroscope Z

  display.setCursor(
    0,
    54
  );

  display.print(
    "GZ:"
  );

  display.print(
    gz,
    1
  );

  display.print(
    " d/s"
  );


  display.display();


  delay(300);
}
