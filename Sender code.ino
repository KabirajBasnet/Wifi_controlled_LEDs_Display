// This code works for ESP8266 only.
// ESP-NOW for ESP32 has different API from the ESP8266 implementation
#include <ESP8266WiFi.h>
#include <espnow.h>
#define RETRY_INTERVAL 5000
#define SEND_INTERVAL 1000 
uint8_t remoteMac[] = {0x82, 0x88, 0x88, 0x88, 0x88, 0x88};
const uint8_t channel = 14;
struct __attribute__((packed)) DataStruct {
  uint8_t target;
  uint8_t pattern;
  uint8_t r;
  uint8_t g;
  uint8_t b;
};
DataStruct myData;
unsigned long sentStartTime;
unsigned long lastSentTime;
void sendData() {
  uint8_t bs[sizeof(myData)];
  memcpy(bs, &myData, sizeof(myData));

  sentStartTime = micros();
  esp_now_send(NULL, bs, sizeof(myData));
}
void sendCallBackFunction(uint8_t* mac, uint8_t sendStatus) {
  unsigned long sentEndTime = micros();
  Serial.printf("Status: %s\n", (sendStatus == 0 ? "Success" : "Failed"));
}

void setup() {
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  Serial.begin(115200);
  Serial.println();
  if (esp_now_init() != 0) {
    Serial.println("ESP_Now init failed...");
    delay(RETRY_INTERVAL);
    ESP.restart();
  }
  esp_now_set_self_role(ESP_NOW_ROLE_CONTROLLER);
  esp_now_add_peer(remoteMac, ESP_NOW_ROLE_SLAVE, channel, NULL, 0);
  esp_now_register_send_cb(sendCallBackFunction);
}
void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    int id, pattern, r, g, b;
    int count = sscanf(line.c_str(), "%d %d %d %d %d",
                       &id, &pattern, &r, &g, &b);
    if (count == 5) {
      myData.target  = (uint8_t)id;
      myData.pattern = (uint8_t)pattern;
      myData.r = (uint8_t)r;
      myData.g = (uint8_t)g;
      myData.b = (uint8_t)b;
      sendData();
    } else {
      Serial.println("Invalid format!");
    }
  }
}
