#include <FastLED.h>

#define NUM_LEDS 5
#define DATA_PIN 9
#define CLOCK_PIN 7

#define FADE_STEPS 50
#define FADE_DELAY 20 

CRGB leds[NUM_LEDS];
CRGB currentColor = CRGB(0, 0, 0); 

void setup() {
  Serial.begin(9600);
  FastLED.addLeds<APA102, DATA_PIN, CLOCK_PIN, BGR>(leds, NUM_LEDS);
  FastLED.clear();
  FastLED.show();
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    data.trim(); 

    Serial.print("Received data: ");
    Serial.println(data);

    int r, g, b;
    char rawData[20];
    data.toCharArray(rawData, sizeof(rawData));

    if (sscanf(rawData, "%d,%d,%d", &r, &g, &b) == 3) { 
      Serial.print("RGB: ");
      Serial.print(r); Serial.print(",");
      Serial.print(g); Serial.print(",");
      Serial.println(b);

      transitionToColor(r, g, b);
    } else {
      Serial.println("Failed to parse RGB data");
    }
  }
}

void transitionToColor(int targetR, int targetG, int targetB) {
  CRGB targetColor = CRGB(targetR, targetG, targetB);

  if (currentColor == CRGB(0, 0, 0)) {
    fill_solid(leds, NUM_LEDS, targetColor);
    FastLED.show();
  } else {

    for (int step = 0; step <= FADE_STEPS; step++) {
      float blendFactor = (float)step / FADE_STEPS;

      CRGB blendedColor = CRGB(
        (1 - blendFactor) * currentColor.r + blendFactor * targetR,
        (1 - blendFactor) * currentColor.g + blendFactor * targetG,
        (1 - blendFactor) * currentColor.b + blendFactor * targetB
      );

      fill_solid(leds, NUM_LEDS, blendedColor);
      FastLED.show();
      delay(FADE_DELAY);
    }
  }

  currentColor = targetColor;
}
