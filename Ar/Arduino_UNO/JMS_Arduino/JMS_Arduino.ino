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
  bool  D_SYSFAN;                             //시스탬펜 on/off
  bool  D_WPUMP;                              //워터펌프 on/off
  bool  D_LED;                                //LED on/off
  float Humidity    = dht.readHumidity();     //습도 %
  float Temperature = dht.readTemperature();  //온도 소숫점 2번째 자리까지
  int   Ground1     = analogRead(A2);         //토양1 수분
  int   Ground2     = analogRead(A3);         //토양2 수분

  int LED_Control, SYSFAN_Control;

  if (Serial.available() > 0) {
    // 시리얼로부터 수신된 데이터를 저장하는 문자열
    String receivedData = Serial.readStringUntil('\n'); // 줄바꿈 문자까지 읽기
    // 콤마(',') 위치 찾기
    int commaIndex = receivedData.indexOf(',');
    // 첫 번째 데이터 추출
    String FirstData = receivedData.substring(0, commaIndex);
    // 두 번째 데이터 추출
    String SecondData = receivedData.substring(commaIndex + 1);

    // 추출한 데이터를 int형으로 변환
    LED_Control = FirstData.toInt();
    SYSFAN_Control = SecondData.toInt();
  }
  if(LED_Control == 0)
  {
    D_LED = 0;
    digitalWrite(LED, LOW);
  }
  else{
    D_LED = 1;
    digitalWrite(LED, HIGH);
  }

  if(SYSFAN_Control == 1){
    D_SYSFAN = 1;
    digitalWrite(SYS_FAN, HIGH);
  }
  else if(SYSFAN_Control == 0){
    D_SYSFAN = 0;
    digitalWrite(SYS_FAN, LOW);
  }
  else{
    //SYSFAN 자동으로 작동
    if(Humidity >= 50 || Temperature>= 35)
      {digitalWrite(SYS_FAN, HIGH); D_SYSFAN = true;}
    else
      {digitalWrite(SYS_FAN, LOW);  D_SYSFAN = false;}
  }

  if(Ground1 >= 380 || Ground2 >= 380)      //WPUMP 작동여부
    {digitalWrite(W_PUMP, HIGH);  D_WPUMP = true;}
  else
    {digitalWrite(W_PUMP, LOW);   D_WPUMP = false;}
  Serial.readStringUntil('\n');
  
  SendDataToOLEDDisplay(Humidity, Temperature);
  //OLED에 데이터 보내기

  SendDataToRaspberryPi(IsRun, D_SYSFAN, D_WPUMP, D_LED, Humidity, Temperature, 1024 - Ground1, 1024 - Ground2);
  //라즈베리파이에 데이터 보내기

  delay(1000);
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
