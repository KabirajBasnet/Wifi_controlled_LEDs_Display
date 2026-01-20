// You can change the pattern to your liking with just some basic logic(same as python)
#include <ESP8266WiFi.h>
#include <espnow.h>
#include <Adafruit_NeoPixel.h>
#define MY_STRIP_ID 21  // CHANGE for each ESP-01
#define LED_PIN   2          // GPIO2 (ESP-01 safe)
#define WIDTH     300
#define HEIGHT    4
#define NUM_LEDS  (WIDTH * HEIGHT)
Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);
uint8_t stars[NUM_LEDS];
#define lefthandstart 42
#define lefthandend 91
#define righthandstart 307
#define righthandend 356
#define brightness 255
unsigned long lastSendHanuman = 0;
const unsigned long INTERVAL_HANUMAN = 20;
float phase = 0.0;
void hanumanAnime() {
  unsigned long now = millis();
  if (now - lastSendHanuman < INTERVAL_HANUMAN) return;
  lastSendHanuman = now;
  float t = (sin(phase) + 1.0) * 0.5;
  uint8_t r = 255;
  uint8_t g = (uint8_t)(100 * t) + 30;
  uint8_t b = 0;
  for (uint16_t i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, r, g, b);
  }
  strip.show();
  phase += 0.08;
}
uint16_t XY(uint16_t x, uint16_t y) {
  if (y % 2 == 0) {
    return y * WIDTH + x;
  } else {
    return y * WIDTH + (WIDTH - 1 - x);
  }
}
typedef struct __attribute__((packed)) {
  uint8_t origin_id;
  uint8_t sender_id;
  uint8_t hop_count;
  uint16_t packet_id;
  uint8_t strip_id;
  uint8_t pattern;
  uint8_t r;
  uint8_t g;
  uint8_t b;
  uint8_t dresspart;
} Command;
Command cmd;
bool play = false;
void onReceive(uint8_t *mac, uint8_t *data, uint8_t len) {
  
  memcpy(&cmd, data, sizeof(cmd));

  if (cmd.strip_id == MY_STRIP_ID){
    play = true;
  }
  else{
    play = false;
  }
}
unsigned long lastTwinkleUpdate = 0;
const unsigned long TWINKLE_INTERVAL = 20;
void updateTwinkles() {
  unsigned long now = millis();
  if (now - lastTwinkleUpdate < TWINKLE_INTERVAL) return;
  lastTwinkleUpdate = now;
  for (uint16_t i = 0; i < NUM_LEDS; i++) {
    if (stars[i] > 2) stars[i] -= 2;
    else stars[i] = 0;
    strip.setPixelColor(
      i,
      stars[i] / 3,
      stars[i] / 3,
      stars[i]
    );
  }
  if (random(100) < 30) {
    uint16_t p = random(NUM_LEDS);
    stars[p] = random(150, 255);
  }
  strip.show();
}
unsigned long lastUpdate = 0;
const uint16_t intervalwavefire = 10;
float waveOffset = 0;
void waveFire() {
  unsigned long now = millis();
  if (now - lastUpdate < intervalwavefire) return;
  lastUpdate = now;
  for (uint16_t col = 0; col < WIDTH; col++) {
    float wave = sin((col * 0.08) + waveOffset);
    float intensity = (wave + 1.0) * 0.5;
    uint8_t r = 255;
    uint8_t g = 20 + (int)(105 * intensity);
    uint8_t b = 0;
    for (uint8_t row = 0; row < HEIGHT; row++) {
      uint16_t idx = row * WIDTH + col;
      strip.setPixelColor(idx, r, g, b);
    }
  }
  strip.show();
  waveOffset += 0.12;  // speed
}
const uint8_t GOLD_R = 239;
const uint8_t GOLD_G = 72;
const uint8_t GOLD_B = 24;
unsigned long lastUpdategold = 0;
const unsigned long INTERVALgold = 30;
void goldShimmer() {
  unsigned long nowgold = millis();
  if (nowgold - lastUpdategold < INTERVALgold) return;
  lastUpdategold = nowgold;
  for (uint16_t i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, GOLD_R, GOLD_G, GOLD_B);
  }
  uint8_t sparkles = random(5, 12);
  for (uint8_t i = 0; i < sparkles; i++) {
    uint16_t p = random(NUM_LEDS);
    strip.setPixelColor(p, 255, 255, 220);
  }
  strip.show();
}
void setup() {
  strip.begin();
  strip.clear();
  strip.show();
  randomSeed(ESP.getCycleCount());
  strip.setBrightness(brightness);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  wifi_set_channel(1);
  esp_now_init();
  esp_now_set_self_role(ESP_NOW_ROLE_SLAVE);
  esp_now_register_recv_cb(onReceive);
}
void loop() {
  unsigned long now = millis();
  if (play == true){  
    if (cmd.pattern == 1){  
      for (int i = 0; i < NUM_LEDS; i++) {
        strip.setPixelColor(i, strip.Color(cmd.r, cmd.g, cmd.b));
      }
      strip.show();
    } else if (cmd.pattern == 4){
      updateTwinkles();
    } else if (cmd.pattern == 5){
      waveFire();
    } else if (cmd.pattern == 6){
      hanumanAnime();
    } else if(cmd.pattern == 7){
      goldShimmer();
    }
  }
}
