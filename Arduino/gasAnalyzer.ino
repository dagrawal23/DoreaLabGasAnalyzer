// Feather9x_TX
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messaging client (transmitter)
// with the RH_RF95 class. RH_RF95 class does not provide for addressing or
// reliability, so you should only use RH_RF95 if you do not need the higher
// level messaging abilities.
// It is designed to work with the other example Feather9x_RX

#include <SPI.h>
#include <RH_RF95.h>
#define EOC 9
#define CS 6
#define CNVST 5
#define SETUP_EXTREF_00 0x44 //external reference and clock mode 00
#define CONVERSION_00 0xD8 //scan channel 0 to 11 , scan mode 00
#define AVERAGING_16 0X38 //average 16 samples for each conversion
// First 3 here are boards w/radio BUILT-IN. Boards using FeatherWing follow.
#if defined (__AVR_ATmega32U4__)  // Feather 32u4 w/Radio
  #define RFM95_CS    8
  #define RFM95_INT   7
  #define RFM95_RST   4

#elif defined(ADAFRUIT_FEATHER_M0) || defined(ADAFRUIT_FEATHER_M0_EXPRESS) || defined(ARDUINO_SAMD_FEATHER_M0)  // Feather M0 w/Radio
  #define RFM95_CS    8
  #define RFM95_INT   3
  #define RFM95_RST   4

#elif defined(ARDUINO_ADAFRUIT_FEATHER_RP2040_RFM)  // Feather RP2040 w/Radio
  #define RFM95_CS   16
  #define RFM95_INT  21
  #define RFM95_RST  17

#elif defined (__AVR_ATmega328P__)  // Feather 328P w/wing
  #define RFM95_CS    4  //
  #define RFM95_INT   3  //
  #define RFM95_RST   2  // "A"

#elif defined(ESP8266)  // ESP8266 feather w/wing
  #define RFM95_CS    2  // "E"
  #define RFM95_INT  15  // "B"
  #define RFM95_RST  16  // "D"

#elif defined(ARDUINO_ADAFRUIT_FEATHER_ESP32S2) || defined(ARDUINO_NRF52840_FEATHER) || defined(ARDUINO_NRF52840_FEATHER_SENSE)
  #define RFM95_CS   10  // "B"
  #define RFM95_INT   9  // "A"
  #define RFM95_RST  11  // "C"

#elif defined(ESP32)  // ESP32 feather w/wing
  #define RFM95_CS   33  // "B"
  #define RFM95_INT  27  // "A"
  #define RFM95_RST  13

#elif defined(ARDUINO_NRF52832_FEATHER)  // nRF52832 feather w/wing
  #define RFM95_CS   11  // "B"
  #define RFM95_INT  31  // "C"
  #define RFM95_RST   7  // "A"

#endif

/* Some other possible setups include:

// Feather 32u4:
#define RFM95_CS   8
#define RFM95_RST  4
#define RFM95_INT  7

// Feather M0:
#define RFM95_CS   8
#define RFM95_RST  4
#define RFM95_INT  3

// Arduino shield:
#define RFM95_CS  10
#define RFM95_RST  9
#define RFM95_INT  7

// Feather 32u4 w/wing:
#define RFM95_RST 11  // "A"
#define RFM95_CS  10  // "B"
#define RFM95_INT  2  // "SDA" (only SDA/SCL/RX/TX have IRQ!)

// Feather m0 w/wing:
#define RFM95_RST 11  // "A"
#define RFM95_CS  10  // "B"
#define RFM95_INT  6  // "D"
*/

/*
Initializes the adc by  writing to the registers
*/
volatile bool newVals = false;
void adc_init(int setup, int conversion, int averaging){
  pinMode(8, OUTPUT);
  pinMode(EOC, INPUT);
  pinMode(CS, OUTPUT);
  pinMode(CNVST, OUTPUT);
  digitalWrite(8, HIGH);
  digitalWrite(CS, HIGH);
  digitalWrite(CNVST, HIGH);
  delay(1);
  SPI.begin();
  SPI.beginTransaction(SPISettings(500000, MSBFIRST, SPI_MODE0));
  digitalWrite(CS, LOW);
  delayMicroseconds(10);
  SPI.transfer(0x18);
  delay(10);
  SPI.transfer(setup);
    delay(10);
  SPI.transfer(conversion);
    delay(10);
  SPI.transfer(averaging);
  delay(1);
  digitalWrite(CS, HIGH);
  digitalWrite(CNVST, HIGH);
}
/*
read analoag inputs
*/
void read_analog(uint16_t* values){
 
  digitalWrite(8, HIGH);
  digitalWrite(CNVST, LOW);
  delayMicroseconds(2000);
  digitalWrite(CNVST, HIGH);
  delay(1);
  //Serial.println(digitalRead(EOC));
  //while(digitalRead(EOC) == HIGH);
  //Serial.println(digitalRead(EOC));
  delay(1);
  while(newVals == false);
  newVals = false;
  digitalWrite(CS, LOW);
  delay(1);
  for(int i = 2; i < 14; i++){
  int upperByte = SPI.transfer(0x00);
  int lowerByte = SPI.transfer(0x00);
  uint16_t val = (upperByte << 8) | (lowerByte & 0xFF);
  values[i] = val;
  
  }
  digitalWrite(CS, HIGH);
  delay(50);
}
// Change to 434.0 or other frequency, must match RX's freq!
#define RF95_FREQ 915.0

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

void setup() {
  pinMode(10,INPUT);
  pinMode(13,OUTPUT);
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);
  digitalWrite(13, HIGH);
  Serial.begin(115200);
  //while (!Serial) delay(1);
  delay(10);

  Serial.println("Feather LoRa TX Test!");

  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  while (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    Serial.println("Uncomment '#define SERIAL_DEBUG' in RH_RF95.cpp for detailed debug info");
    while (1);
  }
  Serial.println("LoRa radio init OK!");

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("setFrequency failed");
    while (1);
  }
  rf95.setPreambleLength(8);
  rf95.setSpreadingFactor(7);
  rf95.setSignalBandwidth(500000);
  Serial.print("Set Freq to: "); Serial.println(RF95_FREQ);

  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then
  // you can set transmitter powers from 5 to 23 dBm:
  rf95.setTxPower(23, false);
  adc_init(SETUP_EXTREF_00, CONVERSION_00, AVERAGING_16);
  attachInterrupt(digitalPinToInterrupt(EOC), blink, FALLING);
}

int16_t packetnum = 0;  // packet counter, we increment per xmission

void loop() {
  bool myTurn = false;
  //wait for turn
  while(!myTurn){
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);
     if (rf95.recv(buf, &len)) {
      Serial.println(buf[0]);
      if(buf[0] == 1)
        myTurn = true;
     }
  }
  //read data from ADC
  int ack = 0;
  uint16_t radiopacket[14] = {0,0,0,0,0,0,0,0,0,0,0,0};
  radiopacket[0] = 9876;
  read_analog(radiopacket);
  radiopacket[1] = (digitalRead(10) == 0)?1:0;
  //repeat send until ack recieved
  while(ack == 0)
  {
  delay(100); // Wait 1 second between transmits, could also 'sleep' here!
  Serial.println("Transmitting..."); // Send a message to rf95_server
 //void*values = malloc(sizeof(uint8_t) * 12);

  

 ///for(int i=0;i<12;i++){
 //  *(values + i) = radiopacket[i];
 //} 
  Serial.print("Sending "); 
  for(int i = 1; i <14; i++){
    Serial.print(radiopacket[i]);
    Serial.print(" ");

    
  }
  Serial.println("");
  

  Serial.println("Sending...");
  delay(10);
  rf95.send((uint8_t *)radiopacket, 28);

  Serial.println("Waiting for packet to complete...");
  delay(20);
  rf95.waitPacketSent();
  // Now wait for a reply
  uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
  uint8_t len = sizeof(buf);

  Serial.println("Waiting for reply...");
  if (rf95.waitAvailableTimeout(1000)) {
    // Should be a reply message for us now
    if (rf95.recv(buf, &len)) {
      Serial.print("Got reply: ");
      Serial.println(buf[0]);
      Serial.print("RSSI: ");
      Serial.println(rf95.lastRssi(), DEC);
      ack = buf[0];
      
    } else {
      Serial.println("Receive failed");
    }
  } else {
    Serial.println("No reply, is there a listener around?");
  }
  
  }
  
  Serial.println("Recieve Okay");
  
}
void blink() {
 
  newVals = true;
}