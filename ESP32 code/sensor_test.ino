#include <ArduinoJson.h>

const int LDR_sensor_pin = 32; 
const int light_pin = 21;

unsigned long totalEffectiveMillis = 0; 
unsigned long targetMillis = 0; 
unsigned long lastUpdateMillis = 0;      
unsigned long dayResetMillis = 0;

int currentGroup = 0;

const unsigned long ONE_DAY_MILLIS = 86400000; // 24 ساعة بالمللي ثانية

void setup() {
  Serial.begin(9600);
  pinMode(light_pin, OUTPUT);
  lastUpdateMillis = millis();
  dayResetMillis = millis();
}

void loop() {
  unsigned long currentMillis = millis();
  unsigned long deltaTime = currentMillis - lastUpdateMillis;
  lastUpdateMillis = currentMillis;

  // 1. التصفير اليومي التلقائي أو استقبال أمر الـ Reset من الراسبري باي
  if (currentMillis - dayResetMillis >= ONE_DAY_MILLIS) {
    resetDay();
  }

  processSerialData();

  // 2. قراءة الحساس اللحظية وتحويلها لنسبة
  int rawLDR = analogRead(LDR_sensor_pin);
  float currentPercentage = (rawLDR / 4095.0) * 100.0;

  // 3. استدعاء دالة التحكم وتمرير رقم الجروب (هنجرب بجروب 1 مثلاً)
  LDR_control(currentGroup, currentPercentage, deltaTime);

  // 4. طباعة الحالة كل نص ثانية عشان تتابع السيريال مونيتور بوضوح
  static unsigned long lastLog = 0;
  if (currentMillis - lastLog > 500) { 
    Serial.print("Group Target: ");
    Serial.print(targetMillis / 1000);
    Serial.print("s | Light: ");
    Serial.print(currentPercentage);
    Serial.print("% | Progress: ");
    Serial.print(totalEffectiveMillis / 1000);
    Serial.println("s");
    lastLog = currentMillis;
  }
}

// --- دالة التحكم الأساسية (بالمنطق الفوري) ---
void LDR_control(int group, float currentPct, unsigned long delta) {
  
  // أ: تحديد الهدف بناءً على الجروب (بالثواني للتجربة)
  // لما تخلص تجارب، شيل الـ 30000 وحط (8 * 3600000) للجروب الأول والثالث
  // وشيل الـ 60000 وحط (10 * 3600000) للجروب التاني
  if (group == 1 || group == 3) {
    targetMillis = 30000; 
  } else if (group == 2) {
    targetMillis = 60000; 
  }

  // ب: المنطق المباشر الفوري (بدون أي تأخير أو فواصل)
  if (totalEffectiveMillis < targetMillis) {
    
    if (currentPct < 66.0) {
      digitalWrite(light_pin, HIGH); // محتاجين نور صناعي
    } else {
      digitalWrite(light_pin, LOW);  // النور الطبيعي كفاية
    }
    
    // في الحالتين النبات بياخد ضوء، فبنزود العداد التراكمي
    totalEffectiveMillis += delta; 
    
  } else {
    // النبات خد وقته بالكامل، اطفي الليد إجباري
    digitalWrite(light_pin, LOW);
  }
}

// دالة تصفير العداد
void resetDay() {
    totalEffectiveMillis = 0;
    dayResetMillis = millis();
    Serial.println("--- New Cycle / Day Started! ---");
}



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
        } else if (groupStr == "group2") {
          currentGroup = 2;
        } else if (groupStr == "group3") {
          currentGroup = 3;
        }
        /*
        if (lightState == "on") {
          digitalWrite(camera_light_pin, HIGH);
        } else {
          digitalWrite(camera_light_pin, LOW);
        }

        Serial.print("Updated Group: ");
        Serial.println(currentGroup);
        Serial.print("Camera Light: ");
        Serial.println(lightState);*/

      } /*else {
        Serial.print("JSON parsing failed: ");
        Serial.println(error.c_str());
      }*/
    }
  }
}