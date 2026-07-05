#include <ArduinoJson.h>
#include <DHT.h>
#include <Preferences.h>
//#include <WiFi.h>

Preferences preferences;

//const char* ssid = "Etisalat-4Y9S";
//const char* password = "A2KUKe6k";

// --- القنوات والأسلاك (نفس ترتيبك) ---
const int soil_sensors[] = {34, 39, 36}; //A --->SN:39 & SP:36
const int valves[] = {26, 25, 33}; //D
const int pump_pin = 27; //D
const int fans[] = {12, 13}; //D
const int heater = 14; //D
const int temp_sensor_pin = 19; //D
const int motion_sensor = 23; //D
const int ultasonic_circuit_pin = 22; //D
const int LDR_sensor_pin = 32; //A
const int light_pin = 21; //D
//const int camera_light_pin = 16; //D

// --- المتغيرات العامة (عشان الـ JSON يشوفها) ---
int sensorValues[3];
float current_temp = 0.0;
bool valves_state[3] = {false, false, false};
bool fans_state = false;
bool heater_state = false;
bool motion_state = false;
bool pump_state = false;
float current_LDR = 0.0;
float currentPercentage = 0.0;
bool light_state = false;

// time read dht
unsigned long currnt_dht_time = 0;
const long time_read_dht = 2000;

// توقيت الإرسال (كل 5 دقايق = 300,000 ملي ثانية)
unsigned long lastLogTime = 0;
const long interval = 5000; 

// ultasonic circuit run time
unsigned long motionStartTime = 0;
const unsigned long duration = 5000;

unsigned long totalEffectiveMillis = 0; 
unsigned long targetMillis = 0; 
unsigned long lastUpdateMillis = 0;      
unsigned long dayResetMillis = 0;

int currentGroup = 1;
int currentSoilGroup[3] = {0, 0, 0};

const unsigned long ONE_DAY_MILLIS = 86400000; // 24 ساعة بالمللي ثانية


DHT dht(temp_sensor_pin, DHT22);


void setup() {
  Serial.begin(9600); // ده اللي هيروح للـ Raspberry Pi عبر الكابل

  // --- EEPROM "greenhouse" ---
  preferences.begin("greenhouse", false);           // "greenhouse" هو اسم المساحة في الذاكرة، false يعني قراءة وكتابة
  currentGroup = preferences.getInt("group", 1);    // اقرأ الجروب، ولو الذاكرة فاضية (أول مرة تشغل الكود) خليه 1

  // --- wifi ---
  /*
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED){
    delay(50);
    Serial.println(".");
  }
  Serial.println("");
  Serial.println("WiFi connected!");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  */
  dht.begin();
  
  for(int i=0 ; i<3; i++) pinMode(valves[i], OUTPUT);
  for(int i=0; i<2; i++) pinMode(fans[i], OUTPUT);
  pinMode(pump_pin, OUTPUT);
  pinMode(heater, OUTPUT);
  pinMode(motion_sensor, INPUT);
  pinMode(ultasonic_circuit_pin, OUTPUT);
  pinMode(light_pin, OUTPUT);
  //pinMode(camera_light_pin, OUTPUT);

  lastUpdateMillis = millis();
  dayResetMillis = millis();
}




void loop() {
  unsigned long currentMillis = millis();


  // restart counter in new day:
  unsigned long deltaTime = currentMillis - lastUpdateMillis;
  lastUpdateMillis = currentMillis;

  if (currentMillis - dayResetMillis >= ONE_DAY_MILLIS) {
    resetDay();
  }


  // take data:
  processSerialData();


  // temp:
  if (currentMillis - currnt_dht_time >= time_read_dht) {
    currnt_dht_time = currentMillis;

    current_temp = dht.readTemperature();
    temp_control(current_temp, currentGroup);
  }

  /* current_temp = dht.readTemperature();
  temp_control(current_temp, currentGroup); */


  // soil:
  for(int i=0; i<3; i++){
    sensorValues[i] = analogRead(soil_sensors[i]);
    float percentage = (sensorValues[i] / 4095.0) * 100.0;
    soil_control(i, currentSoilGroup[i], percentage); 
  }

  bool any_valve_open = false;
  for(int i=0; i<3; i++) {
    if(valves_state[i]) any_valve_open = true;
  }

  if (any_valve_open) {
    digitalWrite(pump_pin, LOW);
    pump_state = true;
  } else {
    digitalWrite(pump_pin, HIGH);
    pump_state = false;
  }


  // motion:
  motion_control();


  // LDR:
  current_LDR = analogRead(LDR_sensor_pin);
  currentPercentage = (current_LDR / 4095.0) * 100.0;
  LDR_control(currentGroup, currentPercentage, deltaTime);


  // 2. إرسال الداتا للـ Pi (كل 5 دقائق)
  if (millis() - lastLogTime >= interval) {
    sendJsonToPi();
    lastLogTime = millis();
  }
}




// --- soil sensor ---
void soil_control(int index, int group, float current_perc) {
  float min_dry, max_dry, min_wet, max_wet;

  // تحديد الـ 4 نطاقات بناءً على نوع التربة
  switch (group) {
    case 1:
      max_dry = 85.0; min_dry = 60.0;
      max_wet = 35.0; min_wet = 20.0;
      break;
    case 2:
      max_dry = 70.0; min_dry = 50.0;
      max_wet = 25.0; min_wet = 10.0;
      break;
    case 3: // نوع تربة 3
      max_dry = 75.0; min_dry = 55.0;
      max_wet = 30.0; min_wet = 15.0;
      break;
    default:
      max_dry = 80.0; min_dry = 60.0;
      max_wet = 30.0; min_wet = 20.0;
      break;
  }

  if(current_perc >= min_dry && current_perc <= max_dry) {
    digitalWrite(valves[index], LOW);
    valves_state[index] = true;
  }
  else if (current_perc >= min_wet && current_perc <= max_wet) {
    digitalWrite(valves[index], HIGH);
    valves_state[index] = false;
  }
}




// --- temp sensor---
void temp_control(float val, int group) {
  if (isnan(val)) {
    digitalWrite(heater, HIGH);
    digitalWrite(fans[0], HIGH);
    digitalWrite(fans[1], HIGH);
    fans_state = false;
    heater_state = false;
    return; // اخرج من الدالة هنا خلاص
  }

  float min_temp, max_temp;

  // تحديد النطاق بناءً على الجدول
  switch (group) {
    case 1:
      min_temp = 24.0;
      max_temp = 28.0;
      break;
    case 2:
      min_temp = 18.0;
      max_temp = 24.0;
      break;
    case 3:
      min_temp = 26.0;
      max_temp = 30.0;
      break;
    default: // حالة احتياطية لو الرقم غلط
      min_temp = 24.0; 
      max_temp = 28.0;
      break;
  }

  // منطق التحكم
  if (val > max_temp) {
    // حرارة عالية: نشغل المروح ونقفل السخان
    digitalWrite(heater, HIGH);
    digitalWrite(fans[0], LOW);
    digitalWrite(fans[1], LOW);
    fans_state = true;
    heater_state = false;
  }
  else if (val < min_temp) {
    // حرارة منخفضة: نشغل السخان ونقفل المروح
    digitalWrite(heater, LOW);
    digitalWrite(fans[0], HIGH);
    digitalWrite(fans[1], HIGH);
    fans_state = false;
    heater_state = true;
  }
  else {
    // الحرارة مثالية (داخل النطاق): نقفل كل حاجة
    digitalWrite(heater, HIGH);
    digitalWrite(fans[0], HIGH);
    digitalWrite(fans[1], HIGH);
    fans_state = false;
    heater_state = false;
  }
}




// --- motion sensor ---
void motion_control(){
  if(digitalRead(motion_sensor) == HIGH){
    digitalWrite(ultasonic_circuit_pin, LOW);
    motion_state = true;
    motionStartTime = millis();
  }
  
  if (motion_state) {
    unsigned long currentMillis = millis();
    
    if (currentMillis - motionStartTime >= duration) {
      digitalWrite(ultasonic_circuit_pin, HIGH);
      motion_state = false;
    }
  }
}




// --- LDR sensor ---
void LDR_control(int group, float currentPct, unsigned long delta) {
  // لو البايثون باعت أمر تشغيل إجباري، اخرج من الدالة وسيب البن زي ما هو
  if (light_state == true) { 
    return; 
  }

  if (group == 1 || group == 3) {
    targetMillis = 30000; 
  } else if (group == 2) {
    targetMillis = 60000; 
  }

  if (totalEffectiveMillis < targetMillis) {    
    if (currentPct < 63.0) {
      digitalWrite(light_pin, LOW); 
      // light_state = true; <-- شيلنا دي عشان متعملش بلوك دائم، الـ LDR بيتحكم في البن بس
    }
    else if (currentPct > 68.0) {
      digitalWrite(light_pin, HIGH);  
      // light_state = false;
    }
    totalEffectiveMillis += delta;
  } 
  else {
    digitalWrite(light_pin, HIGH);
  }
}



// --- reset day ---
void resetDay() {
    totalEffectiveMillis = 0;
    dayResetMillis = millis();
    Serial.println("--- New Cycle / Day Started! ---");
}



// --- process data ---
void processSerialData() {
  if (Serial.available() > 0) {
    String incomingData = Serial.readStringUntil('\n');
    incomingData.trim();

    if (incomingData.equalsIgnoreCase("r") || incomingData.equalsIgnoreCase("R")) {
      resetDay();
    } else {
      DynamicJsonDocument doc(1024);
      DeserializationError error = deserializeJson(doc, incomingData);

      if (!error) {
        String groupStr = doc["farming"]["group"];
        String lightState = doc["light"];

        if (groupStr == "group1") {
          currentGroup = 1;
          preferences.putInt("group", 1);
        } else if (groupStr == "group2") {
          currentGroup = 2;
          preferences.putInt("group", 2);
        } else if (groupStr == "group3") {
          currentGroup = 3;
          preferences.putInt("group", 3);
        }

        JsonObject pots = doc["farming"]["pots"];
        int index = 0;
        
        for (JsonPair kv : pots) {
          String soilType = kv.value().as<String>();
          
          if (soilType == "soil1") {
            currentSoilGroup[index] = 1;
          } else if (soilType == "soil2") {
            currentSoilGroup[index] = 2;
          } // يمكنك إضافة المزيد من الأنواع هنا إذا لزم الأمر
          
          index++;
          if (index >= 3) break; // لتفادي تجاوز حدود المصفوفة
        }
        
        if (lightState == "on") {
          digitalWrite(light_pin, LOW);
          light_state = true; // نرفع العلم إن التشغيل يدوي ثابت
        } else {
          digitalWrite(light_pin, HIGH);
          light_state = false; // نقفل العلم عشان الـ LDR يرجع ياخد التحكم لو عاوز
        }

      }
    }
  }
}


// --- trans. to pi ---
void sendJsonToPi() {
  StaticJsonDocument<500> doc;
  
  // تجميع قراءات الحساسات  
  JsonArray sensors = doc.createNestedArray("soil_sensors");
  for(int i=0; i<3; i++) sensors.add(round(((sensorValues[i] / 4095.0) * 100.0) * 100.0) / 100.0);
  doc["temp_sensor"] = current_temp;

  // تجميع حالة الأجهزة
  JsonArray v_states = doc.createNestedArray("valves");
  for(int i=0; i<3; i++) v_states.add(valves_state[i]);
  
  doc["fans"] = fans_state;
  doc["heater"] = heater_state;

  doc["motion_sensor"] = motion_state;

  doc["pump"] = pump_state;
  doc["LDR"] = round(((current_LDR / 4095.0) * 100.0) * 100.0) / 100.0;
  doc["light"] = light_state;

  // إرسال النص النهائي عبر السيريال
  serializeJson(doc, Serial);
  Serial.println(); // سطر جديد عشان الـ Pi يعرف إن الرسالة خلصت
}
