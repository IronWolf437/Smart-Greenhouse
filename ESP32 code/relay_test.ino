int buttonPin = 19; // Pin connected to the button
int ledPin = 13;  // Pin connected to the LED

void setup() {
    pinMode(buttonPin, INPUT_PULLUP); // Set button pin as input with pull-up resistor
    pinMode(ledPin, OUTPUT);   // Set LED pin as output
}

void loop() {
    int buttonState = digitalRead(buttonPin); // Read the state of the button

    if (buttonState == LOW) { // If the button is pressed
        digitalWrite(ledPin, HIGH); // Turn on the LED
    } else {
        digitalWrite(ledPin, LOW); // Turn off the LED
    }
}