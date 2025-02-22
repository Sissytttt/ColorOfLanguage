
#include <FastLED.h>

// How many LEDs in your strip?
#define NUM_LEDS 5

// Define the pin for the data line
#define DATA_PIN 5

// Define the array of LEDs
CRGB leds[NUM_LEDS];

// Gamma color correction table
const uint8_t PROGMEM gamma8[] = {
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255 
};

void setup() {
  Serial.begin(9600);
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
}

void loop() {
  if (Serial.available()) {
    String hexColor = Serial.readStringUntil('\n');
    hexColor.trim();
    
    // Convert the hex color to RGB values
    int r = strtol(hexColor.substring(1, 3).c_str(), NULL, 16);
    int g = strtol(hexColor.substring(3, 5).c_str(), NULL, 16);
    int b = strtol(hexColor.substring(5, 7).c_str(), NULL, 16);

    // Apply gamma correction
    r = pgm_read_byte(&gamma8[r]);
    g = pgm_read_byte(&gamma8[g]);
    b = pgm_read_byte(&gamma8[b]);

    // Set the LEDs to the received RGB color
    for (int i = 0; i < NUM_LEDS; i++) {
      leds[i] = CRGB(r, g, b);
    }
    FastLED.show();

    // Print the color values to the Serial Monitor
    Serial.print("Hex: ");
    Serial.println(hexColor);
    Serial.print("RGB: ");
    Serial.print("R=");
    Serial.print(r);
    Serial.print(" G=");
    Serial.print(g);
    Serial.print(" B=");
    Serial.println(b);
  }
}





// #include <FastLED.h>

// // How many LEDs in your strip?
// #define NUM_LEDS 5

// // Define the pin for the data line
// #define DATA_PIN 5

// // Define the array of LEDs
// CRGB leds[NUM_LEDS];

// // Gamma color correction table
// const uint8_t PROGMEM gamma8[] = {
//     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
//     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
//     1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
//     2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
//     5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
//    10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
//    17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
//    25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
//    37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
//    51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
//    69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
//    90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
//   115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
//   144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
//   177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
//   215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255 
// };

// bool pulsing = true;    // Start with pulsing on power-up
// bool colorChanged = false;
// String currentColor = "#FFFFFF"; // Default white color

// void setup() {
//   Serial.begin(9600);
//   FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
//   FastLED.clear();
//   FastLED.show();
// }

// void loop() {
//   if (Serial.available()) {
//     String command = Serial.readStringUntil('\n');
//     command.trim();
//   }

//   if (pulsing) {
//     runLEDSequence(); // Pulsing effect on power-up
//   } else if (colorChanged) {
//     // Cycle through pulsing effect once
//     runLEDSequence();
//     // Change to the new color after pulsing
//     applyColor(currentColor);
//     colorChanged = false;
//     pulsing = true; // Reset pulsing for future commands
//   }
// }

// void runLEDSequence() {
//   for (int i = 0; i < NUM_LEDS; i++) {
//     // Fade in
//     for (int brightness = 0; brightness <= 50; brightness++) {
//       leds[i] = CRGB(brightness, brightness, brightness);
//       FastLED.show();
//       delay(10);  // Delay for smooth fading
//     }

//     // Fade out
//     for (int brightness = 50; brightness >= 0; brightness--) {
//       leds[i] = CRGB(brightness, brightness, brightness);
//       FastLED.show();
//       delay(10);  // Delay for smooth fading
//     }
//   }
// }

// void applyColor(String hexColor) {
//   int r, g, b;
//   if (parseColor(hexColor, r, g, b)) {
//     r = pgm_read_byte(&gamma8[r]);
//     g = pgm_read_byte(&gamma8[g]);
//     b = pgm_read_byte(&gamma8[b]);

//     for (int i = 0; i < NUM_LEDS; i++) {
//       leds[i] = CRGB(r, g, b);
//     }
//     FastLED.show();
//   }
// }

// bool parseColor(String hexColor, int &r, int &g, int &b) {
//   hexColor.trim();
//   if (hexColor.length() == 7 && hexColor[0] == '#') {
//     r = strtol(hexColor.substring(1, 3).c_str(), NULL, 16);
//     g = strtol(hexColor.substring(3, 5).c_str(), NULL, 16);
//     b = strtol(hexColor.substring(5, 7).c_str(), NULL, 16);
//     return true;
//   }
//   return false;
// }
