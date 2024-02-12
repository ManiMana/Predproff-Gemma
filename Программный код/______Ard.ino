#include <Arduino.h>

// Определения для A4988
const int stepPinA[2] = {22, 28}; // STEP пины
const int dirPinA[2] = {23, 29}; // DIR пины
const float stepsPerMM_X = 5.6; // Количество шагов на мм для оси X
const float stepsPerMM_Y = 5.6;  // Количество шагов на мм для оси Y
float currentPositionX = 0.0;
float currentPositionY = 0.0;

// Определения для ULN2003
const int motorPinsULN2003[][4] = {
  {2, 3, 4, 5},
  {6, 7, 8, 9},
  {10, 11, 12, 13}
  
};

// Пины концевиков
const int endStopX = 40; // Концевик оси X
const int endStopY = 41; // Концевик оси Y

void initSteppers() {
  for (int i = 0; i < 2; i++) {
    pinMode(stepPinA[i], OUTPUT);
    pinMode(dirPinA[i], OUTPUT);
  }
  pinMode(endStopX, INPUT_PULLUP);
  pinMode(endStopY, INPUT_PULLUP);
}

void initULN2003Motors() {
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 4; j++) {
      pinMode(motorPinsULN2003[i][j], OUTPUT);
    }
  }
}

void setSpeed(float speedMMPerSec, float &stepDelayMicroseconds, float stepsPerMM) {
  float stepsPerSec = speedMMPerSec * stepsPerMM;
  stepDelayMicroseconds = 1e6 / stepsPerSec / 2;
}

void moveHBot(float xMM, float yMM, float speedMMPerSec) {
  float deltaX = xMM - currentPositionX;
  float deltaY = yMM - currentPositionY;
  float stepDelayMicroseconds;
  setSpeed(speedMMPerSec, stepDelayMicroseconds, (stepsPerMM_X + stepsPerMM_Y) / 2);
  
  int stepsX = round(deltaX * stepsPerMM_X);
  int stepsY = round(deltaY * stepsPerMM_Y);
  int motorSteps[2] = {stepsX + stepsY, stepsX - stepsY};
  bool dir[2] = {motorSteps[0] >= 0, motorSteps[1] >= 0};
  
  digitalWrite(dirPinA[0], dir[0]);
  digitalWrite(dirPinA[1], dir[1]);
  
  for (int i = 0; i < max(abs(motorSteps[0]), abs(motorSteps[1])); i++) {
    if (i < abs(motorSteps[0])) {
      digitalWrite(stepPinA[0], HIGH);
      delayMicroseconds(stepDelayMicroseconds);
      digitalWrite(stepPinA[0], LOW);
      delayMicroseconds(stepDelayMicroseconds);
    }
    if (i < abs(motorSteps[1])) {
      digitalWrite(stepPinA[1], HIGH);
      delayMicroseconds(stepDelayMicroseconds);
      digitalWrite(stepPinA[1], LOW);
      delayMicroseconds(stepDelayMicroseconds);
    }
  }
  
  currentPositionX += deltaX;
  currentPositionY += deltaY;
}

void setup() {
  Serial.begin(9600);
  initSteppers();
  initULN2003Motors();
}

void loop() {
//  moveHBot(100, 100, 5); // Пример использования: перемещение к точке (100, 100) со скоростью 5 мм/с
  //delay(5000); // Пауза перед следующим действием
  moveHBot(10, 10, 1); // Возвращение в начальную точку (0, 0)
  delay(5000); // Пауза перед следующим действием
}
