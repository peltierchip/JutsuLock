/*----Ardunio to Shield Pinout Controls-----

Are using a Seeed motor shield to drive 2 DC motors

Seeed motor shield uses Arduino pins 8->13
Pin 9 sets the enable and speed of shield outputs 1 & 2
Pin 10 sets the enable and speed of shield outputs 3 & 4
Pin 8 from Uno controls the state of shield output 1
Pin 11 from Uno controls the state of shield output 2

*/

#include <SoftwareSerial.h>
SoftwareSerial BTserial(3, 2); // RX, TX

int locked = 0;
int leftmotorForward = 8; 
int leftmotorBackward = 11;
int leftmotorspeed = 9;

//--- Speeds and Timers

int Runtime = 5000; // How long motor actions will last
int Fast = 255; // fast speed (of 255 max)

//------------------------------------------------------

void setup() //---6 Pins being used are outputs--- 
{

  pinMode(leftmotorForward, OUTPUT);
  pinMode(leftmotorBackward, OUTPUT);
  pinMode(leftmotorspeed, OUTPUT);

  Serial.begin(9600);
  BTserial.begin(9600);

}

// ---Main Program Loop -----------------------------

void loop()
{
  // Serial monitor prints data recieved via bluetooth
  if (BTserial.available()){
    char c = BTserial.read();
    if (c == 1 && !locked){
      //lock door
      lockDoor();
      locked = 1;
      Serial.println("door locked"); 
      
      while (BTserial.available()) BTserial.read(); //clear buffer  
    }
    
    else if (c == 2 && locked){
      // unlock door
      unlockDoor();
      locked = 0;
      Serial.println("door unlocked");
      
      while (BTserial.available()) BTserial.read(); //clear buffer
    }
    else Serial.println(locked);
  }
}

//----- "Sub-rutine" Voids called by the main loop

void unlockDoor()
{
  analogWrite(leftmotorspeed,Fast); //Enable left motor by setting speed
  digitalWrite(leftmotorBackward,LOW); // Drives LOW outputs down first to avoid damage
  digitalWrite(leftmotorForward,HIGH);
  
  delay(Runtime);
  digitalWrite(leftmotorspeed,LOW);  //Stop
}

void lockDoor()
{
  analogWrite(leftmotorspeed,Fast); //Enable left motor by setting speed
  digitalWrite(leftmotorForward,LOW); // Drives LOW outputs down first to avoid damage
  digitalWrite(leftmotorBackward,HIGH);
  
  delay(Runtime);
  digitalWrite(leftmotorspeed,LOW); //Stop
}

