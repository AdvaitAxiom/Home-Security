/*
 * Smart Home Anomaly Detection System
 * ESP32 Sensor Simulation for Wokwi
 * 
 * This code simulates three sensors:
 * 1. Sound sensor (analog) - connected to pin 34
 * 2. Flame sensor (digital) - connected to pin 26
 * 3. PIR motion sensor (digital) - connected to pin 27
 * 
 * The ESP32 reads data from these sensors and sends it to ThingSpeak
 * for further processing by the AI model.
 */

#include <WiFi.h>        // WiFi library for ESP32
#include <HTTPClient.h>  // HTTP client for making API requests
#include <time.h>        // For timestamp generation

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";      // Replace with your WiFi SSID
const char* password = "YOUR_WIFI_PASSWORD";  // Replace with your WiFi password

// ThingSpeak settings
const char* thingSpeakServer = "api.thingspeak.com";
const String apiKey = "YOUR_THINGSPEAK_WRITE_API_KEY";  // Replace with your ThingSpeak Write API Key
const unsigned long channelID = 0000000;  // Replace with your ThingSpeak Channel ID

// Sensor pins
const int soundSensorPin = 34;  // Analog pin for sound sensor
const int flameSensorPin = 26;  // Digital pin for flame sensor
const int motionSensorPin = 27; // Digital pin for PIR motion sensor

// NTP Server for time synchronization
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 0;  // GMT offset in seconds (adjust for your timezone)
const int daylightOffset_sec = 3600;  // Daylight saving time offset in seconds

// Variables to store sensor readings
int soundValue = 0;
bool flameDetected = false;
bool motionDetected = false;

// Variables for sound pattern simulation
unsigned long lastSoundPatternChange = 0;
const unsigned long patternChangeDuration = 10000;  // Change pattern every 10 seconds
int currentSoundPattern = 0;  // 0: normal, 1: glass break, 2: fire crackle, 3: human scream, 4: dog bark
const char* soundPatternNames[] = {"normal", "glass_break", "fire_crackle", "human_scream", "dog_bark"};

// Variables for data sending
unsigned long lastDataSendTime = 0;
const unsigned long dataSendInterval = 15000;  // Send data every 15 seconds (ThingSpeak limit)

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  delay(1000);  // Give time for serial to initialize
  
  // Set pin modes
  pinMode(soundSensorPin, INPUT);
  pinMode(flameSensorPin, INPUT);
  pinMode(motionSensorPin, INPUT);
  
  // Connect to WiFi
  connectToWiFi();
  
  // Initialize time
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  
  // Initialize random seed for simulation
  randomSeed(analogRead(35));  // Use an unconnected analog pin for random seed
  
  Serial.println("Smart Home Anomaly Detection System initialized!");
}

void loop() {
  // Simulate sensor readings
  simulateSensorReadings();
  
  // Print sensor values to serial monitor
  printSensorValues();
  
  // Send data to ThingSpeak at specified intervals
  unsigned long currentMillis = millis();
  if (currentMillis - lastDataSendTime >= dataSendInterval) {
    lastDataSendTime = currentMillis;
    sendDataToThingSpeak();
  }
  
  // Change sound pattern periodically for simulation
  if (currentMillis - lastSoundPatternChange >= patternChangeDuration) {
    lastSoundPatternChange = currentMillis;
    // Randomly select a new sound pattern
    currentSoundPattern = random(5);  // 0-4 for the different patterns
    Serial.print("Changed sound pattern to: ");
    Serial.println(soundPatternNames[currentSoundPattern]);
  }
  
  delay(1000);  // Small delay between readings
}

// Function to connect to WiFi
void connectToWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  
  // Wait for connection
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.print("Connected to WiFi. IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("");
    Serial.println("Failed to connect to WiFi. Check credentials or network.");
  }
}

// Function to simulate sensor readings
void simulateSensorReadings() {
  // Simulate sound sensor based on current pattern
  switch (currentSoundPattern) {
    case 0:  // Normal
      soundValue = random(300, 450);  // Lower amplitude for normal sounds
      break;
    case 1:  // Glass break
      soundValue = random(700, 900);  // High amplitude spike
      break;
    case 2:  // Fire crackle
      soundValue = random(500, 650);  // Medium amplitude with variations
      break;
    case 3:  // Human scream
      soundValue = random(750, 900);  // Very high amplitude
      break;
    case 4:  // Dog bark
      soundValue = random(600, 750);  // High amplitude but shorter than scream
      break;
  }
  
  // Simulate flame sensor (occasionally detect flame)
  if (random(100) < 5) {  // 5% chance of flame detection
    flameDetected = true;
  } else {
    flameDetected = false;
  }
  
  // Simulate motion sensor (more frequent motion detection)
  if (random(100) < 20) {  // 20% chance of motion detection
    motionDetected = true;
  } else {
    motionDetected = false;
  }
}

// Function to print sensor values to serial monitor
void printSensorValues() {
  Serial.println("\n----- Sensor Readings -----");
  Serial.print("Sound Amplitude: ");
  Serial.print(soundValue);
  Serial.print(" (Pattern: ");
  Serial.print(soundPatternNames[currentSoundPattern]);
  Serial.println(")");
  
  Serial.print("Flame Detected: ");
  Serial.println(flameDetected ? "YES" : "NO");
  
  Serial.print("Motion Detected: ");
  Serial.println(motionDetected ? "YES" : "NO");
}

// Function to get current timestamp as string
String getTimestamp() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    return "";
  }
  char timeStringBuff[50];
  strftime(timeStringBuff, sizeof(timeStringBuff), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  return String(timeStringBuff);
}

// Function to send data to ThingSpeak
void sendDataToThingSpeak() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected. Reconnecting...");
    connectToWiFi();
    return;
  }
  
  HTTPClient http;
  
  // Prepare URL with API key and field values
  String url = "http://" + String(thingSpeakServer) + "/update?api_key=" + apiKey;
  url += "&field1=" + String(soundValue);  // Sound amplitude
  url += "&field2=" + String(flameDetected ? 1 : 0);  // Flame sensor (0/1)
  url += "&field3=" + String(motionDetected ? 1 : 0);  // Motion sensor (0/1)
  url += "&field4=" + String(currentSoundPattern);  // Sound pattern type
  
  // Begin HTTP connection
  http.begin(url);
  
  // Send HTTP GET request
  int httpResponseCode = http.GET();
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("Data sent to ThingSpeak successfully.");
    Serial.print("Response code: ");
    Serial.println(httpResponseCode);
  } else {
    Serial.print("Error sending data. Error code: ");
    Serial.println(httpResponseCode);
  }
  
  // Free resources
  http.end();
}