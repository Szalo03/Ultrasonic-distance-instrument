import machine
import time
import framebuf

# ==========================================
# 1. TŘÍDA PRO DISPLEJ NOKIA 5110 (PCD8544)
# ==========================================
class PCD8544(framebuf.FrameBuffer):
    def __init__(self, spi, cs, dc, rst):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.width = 84
        self.height = 48
        self.buffer = bytearray((self.height // 8) * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        self.rst.value(0)
        time.sleep_ms(10)
        self.rst.value(1)
        
        self.command(0x21) # Rozšířené příkazy
        self.command(0xBF) # Kontrast
        self.command(0x04) # Teplotní koeficient
        self.command(0x14) # Bias
        self.command(0x20) # Základní příkazy
        self.command(0x0C) # Normální zobrazení
        self.clear()
        self.show()

    def command(self, data):
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytearray([data]))
        self.cs.value(1)

    def clear(self):
        self.fill(0)

    def show(self):
        self.command(0x40)
        self.command(0x80)
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(self.buffer)
        self.cs.value(1)

# ==========================================
# 2. FUNKCE PRO SENZOR HC-SR04
# ==========================================
def measure_distance(trig_pin, echo_pin):
    trig_pin.value(0)
    time.sleep_us(2)
    
    trig_pin.value(1)
    time.sleep_us(10)
    trig_pin.value(0)
    
    try:
        pulse_time = machine.time_pulse_us(echo_pin, 1, 30000)
        if pulse_time > 0:
            return (pulse_time * 0.0343) / 2
    except OSError:
        pass
    return -1.0

# ==========================================
# 3. HLAVNÍ PROGRAM (MAIN)
# ==========================================
# Pin konfigurace
# BL=0, DC=1, RST=2, CS(CE)=17, SCK=18, MO=19, Buzzer_S=12
trig = machine.Pin(4, machine.Pin.OUT)
echo = machine.Pin(5, machine.Pin.IN)

rst = machine.Pin(2, machine.Pin.OUT)
dc = machine.Pin(1, machine.Pin.OUT)
cs = machine.Pin(17, machine.Pin.OUT)
bl = machine.Pin(0, machine.Pin.OUT)
bl.value(1) # Podsvícení (vypnuto)

# Inicializace Buzzeru (PWM pro generování tónu) na Pinu 16
buzzer = machine.PWM(machine.Pin(12))
buzzer.freq(1000) # Frekvence tónu 1 kHz
buzzer.duty_u16(0) # Na začátku je bzučák potichu

# Inicializace SPI displeje
spi = machine.SPI(0, baudrate=3200000, polarity=0, phase=0, 
                  sck=machine.Pin(18), mosi=machine.Pin(19))
lcd = PCD8544(spi, cs, dc, rst)

# Uvítání
lcd.clear()
lcd.text("Radar s", 18, 10, 1)
lcd.text("buzzerem", 14, 25, 1)
lcd.show()
time.sleep(2)

# Proměnné pro neblokující pípání
last_beep_time = time.ticks_ms()
buzzer_is_on = False
while True:
    dist = measure_distance(trig, echo)
    current_time = time.ticks_ms()
    
    lcd.clear()
    lcd.text("Vzdalenost:", 0, 0, 1)
    
    if dist >= 0:
        lcd.text("{:.1f} cm".format(dist), 0, 15, 1)
        
        # Grafický ukazatel (čára se zkracuje s klesající vzdáleností)
        bar_length = int(min(dist, 84))
        lcd.fill_rect(0, 30, bar_length, 8, 1) 
        
        # Logika pípání bzučáku
        if dist < 10.0:
            # Kritická blízkost: nepřerušovaný tón
            buzzer.duty_u16(32768) # 50% střída pro hlasitý zvuk
            buzzer_is_on = True
        elif dist < 50.0:
            # Běžná blízkost: pípání s frekvencí podle vzdálenosti
            # Výpočet intervalu: např. 40 cm = 400 ms pauza, 10 cm = 100 ms pauza
            beep_interval = int(dist * 10) 
            
            # Pokud uběhl časový interval, přepneme stav bzučáku
            if time.ticks_diff(current_time, last_beep_time) > beep_interval:
                buzzer_is_on = not buzzer_is_on
                if buzzer_is_on:
                    buzzer.duty_u16(32768) # Zapnout zvuk
                else:
                    buzzer.duty_u16(0)     # Vypnout zvuk
                last_beep_time = current_time
        else:
            # Bezpečná vzdálenost (nad 50 cm): ticho
            buzzer.duty_u16(0)
            buzzer_is_on = False
            
    else:
        lcd.text("Mimo dosah", 0, 15, 1)
        buzzer.duty_u16(0) # Ticho při chybě měření

    lcd.show()
    time.sleep_ms(50)
