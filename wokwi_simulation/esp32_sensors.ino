#include <WiFi.h>
#include <ThingSpeak.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Pin definitions
#define SOUND_SENSOR_PIN 34
#define FLAME_SENSOR_PIN 26
#define MOTION_SENSOR_PIN 27

// WiFi credentials
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// ThingSpeak settings
const char* thingSpeakApiKey = "9OEJ8JT742BJSI8C"; // Replace with your Write API Key
unsigned long thingSpeakChannelID = 2996674;  // replace with your ThingSpeak Channel ID

WiFiClient client;
LiquidCrystal_I2C lcd(0x27, 20, 4);

// Variables
int soundValue = 0;
bool flameDetected = false;
bool motionDetected = false;

unsigned long lastSoundPatternChange = 0;
const unsigned long patternChangeDuration = 30000; // 30 seconds
int currentSoundPattern = 0;
const char* soundPatternNames[] = {"normal", "glass_break", "fire_crackle", "human_scream", "dog_bark"};

unsigned long lastThingSpeakUpdate = 0;
const unsigned long thingSpeakInterval = 15000; // 15 seconds

// Timer for toggling flame and motion detection
unsigned long lastToggleTime = 0;
const unsigned long toggleInterval = 30000; // 30 seconds

void setup() {
  Serial.begin(115200);
  pinMode(SOUND_SENSOR_PIN, INPUT);
  pinMode(FLAME_SENSOR_PIN, INPUT);
  pinMode(MOTION_SENSOR_PIN, INPUT);

  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Smart Home Secure");

  delay(1500);
  lcd.clear();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  lcd.setCursor(0, 0);
  lcd.print("Connecting WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected.");
  lcd.setCursor(0, 0);
  lcd.print("WiFi Connected");

  ThingSpeak.begin(client);
  randomSeed(analogRead(35));
  
  // Initialize flame and motion detection values
  flameDetected = false;
  motionDetected = false;
  lastToggleTime = millis(); // Start the toggle timer
}

void loop() {
  unsigned long now = millis();
  
  // Check if it's time to toggle flame and motion detection
  if (now - lastToggleTime > toggleInterval) {
    lastToggleTime = now;
    flameDetected = !flameDetected;
    motionDetected = !motionDetected;
    Serial.println("Toggled flame and motion detection");
    Serial.print("Flame: ");
    Serial.println(flameDetected ? "YES" : "NO");
    Serial.print("Motion: ");
    Serial.println(motionDetected ? "YES" : "NO");
  }
  
  simulateSensorReadings();
  printSensorValues();

  if (now - lastThingSpeakUpdate > thingSpeakInterval) {
    lastThingSpeakUpdate = now;
    sendToThingSpeak();
  }

  if (now - lastSoundPatternChange > patternChangeDuration) {
    lastSoundPatternChange = now;
    currentSoundPattern = random(5);
    Serial.println("\nSound pattern changed");
    Serial.print("New pattern: ");
    Serial.print(currentSoundPattern);
    Serial.print(" (");
    Serial.print(soundPatternNames[currentSoundPattern]);
    Serial.println(")");
  }

  delay(1000);
}

void simulateSensorReadings() {
  // Only simulate sound values based on the current pattern
  // Flame and motion detection are now toggled every 30 seconds
  switch (currentSoundPattern) {
    case 0: soundValue = random(300, 450); break;
    case 1: soundValue = random(700, 900); break;
    case 2: soundValue = random(500, 650); break;
    case 3: soundValue = random(750, 900); break;
    case 4: soundValue = random(600, 750); break;
  }
  
  // flameDetected and motionDetected are now controlled by the toggle timer
}

void printSensorValues() {
  Serial.println("\n--- Sensor Readings ---");
  Serial.print("Sound: ");
  Serial.print(soundValue);
  Serial.print(" (");
  Serial.print(soundPatternNames[currentSoundPattern]);
  Serial.println(")");

  Serial.print("Flame: ");
  Serial.println(flameDetected ? "YES" : "NO");

  Serial.print("Motion: ");
  Serial.println(motionDetected ? "YES" : "NO");

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Snd:");
  lcd.print(soundValue);
  lcd.print(" ");
  lcd.print(currentSoundPattern);

  lcd.setCursor(0, 1);
  lcd.print("Flm:");
  lcd.print(flameDetected ? "Y" : "N");
  lcd.print(" Mtn:");
  lcd.print(motionDetected ? "Y" : "N");
}

void sendToThingSpeak() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected.");
    lcd.setCursor(0, 3);
    lcd.print("WiFi Down");
    return;
  }

  ThingSpeak.setField(1, soundValue);
  ThingSpeak.setField(2, flameDetected ? 1 : 0);
  ThingSpeak.setField(3, motionDetected ? 1 : 0);
  ThingSpeak.setField(4, currentSoundPattern);

  int statusCode = ThingSpeak.writeFields(thingSpeakChannelID, thingSpeakApiKey);

  if (statusCode == 200) {
    Serial.println("Data sent to ThingSpeak.");
    lcd.setCursor(0, 3);
    lcd.print("Sent to TS OK    ");
  } else {
    Serial.print("ThingSpeak Error: ");
    Serial.println(statusCode);
    lcd.setCursor(0, 3);
    lcd.print("TS Error:");
    lcd.print(statusCode);
  }
}
