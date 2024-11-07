#include <Arduino.h>

class Prueba {
  public:
    Prueba(int pinAvance, int pinRetro){
      _pinAvance = pinAvance;
      _pinRetro = pinRetro;
    };
    void setOUTPUT(){
      pinMode(_pinAvance, OUTPUT);
      pinMode(_pinRetro, OUTPUT);
    };

    void setFrontSpeed(int velocidad){
      digitalWrite(_pinAvance, velocidad);
    };

    void setBackSpeed(int velocidad){
      digitalWrite(_pinRetro, velocidad);
    };

  private:
    int _pinAvance;
    int _pinRetro;
};