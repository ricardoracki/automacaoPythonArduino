#define led_red 13
#define led_yellow 12
#define led_green 11

String serial_command = "";
int buffer_sensor = 0;


void setup() {
  pinMode(led_red, OUTPUT);
  pinMode(led_yellow, OUTPUT);
  pinMode(led_green, OUTPUT);


  Serial.begin(9600);
}

void loop() {
  while (Serial.available() > 0) {
    serial_command = serial_command + char(Serial.read());
    delay(10);
  }

  if (analogRead(A0) > buffer_sensor + 10 || analogRead(A0) < buffer_sensor - 10){
      buffer_sensor = analogRead(A0);
      Serial.println(buffer_sensor);

      delay(100);
  }


  int indexOfSeparator = serial_command.indexOf(":");
  // Template_Command = address:value
  if (indexOfSeparator > 0) {
    serial_command.trim();
    String target = serial_command.substring(0, indexOfSeparator);
    bool value = serial_command.substring(indexOfSeparator + 1).equals("true");

    serial_command = "";

    if (target == "led_red") digitalWrite(led_red, value);
    else if (target == "led_yellow") digitalWrite(led_yellow, value);
    else if (target == "led_green") digitalWrite(led_green, value);

  }

}
