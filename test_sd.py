import ili9XXX
import lvgl as lv
import lv_utils
import machine
lv.init()
disp = ili9XXX.ili9341()
disp.init()
import xpt2046
touch = xpt2046.xpt2046()

import espidf as esp
import machine, os, lv_spi, sdcard
spi = lv_spi.SPI(spihost=esp.VSPI_HOST, mosi=23, miso=19, clk=18, cs=5)
sd = sdcard.SDCard(spi, machine.Pin(5))
os.mount(sd, "/sd")
print(os.listdir('/sd'))

scr = lv.obj()
lv.screen_load(scr)

slider = lv.slider(scr)
slider.set_width(150)
slider.align(lv.ALIGN.TOP_MID, 0, 15)

led1 = lv.led(scr)
led1.align(lv.ALIGN.CENTER, 0, 0)
led1.set_brightness(slider.get_value() * 2)
# led1.set_drag(True)
led1.set_size(20,20)

def slider_event_cb(event):
    led1.set_brightness(slider.get_value() * 2)

slider.add_event_cb(slider_event_cb, lv.EVENT.VALUE_CHANGED, None)

# Create a Spinner object
spin = lv.spinner(scr)
spin.set_anim_params(1000, 100)
spin.set_size(100, 100)
spin.align(lv.ALIGN.CENTER, 0, 0)
