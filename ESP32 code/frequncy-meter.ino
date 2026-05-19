#define INPUT_PIN 18

volatile uint32_t pulse_count = 0;
uint32_t last_pulse_count = 0;
unsigned long last_time = 0;

void IRAM_ATTR handleInterrupt() {
  pulse_count++;
}

void setup() {
  Serial.begin(115200);
  pinMode(INPUT_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(INPUT_PIN), handleInterrupt, RISING);
}

void loop() {
  unsigned long current_time = millis();
  
  if (current_time - last_time >= 1000) {
    // بناخد نسخة من العداد ونطرح القديم عشان نعرف اللي جالنا في ثانية
    uint32_t current_pulses = pulse_count; 
    uint32_t pulses_in_interval = current_pulses - last_pulse_count;
    
    float frequency_khz = pulses_in_interval / 1000.0;
    
    Serial.print("Freq: ");
    Serial.print(frequency_khz);
    Serial.println(" kHz");
    
    last_pulse_count = current_pulses;
    last_time = current_time;
  }
}