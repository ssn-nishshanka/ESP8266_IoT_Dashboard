// Reads temperature and humidity from the DHT11
// Detects light presence from a digital light sensor
// Sends data via Serial in CSV format

#include <DHT.h>

// Define pins
#define DHTPIN D4      
#define DHTTYPE DHT11
#define LIGHTPIN D5    

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);  // Start serial communication
  dht.begin();           // Initialize DHT sensor
  pinMode(LIGHTPIN, INPUT);  // Light sensor digital output
  delay(2000);  // Allow DHT11 and sensor to stabilize
}

void loop() {
  // Read temperature and humidity
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  // Skip loop if DHT11 reading fails
  if (isnan(temp) || isnan(hum)) {
    Serial.println("Error: Failed to read from DHT sensor!");
    delay(2000);
    return;
  }

  // Read light sensor and invert logic
  // Sensor output: 0 = light present, 1 = no light
  int rawLight = digitalRead(LIGHTPIN);
  int lightDetected = (rawLight == 0) ? 1 : 0;  // 1 = light present, 0 = no light

  // Print CSV only: temp,humidity,light
  Serial.print(temp); 
  Serial.print(",");
  Serial.print(hum); 
  Serial.print(",");
  Serial.println(lightDetected);

  delay(2000); // Read every 2 seconds
}
