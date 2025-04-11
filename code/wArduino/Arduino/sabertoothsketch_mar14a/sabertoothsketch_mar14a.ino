// =======================================================================================
//                              Arduino Robot Controller (Automatic Mode)
// =======================================================================================
//                          Last Revised Date: 03/14/2025
//                             Revised By: ChatGPT (Based on Prof McLaughlin's Code)
// =======================================================================================
// ---------------------------------------------------------------------------------------
//                          Libraries
// ---------------------------------------------------------------------------------------
#include <Sabertooth.h>
#include <Wire.h>

#define I2C_ADDRESS 0x08  // I2C address (not used in automatic mode)
String I2CInboundString = ""; // Buffer for storing the received data

// ---------------------------------------------------------------------------------------
//    Timer Controller Variable
// ---------------------------------------------------------------------------------------
long currentTime = millis();

// ---------------------------------------------------------------------------------------
//    Motor Control Variables
// ---------------------------------------------------------------------------------------
#define SABERTOOTH_ADDR 128
Sabertooth *ST = new Sabertooth(SABERTOOTH_ADDR, Serial1); // TX1 → Pin#18

int driveDeadBandRange = 10;
int currentSpeed = 0;
int currentTurn = 0;
boolean robotMoving = false;

// ---------------------------------------------------------------------------------------
//    Setup Function
// ---------------------------------------------------------------------------------------
void setup() {
    Serial.begin(115200);      // Serial monitor for debugging
    Serial3.begin(115200);     // Serial3 for Raspberry Pi communication

    Serial.println("Automatic Mode Started");

    // Initialize Sabertooth Motor Controller
    Serial1.begin(9600); 
    ST->autobaud();
    ST->setTimeout(200);
    ST->setDeadband(driveDeadBandRange);

    // Set pin 13 for heartbeat LED
    pinMode(13, OUTPUT);
    digitalWrite(13, LOW);
}

// =======================================================================================
//    Main Program Loop
// =======================================================================================
void loop() {
    currentTime = millis();
    
    // Check for incoming serial messages from Raspberry Pi
    check_inbound_serial_message();

    // Blink Arduino LED to show it's alive
    blink_status_led();
}

// =======================================================================================
//    Function to Move Robot Based on Command
// =======================================================================================
void moveRobot(String command) {
    if (command == "F") {
        Serial.println("Moving Forward");
        ST->drive(-150);  // Move forward at speed 150
        ST->turn(0);
        robotMoving = true;
    } 
    else if (command == "L") {
        Serial.println("Turning Left");
        ST->drive(0);   // Stop forward movement
        ST->turn(100); // Turn left
        delay(1000);    // Adjust turn duration as needed
        ST->turn(0);    // Stop turning
    } 
    else if (command == "R") {
        Serial.println("Turning Right");
        ST->drive(0);   // Stop forward movement
        ST->turn(-100);  // Turn right
        delay(1000);    // Adjust turn duration as needed
        ST->turn(0);    // Stop turning
    } 
    else if (command == "S") {
        Serial.println("Stopping");
        ST->stop();
        robotMoving = false;
    }
}

// =======================================================================================
//    Function to Check Serial Messages from Raspberry Pi
// =======================================================================================
void check_inbound_serial_message() {
    static String message = ""; // Buffer to store incoming messages

    // Read data from Serial3 (Raspberry Pi)
    while (Serial3.available() > 0) {
        char incomingChar = Serial3.read();

        // Check for message termination character '%'
        if (incomingChar == '%') {
            Serial.println("Received Command: " + message);
            
            // Process movement command
            moveRobot(message);

            // Clear buffer for next command
            message = "";
        } else {
            message += incomingChar;
        }
    }
}

// =======================================================================================
//    Function to Blink LED for Heartbeat
// =======================================================================================
void blink_status_led() {
    static long blinkMillis = millis();
    static boolean blinkOn = false;

    if ((blinkMillis + 500) < currentTime) {
        if (blinkOn) {
            digitalWrite(13, LOW);
            blinkOn = false;
        } else {
            digitalWrite(13, HIGH);
            blinkOn = true;
        }
        blinkMillis = millis();
    }
}
