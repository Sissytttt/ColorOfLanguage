// color grad change

#include <FastLED.h>

#define NUM_LEDS 5
#define DATA_PIN 9
#define CLOCK_PIN 7

#define FADE_STEPS 50
#define FADE_DELAY 20
#define FLUCTUATION_RANGE 2
#define FLASH_DURATION 100

CRGB leds[NUM_LEDS];
CRGB currentColor = CRGB(20, 20, 20);  // Default dim white light
CRGB targetColor = CRGB(20, 20, 20);
bool fluctuateMode = false;  // Speaking effect
bool flashFlag = false;      // Flash effect flag


void fadeIn(CRGB target, int steps, int delayMs);


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
            fadeIn(currentColor, 30, 20);
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
        displaySeparateRGB(blendedColor);
        delay(FADE_DELAY);
    }

    currentColor = targetColor;
}


// Fluctuation effect when speaking
void fluctuate() {
    static float t = 0.0;  // 时间变量
    static float speed = 0.1;  // 呼吸速度
    static float base = 0.8;   // 基础亮度（百分比）
    static float range = 0.2;  // 呼吸幅度（亮度浮动范围）

    t += speed;

    float brightnessFactor = base + range * sin(t);  // 让亮度上下浮动 (sin波)
    
    int fluctuation = random(-FLUCTUATION_RANGE, FLUCTUATION_RANGE + 1);

    CRGB fluctuatedColor = CRGB(
        constrain(currentColor.r * brightnessFactor + fluctuation, 0, 255),
        constrain(currentColor.g * brightnessFactor + fluctuation, 0, 255),
        constrain(currentColor.b * brightnessFactor + fluctuation, 0, 255)
    );

    displaySeparateRGB(fluctuatedColor);
    delay(50);  // 稍微短一点点，呼吸更顺滑
}

// Flash effect for "KEYWORD"
void flash() {
    CHSV hsvColor = rgb2hsv_approximate(currentColor);  // Convert current color to HSV
    int boostedBrightness = constrain(hsvColor.value + 10, 0, 255); // Increase brightness but stay within limits

    CHSV flashedHSV = CHSV(hsvColor.hue, hsvColor.saturation, boostedBrightness);
    CRGB flashedRGB;
    hsv2rgb_rainbow(flashedHSV, flashedRGB);  // Convert back to RGB

    // Set LED to brighter version of the current color
    displaySeparateRGB(flashedRGB);
    delay(100);

    // Restore the original color
    displaySeparateRGB(flashedRGB);
}



void fadeIn(CRGB target, int steps = 30, int delayMs = 20) {
    for (int i = 0; i <= steps; i++) {
        float brightnessFactor = (float)i / steps;
        CRGB fadedColor = CRGB(
            target.r * brightnessFactor,
            target.g * brightnessFactor,
            target.b * brightnessFactor
        );
        displaySeparateRGB(fadedColor);
        delay(delayMs);
    }
}


void displaySeparateRGB(CRGB color) {
    for (int i = 0; i < NUM_LEDS; i++) {
        int channel = i % 3;
        if (channel == 0) {
            leds[i] = CRGB(color.r, 0, 0);
        } else if (channel == 1) {
            leds[i] = CRGB(0, color.g, 0);
        } else {
            leds[i] = CRGB(0, 0, color.b);
        }
    }
    FastLED.show();
}

