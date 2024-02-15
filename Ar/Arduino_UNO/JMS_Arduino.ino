#include "DHT.h"

#define GROUND1 A2    //토양센서1
#define GROUND2 A3    //토양센서2
#define DHTPIN  4     //온습도센서
#define LED     9     //LED
#define W_PUMP  10    //펌프
#define SYS_FAN 11    //sys팬

#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
  pinMode(SYS_FAN, OUTPUT);
  pinMode(W_PUMP, OUTPUT);
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);

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


  SendDataToRaspberryPi(IsRun, SYSFAN, WPUMP, Humidity, Temperature, 1024 - Ground1, 1024 - Ground2);
  //라즈베리파이에 데이터 보내기
  
  delay(1000);
}

void SendDataToRaspberryPi(bool IsRun, bool SYSFAN, bool WPUMP, float humidity, float temperature, int ground1, int ground2)
{
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