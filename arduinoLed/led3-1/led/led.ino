#include <FastLED.h>

#define NUM_LEDS 5
#define DATA_PIN 9
#define CLOCK_PIN 7

#define FADE_STEPS 50
#define FADE_DELAY 20
#define FLUCTUATION_RANGE 3
#define FLASH_DURATION 100

CRGB leds[NUM_LEDS];
CRGB currentColor = CRGB(20, 20, 20);  // Default dim white light
CRGB targetColor = CRGB(20, 20, 20);
bool fluctuateMode = false;  // Speaking effect
bool flashFlag = false;      // Flash effect flag

void setup() {
    Serial.begin(9600);
    FastLED.addLeds<APA102, DATA_PIN, CLOCK_PIN, BGR>(leds, NUM_LEDS);
    FastLED.clear();
    FastLED.show();
    fill_solid(leds, NUM_LEDS, currentColor);
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

        if (data == "SPEAKING") {
            fluctuateMode = true;
        } 
        else if (data == "STOP SPEAKING") {
            fluctuateMode = false;
            fill_solid(leds, NUM_LEDS, currentColor);
            FastLED.show();
        } 
        else if (data.startsWith("COLOR: ")) {
            sscanf(rawData, "COLOR: %d,%d,%d", &r, &g, &b);
            transitionToColor(r, g, b);
        } 
        else if (data == "KEYWORD") {
            flashFlag = true;
        } 
        else if (data == "START SESSION" || data == "END SESSION") {
            // No effect on LED behavior
        }
    }

    if (fluctuateMode) {
        fluctuate();
    }

    if (flashFlag) {
        flash();
        flashFlag = false;
    }
}

// Smoothly transition to a new color
void transitionToColor(int targetR, int targetG, int targetB) {
    targetColor = CRGB(targetR, targetG, targetB);

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

    currentColor = targetColor;
}

// Fluctuation effect when speaking
void fluctuate() {
    int fluctuation = random(-FLUCTUATION_RANGE, FLUCTUATION_RANGE + 1);
    CRGB fluctuatedColor = CRGB(
        constrain(currentColor.r + fluctuation, 0, 40),
        constrain(currentColor.g + fluctuation, 0, 40),
        constrain(currentColor.b + fluctuation, 0, 40)
    );

    fill_solid(leds, NUM_LEDS, fluctuatedColor);
    FastLED.show();
    delay(100);
}

// Flash effect for "KEYWORD"
void flash() {
    CHSV hsvColor = rgb2hsv_approximate(currentColor);  // Convert current color to HSV
    int boostedBrightness = constrain(hsvColor.value + 80, 0, 255); // Increase brightness but stay within limits

    CHSV flashedHSV = CHSV(hsvColor.hue, hsvColor.saturation, boostedBrightness);
    CRGB flashedRGB;
    hsv2rgb_rainbow(flashedHSV, flashedRGB);  // Convert back to RGB

    // Set LED to brighter version of the current color
    fill_solid(leds, NUM_LEDS, flashedRGB);
    FastLED.show();
    delay(100);

    // Restore the original color
    fill_solid(leds, NUM_LEDS, currentColor);
    FastLED.show();
}
