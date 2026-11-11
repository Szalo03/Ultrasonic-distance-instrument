# Ultrasonic-distance-instrument

## 🎯 Project Goal
Design and create a functional parking sensor model using a Raspberry Pi Pico W microcontroller. The system displays the precise distance from an obstacle on an LCD screen and provides an audible warning as the distance changes.

---

## 👥 Team Members
> Marek Šádek,
> Marek Gláser,
> Dávid Szalay

---

## 🛠️ Hardware & Components

### 1. [Raspberry Pi Pico W](https://pip-assets.raspberrypi.com/categories/686-raspberry-pi-pico-w/documents/RP-008312-DS-2-pico-w-datasheet.pdf)

Chosen as our main microcontroller processing unit for its low cost, dual-core processor, and built-in wireless connectivity capabilities.

![Raspberry Pi Pico Pinout](Images/raspberry_pinout.png)

---

### 2. [DFRobot Gravity Sensor Expansion Shield](https://wiki.dfrobot.com/dfr0265/)

Simplifies our wiring setup by providing convenient plug-and-play breakout headers for connecting our display, sensors, and buzzer without messy breadboards.

![DFRobot Gravity Shield](Images/dfrobot_gravity_board.png)

---

### 3. [HC-SR04 Ultrasonic Distance Sensor](https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf) (2×)

Provides accurate, non-contact distance measurement from 2 cm to 400 cm using high-frequency sonar waves to detect nearby obstacles.

![Ultrasonic Sensor](Images/HC_SR04_Pinout.png)

---

### 4. [Nokia 5110 LCD SPI Display](https://cdn.sparkfun.com/assets/b/1/b/e/f/Nokia5110.pdf)

A low-power 84×48 pixel monochrome display used to output real-time distance measurements, status diagnostics, and visual warnings to the user.

![Nokia 5110 LCD Pinout](Images/Nokia_5110_LCD_Pinout.png)

---

### 5. [HW-508 v0.2 Passive Buzzer](https://www.datasheethub.com/datasheets/others/hw-508-small-passive-buzzer-module-datasheet.pdf)

Outputs variable-frequency sound alerts that speed up or change tone as an object moves closer to the sensors, creating an intuitive audible parking assistant.

![Passive Buzzer](Images/Buzzer_Pinout.png)

---

