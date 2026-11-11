# Ultrasonic-distance-instrument

## 🎯 Project Goal
Design and create a functional parking sensor model using a Raspberry Pi Pico W microcontroller. The system displays the precise distance from an obstacle on an LCD screen and provides an audible warning as the distance changes.

---

## 👥 Team Members
> [Marek Šádek](https://github.com/SadekMarek),
> [Marek Gláser](https://github.com/glasermarek),
> [Dávid Szalay](https://github.com/Szalo03)

---

## 🛠️ Hardware & Components

### 1. [Raspberry Pi Pico W](https://pip-assets.raspberrypi.com/categories/686-raspberry-pi-pico-w/documents/RP-008312-DS-2-pico-w-datasheet.pdf)

Chosen as our main microcontroller processing unit for its low cost, dual-core processor, and built-in wireless connectivity capabilities.

<p align="center">
  <img src="Images/raspberry_pinout.png" alt="Raspberry Pi Pico Pinout" />
</p>

---

### 2. [DFRobot Gravity Sensor Expansion Shield](https://wiki.dfrobot.com/dfr0265/)

Simplifies our wiring setup by providing convenient plug-and-play breakout headers for connecting our display, sensors, and buzzer without messy breadboards.

<p align="center">
  <img src="Images/dfrobot_gravity_board.png" alt="DFRobot Gravity Shield" />
</p>

---

### 3. [HC-SR04 Ultrasonic Distance Sensor](https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf) (2×)

Provides accurate, non-contact distance measurement from 2 cm to 400 cm using high-frequency sonar waves to detect nearby obstacles.

<p align="center">
  <img src="Images/HC_SR04_Pinout.png" alt="Ultrasonic Sensor" />
</p>

---

### 4. [Nokia 5110 LCD SPI Display](https://cdn.sparkfun.com/assets/b/1/b/e/f/Nokia5110.pdf)

A low-power 84×48 pixel monochrome display used to output real-time distance measurements, status diagnostics, and visual warnings to the user.

<p align="center">
  <img src="Images/Nokia_5110_LCD_Pinout.png" alt="Nokia 5110 LCD Pinout" />
</p>

---

### 5. [HW-508 v0.2 Passive Buzzer](https://www.datasheethub.com/datasheets/others/hw-508-small-passive-buzzer-module-datasheet.pdf)

Outputs variable-frequency sound alerts that speed up or change tone as an object moves closer to the sensors, creating an intuitive audible parking assistant.

<p align="center">
  <img src="Images/Buzzer_Pinout.png" alt="Passive Buzzer" />
</p>

---
