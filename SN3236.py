import time 
import RPi.GPIO as GPIO
import smbus

SN3236_I2CADDR      = 0x3c
SN3236_POWER        = 0x00
SN3236_PWMREG_HIGH  = 0x01      # 01H-24H,OUT1-OUT36,PWM256级
SN3236_UpdateREG    = 0x25      # 更新寄存器,01H-24H,26h-49h
SN3236_LEDConfig    = 0x26      # 26H-49H,
SN3236_RESET        = 0x4F
SN3236_ALLOFF       = 0x4A

#color                [B,G,R]
SN3236_R            = [0x00,0x00,0xff]
SN3236_B            = [0x00,0xff,0x00]
SN3236_G            = [0xff,0x00,0x00]
SN3236_P            = [86,78,255]
SN3236_HWPWR        = 13        # Power Enable use BCM GPIO.13

class SN3236(object) :
    def __init__(self,addr = 0x3c) :
        self.i2c = smbus.SMBus(1)
        SN3236_I2CADDR = addr
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SN3236_HWPWR,GPIO.OUT)
        GPIO.output(SN3236_HWPWR,GPIO.LOW)

    def SN3236_PwrOn(self) :
        GPIO.output(SN3236_HWPWR,GPIO.HIGH)
        self.i2c.write_byte_data(SN3236_I2CADDR,SN3236_POWER,0x01)

    def SN3236_PwrOff(self) :
        self.i2c.write_byte_data(SN3236_I2CADDR,SN3236_POWER,0x00)
        GPIO.output(SN3236_HWPWR,GPIO.LOW)

    def SN3236_Rstreg(self) :
        self.i2c.write_byte_data(SN3236_I2CADDR,SN3236_RESET,0x01)

    def SN3236_Test(self,color) :
        PWM_Value = color * 12
        ON_Value = [0x01] *36
        self.i2c.write_i2c_block_data(SN3236_I2CADDR,SN3236_PWMREG_HIGH,PWM_Value[0:18])
        self.i2c.write_i2c_block_data(SN3236_I2CADDR,SN3236_PWMREG_HIGH + 0x12,PWM_Value[18:36])
        self.i2c.write_i2c_block_data(SN3236_I2CADDR,SN3236_LEDConfig,ON_Value[0:18])
        self.i2c.write_i2c_block_data(SN3236_I2CADDR,SN3236_LEDConfig + 0x12,ON_Value[18:36])
        self.i2c.write_byte_data(SN3236_I2CADDR,0x25,0x01)

    def SN3236_Show(self,color) :
        PWM_Value = color
        ON_Value = [0x01] *36
        self.i2c.write_i2c_block_data(SN3236_I2CADDR,SN3236_PWMREG_HIGH,PWM_Value[0:18])
        self.i2c.write_i2c_block_data(SN3236_I2CADDR,SN3236_PWMREG_HIGH + 0x12,PWM_Value[18:36])
        self.i2c.write_i2c_block_data(SN3236_I2CADDR,SN3236_LEDConfig,ON_Value[0:18])
        self.i2c.write_i2c_block_data(SN3236_I2CADDR,SN3236_LEDConfig + 0x12,ON_Value[18:36])
        self.i2c.write_byte_data(SN3236_I2CADDR,0x25,0x01)

    
def main() :
    a = SN3236()
    a.SN3236_PwrOn()
    a.SN3236_Test(SN3236_R)
    time.sleep(0.5)
    a.SN3236_Test(SN3236_B)
    time.sleep(0.5)
    a.SN3236_Test(SN3236_G)
    time.sleep(0.5)
    a.SN3236_Test(SN3236_P)
    time.sleep(1)
    a.SN3236_Rstreg()
    a.SN3236_PwrOff()

if __name__ == '__main__' :
	main()
