#include "DHT.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <avr/wdt.h> // Watchdog 타이머를 위한 라이브러리 추가

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

#define GROUND1 A2
#define GROUND2 A3
#define DHTPIN  4
#define LED     8
#define W_PUMP  12
#define SYS_FAN 13

#define DHTTYPE DHT21

DHT dht(DHTPIN, DHTTYPE);
unsigned long previousMillis = 0;
const long interval = 1000;

void setup() {
  wdt_disable(); // 초기 설정 동안에는 Watchdog를 비활성화
  Serial.begin(9600);
  dht.begin();
  pinMode(SYS_FAN, OUTPUT);
  pinMode(W_PUMP, OUTPUT);
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);} // Don't proceed, loop forever
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(WHITE);

  wdt_enable(WDTO_8S); // Watchdog 타이머를 8초로 설정
}

void loop() {

  wdt_reset(); // Loop의 시작에서 Watchdog 타이머를 리셋
  bool  IsRun = true;
  bool  D_SYSFAN;
  bool  D_WPUMP;
  bool  D_LED = true;
  float Humidity    = dht.readHumidity();
  float Temperature = dht.readTemperature();
  int   Ground1     = analogRead(A2);
  int   Ground2     = analogRead(A3);
  unsigned long currentMillis = millis();

  if(Humidity >= 30.0 || Temperature>= 35.0) {
    digitalWrite(SYS_FAN, HIGH); D_SYSFAN = true;}
  else {
    digitalWrite(SYS_FAN, LOW);  D_SYSFAN = false;}

  if(Ground1 >= 380 || Ground2 >= 380) {
    digitalWrite(W_PUMP, HIGH);  D_WPUMP = true;}
  else {
    digitalWrite(W_PUMP, LOW);   D_WPUMP = false;}
  
  SendDataToOLEDDisplay(Humidity, Temperature);
  if (currentMillis - previousMillis >= interval) {
    SendDataToRaspberryPi(IsRun, D_SYSFAN, D_WPUMP, D_LED, Humidity, Temperature, 1024 - Ground1, 1024 - Ground2);
    previousMillis = currentMillis;
  }
}

void SendDataToRaspberryPi(bool IsRun, bool D_SYSFAN, bool D_WPUMP, bool D_LED, float humidity, float temperature, int ground1, int ground2){
  Serial.print("IsRun : ");
  Serial.println(IsRun);

  Serial.print("SYSFAN : ");
  Serial.println(D_SYSFAN);

  Serial.print("WPUMP : ");
  Serial.println(D_WPUMP);

  Serial.print("LED : ");
  Serial.println(D_LED);

  Serial.print("Humidity : ");
  Serial.print(humidity);
  Serial.println(" %");

  Serial.print("Temperature : ");
  Serial.print(temperature);
  Serial.println(" *C");

  Serial.print("Ground1 : ");
  Serial.println(ground1);

  Serial.print("Ground2 : ");
  Serial.println(ground2);
  Serial.println();
}

void SendDataToOLEDDisplay(float humidity, float temperature) {
  char buffer[50];
  char temp[20];

  //습도 OLED에 출력
  display.clearDisplay();
  memset(buffer, 0, sizeof(buffer));  // buffer 초기화
  dtostrf(humidity, 3, 1, temp);
  sprintf(buffer, "Hu: %s %%", temp);
  display.setCursor(0,10);
  display.println(buffer);
  
  //온도 OLED에 출력
  memset(buffer, 0, sizeof(buffer));  // buffer 초기화
  dtostrf(temperature, 3, 1, temp);
  sprintf(buffer, "Te: %s C", temp);  
  display.setCursor(0,30);
  display.println(buffer);
  
  // Show the display buffer on the screen. You MUST call display.display() after
  // writing to the display buffer.
  display.display();
  // Clear the buffer
  display.clearDisplay();
}