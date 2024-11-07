#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>


class DisplayHandler{
  public:

    DisplayHandler(int a){};

    void write(Adafruit_SSD1306 display, const char *message, int x_start = 0, int y_start = 0, float size = 2.5){
      display.clearDisplay();
      display.setTextSize(size);             // Normal 1:1 pixel scale
      display.setCursor(x_start, y_start);             // Start at top-left corner
      display.setTextColor(SSD1306_WHITE);        // Draw white text

      int16_t x1, y1;
      uint16_t w, h;

      display.getTextBounds(message, x_start, y_start, &x1, &y1, &w, &h); //calc width of new string
      display.setCursor((128 - w) /2, (64-h)/2);

      display.print(message);;
      display.display();
    }

  private:

      void centerText(const char *buf, int x, int y, Adafruit_SSD1306 display)
      {
          int16_t x1, y1;
          uint16_t w, h;
          
          display.getTextBounds(buf, x, y, &x1, &y1, &w, &h); //calc width of new string
          display.setCursor((128 - w) /2, (64-h)/2);
      }
};

