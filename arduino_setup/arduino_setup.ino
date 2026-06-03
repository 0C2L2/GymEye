#include <Servo.h>

Servo pan;
Servo tilt;

int panPos = 90;   // current pan position (45-135)
int tiltPos = 90;  // current tilt position (45-135)

void setup() {
  Serial.begin(9600);
  tilt.attach(10);
  pan.attach(9);
  
  // For continuous rotation pan servo
  // 90 = stop, <90 = one direction, >90 = other direction
  pan.write(90);   // stop
  tilt.write(90);  // center
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    if (cmd == "PAN:LEFT") {
      pan.write(100);  // swapped
      delay(500);
      pan.write(90);   // stop
    }
    else if (cmd == "PAN:RIGHT") {
      pan.write(80);   // swapped
      delay(500);
      pan.write(90);   // stop
    }
    else if (cmd == "PAN:STOP") {
      pan.write(90);  // stop
    }
    else if (cmd.startsWith("TILT:")) {
      int angle = cmd.substring(5).toInt();
      angle = constrain(angle, 45, 135);
      tiltPos = angle;
      tilt.write(tiltPos);
    }
  }
}