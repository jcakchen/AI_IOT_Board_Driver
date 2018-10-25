import time
import RPi.GPIO as GPIO
import smbus

MPR121_I2CADDR  = 0x5A

MPR121_TOUCHSTATUS_L    = 0x00
MPR121_TOUCHSTATUS_H    = 0x01
MPR121_FILTDATA_0L      = 0x04
MPR121_FILTDATA_0H      = 0x05
MPR121_BASELINE_0       = 0x1E
MPR121_MHDR             = 0x2B
MPR121_NHDR             = 0x2C
MPR121_NCLR             = 0x2D
MPR121_FDLR             = 0x2E
MPR121_MHDF             = 0x2F
MPR121_NHDF             = 0x30
MPR121_NCLF             = 0x31
MPR121_FDLF             = 0x32
MPR121_NHDT             = 0x33
MPR121_NCLT             = 0x34
MPR121_FDLT             = 0x35
MPR121_TOUCHTH_0        = 0x41
MPR121_RELEASETH_0      = 0x42
MPR121_DEBOUNCE         = 0x5B
MPR121_CONFIG1          = 0x5C
MPR121_CONFIG2          = 0x5D
MPR121_CHARGECURR_0     = 0x5F
MPR121_CHARGETIME_1     = 0x6C
MPR121_ECR              = 0x5E
MPR121_AUTOCONFIG0      = 0x7B
MPR121_AUTOCONFIG1      = 0x7C
MPR121_UPLIMIT          = 0x7D
MPR121_LOWLIMIT         = 0x7E
MPR121_TARGETLIMIT      = 0x7F
MPR121_GPIODIR          = 0x76
MPR121_GPIOEN           = 0x77
MPR121_GPIOSET          = 0x78
MPR121_GPIOCLR          = 0x79
MPR121_GPIOTOGGLE       = 0x7A
MPR121_SOFTRESET        = 0x80

class MPR121(object) :

    def __init__(self,pin_irq = 25,mode = "Normal",callback = None) :
        self.MPR121_IRQ = pin_irq
        self.mode = mode
        self.i2c = smbus.SMBus(1)
        self.callback = callback
        if(self.callback == None) :
            self.callback = self.MPR121_Callback
        if(self.mode == "Normal") :
            self.MPR121_IRQ == None
        elif(self.mode == "IRQ") :
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.MPR121_IRQ,GPIO.IN,pull_up_down = GPIO.PUD_UP)
            GPIO.add_event_detect(self.MPR121_IRQ, GPIO.FALLING, callback=self.callback)
        else :
            print("error: mode style isn't \"Normal\" or \"IRQ\" ！")
            exit()
        self.MPR121_Init(12,6)
        
    def MPR121_Init(self,touch,release) :
        # 复位芯片
        self.i2c.write_byte_data(MPR121_I2CADDR,MPR121_SOFTRESET,0x63)
        self.i2c.write_byte_data(MPR121_I2CADDR,MPR121_ECR,0x00)
        if self.i2c.read_byte_data(MPR121_I2CADDR,MPR121_CONFIG2) != 0x24 :
            print("error: Init MPR121 false!")
            exit()
        # 设置阈值
        assert touch >= 0 and touch <= 255
        assert release >= 0 and release <= 255
        for i in range(12):
            self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_TOUCHTH_0 + 2 * i, touch)
            self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_RELEASETH_0 + 2 * i, release)
        # 配置基线过滤器
        self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_MHDR,0x01)
        self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_NHDR,0x01)
        self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_NCLR,0x0E)
        self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_FDLR,0x00)
        self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_MHDF,0x01)
        self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_NHDF,0x05)
        self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_NCLF,0x01)
        self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_FDLF,0x00)
        self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_NHDT,0x00)
        self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_NCLT,0x00)
        self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_FDLT,0x00)
        # 配置其他寄存器
        self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_DEBOUNCE,0x00)
        self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_CONFIG1,0x10)
        self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_CONFIG2,0x20)
        # 使能所有电极
        self.i2c.write_byte_data(MPR121_I2CADDR, MPR121_ECR,0x8F)

    def MPR121_Get(self) :
        value = self.i2c.read_byte_data(MPR121_I2CADDR, MPR121_TOUCHSTATUS_H)
        value = (value << 8) + self.i2c.read_byte_data(MPR121_I2CADDR, MPR121_TOUCHSTATUS_L)
        # print("Value:" + bin(value))
        return value

    def MPR121_Callback(self,channel):
        value = self.MPR121_Get()
        print(bin(value))


def main() :
    print("Please Choose test mode:")
    print("Input 1: Normal mode")
    print("Input 2: Interrupt mode")
    print("Input 3: Interrupt mode with user callback\n")
    mode = input("Enter your choose: ")
    if(mode == "1") :
        global MPR121_touch
        MPR121_touch = MPR121()
        while(1) :
            value = MPR121_touch.MPR121_Get()
            print(bin(value))
            time.sleep(0.5)
    elif(mode == "2") :
        MPR121_touch = MPR121(25,"IRQ")
        while(1) :
            time.sleep(1)
    elif(mode == "3") :
        MPR121_touch = MPR121(25,"IRQ",User_Callback)
        while(1) :
            time.sleep(1)
    else :
        print("Error:Input faile,will exit!")
        exit()

def User_Callback(channel) :
    value = MPR121_touch.MPR121_Get()
    print(value)
    if(value != 0):
        for i in range(0,12,1) :
            tmp = value >> i
            if(tmp & 0x01) :
                print("The pad " + str(i) + "has ben push!")
        print("\n")

if __name__ == '__main__' :
	main()