#include "DHT.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

#define GROUND1 A2    //토양센서1
#define GROUND2 A3    //토양센서2
#define DHTPIN  4     //온습도센서
#define LED     8     //LED
#define W_PUMP  12    //펌프
#define SYS_FAN 13    //sys팬

#define DHTTYPE DHT21

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
  pinMode(SYS_FAN, OUTPUT);
  pinMode(W_PUMP, OUTPUT);
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3C for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);} // Don't proceed, loop forever}-
    // Clear the buffer
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(WHITE);
}

void loop() {
  bool  IsRun = true;                         //작동여부
  //온오프 기능 추가해야함, 임시로 작동으로만 저장되게 설정
  bool  SYSFAN;                               //시스탬펜 on/off
  bool  WPUMP;                                //워터펌프 on/off
  float Humidity    = dht.readHumidity();     //습도 %
  float Temperature = dht.readTemperature();  //온도 소숫점 2번째 자리까지
  int   Ground1     = analogRead(A2);         //토양1 수분
  int   Ground2     = analogRead(A3);         //토양2 수분

  if(Humidity >= 50 || Temperature>= 35)      //SYS팬 동작여부
    {digitalWrite(SYS_FAN, HIGH); SYSFAN = true;}
  else
    {digitalWrite(SYS_FAN, LOW);  SYSFAN = false;}


  if(Ground1 >= 380 || Ground2 >= 380)      //WPUMP 작동여부
    {digitalWrite(W_PUMP, HIGH);  WPUMP = true;}
  else
    {digitalWrite(W_PUMP, LOW);   WPUMP = false;}
  Serial.readStringUntil('\n');
  
  SendDataToOLEDDisplay(IsRun, SYSFAN, WPUMP, Humidity, Temperature, 1024 - Ground1, 1024 - Ground2);
  //OLED에 데이터 보내기

  SendDataToRaspberryPi(IsRun, SYSFAN, WPUMP, Humidity, Temperature, 1024 - Ground1, 1024 - Ground2); 
  //라즈베리파이에 데이터 보내기
  delay(1000);
}

void SendDataToRaspberryPi(bool IsRun, bool SYSFAN, bool WPUMP, float humidity, float temperature, int ground1, int ground2){
  Serial.print("IsRun : ");
  Serial.println(IsRun);

  Serial.print("SYSFAN : ");
  Serial.println(SYSFAN);

  Serial.print("WPUMP : ");
  Serial.println(WPUMP);

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

void SendDataToOLEDDisplay(bool IsRun, bool SYSFAN, bool WPUMP, float humidity, float temperature, int ground1, int ground2) {
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
