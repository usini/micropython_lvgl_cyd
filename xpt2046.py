"""XPT2046 Touch module modified for LVGL."""
import lvgl as lv

_STATE_PRESSED = lv.INDEV_STATE.PRESSED
_STATE_RELEASED = lv.INDEV_STATE.RELEASED

class xpt2046(object):
    """Serial interface for XPT2046 Touch Screen Controller."""

    # Command constants from ILI9341 datasheet
    GET_Y = const(0b11010000)  # X position
    GET_X = const(0b10010000)  # Y position
    GET_Z1 = const(0b10110000)  # Z1 position
    GET_Z2 = const(0b11000000)  # Z2 position
    GET_TEMP0 = const(0b10000000)  # Temperature 0
    GET_TEMP1 = const(0b11110000)  # Temperature 1
    GET_BATTERY = const(0b10100000)  # Battery monitor
    GET_AUX = const(0b11100000)  # Auxiliary input to ADC

    def __init__(self, cs=33, baudrate=10, interrupt_pin=36,sck=25,mosi=32,miso=39,
                 width=320, height=240,
                 x_min=100, x_max=1962, y_min=100, y_max=1900):
        """Initialize touch screen controller.

        Args:
            spi (Class Spi):  SPI interface for OLED
            cs (Class Pin):  Chip select pin
            int_pin (Class Pin):  Touch controller interrupt pin
            int_handler (function): Handler for screen interrupt
            width (int): Width of LCD screen
            height (int): Height of LCD screen
            x_min (int): Minimum x coordinate
            x_max (int): Maximum x coordinate
            y_min (int): Minimum Y coordinate
            y_max (int): Maximum Y coordinate
        """
        from machine import SoftSPI, Pin
        self.spi = SoftSPI(baudrate=baudrate*1000*1000, sck=Pin(sck), mosi=Pin(mosi), miso=Pin(miso))
        indev_drv = lv.indev_create()
        indev_drv.set_type(lv.INDEV_TYPE.POINTER)
        indev_drv.set_display(lv.display_get_default())
        indev_drv.set_read_cb(self.read)
        
        self.cs = Pin(cs)
        self.cs.init(self.cs.OUT, value=1)
        self.rx_buf = bytearray(3)  # Receive buffer
        self.tx_buf = bytearray(3)  # Transmit buffer
        self.width = width
        self.height = height
        # Set calibration
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.x_multiplier = width / (x_max - x_min)
        self.x_add = x_min * -self.x_multiplier
        self.y_multiplier = height / (y_max - y_min)
        self.y_add = y_min * -self.y_multiplier
        self.state = False
        self.interrupt = Pin(interrupt_pin, Pin.IN)
   
    def read(self, index_drv,data) -> int:
        if not self.interrupt.value():          
           coords = self.raw_touch()
           if coords is None:
               return False
           x, y = self.normalize(*coords)
           data.point.x, data.point.y = x,y
           data.state = _STATE_PRESSED
           self.state = True
        else:
            if self.state is True:
                data.state = _STATE_RELEASED
                self.state = False
        return False

    def normalize(self, x, y):
        """Normalize mean X,Y values to match LCD screen."""
        x = int(self.x_multiplier * x + self.x_add)
        y = int(self.y_multiplier * y + self.y_add)
        return x, y

    def raw_touch(self):
        """Read raw X,Y touch values.

        Returns:
            tuple(int, int): X, Y
        """
        x = self.send_command(self.GET_X)
        y = self.send_command(self.GET_Y)
        if self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max:
            return (x, y)
        else:
            return None

    def send_command(self, command):
        """Write command to XT2046 (MicroPython).

        Args:
            command (byte): XT2046 command code.
        Returns:
            int: 12 bit response
        """
        self.tx_buf[0] = command
        self.cs(0)
        self.spi.write_readinto(self.tx_buf, self.rx_buf)
        self.cs(1)

        return (self.rx_buf[1] << 4) | (self.rx_buf[2] >> 4)

