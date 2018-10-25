import time
import RPi.GPIO as GPIO
import smbus
import spidev
import G57ASCII

# BCM GPIO5 = RST
# BCM GPIO6 = D/C

class OLED(object) :
    OLED_CMD = 0
    OLED_DATA = 1

    def __init__(self,interface,dev) :
        self.interface = interface
        self.dev = dev
        if(self.interface == "SPI") :
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(5,GPIO.OUT)
            GPIO.output(5,GPIO.LOW)
            GPIO.setup(6,GPIO.OUT)
            GPIO.output(6,GPIO.LOW)
            self.spi = spidev.SpiDev()
            self.spi.open(0,self.dev)
            self.OLED_Reset()
        elif(self.interface == "I2C") :
            self.dev = 0x3c
            self.i2c = smbus.SMBus(1)
        else :
            print("Interface Write fail！")
            exit()
        self.OLED_Init()

    def OLED_Reset(self) :
        GPIO.output(5,GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(5,GPIO.HIGH)
        time.sleep(0.1)

    def OLED_Write_Byte(self,data,DC) :
        if(self.interface == "SPI") :
            if DC :
                GPIO.output(6,GPIO.HIGH)
            else :
                GPIO.output(6,GPIO.LOW)
            to_send = [data]
            self.spi.xfer(to_send)
            GPIO.output(5,GPIO.HIGH)
        else :
            if DC :             # DATA = 1
                self.i2c.write_byte_data(self.dev,0x40,data)
            else :              # CMD = 0
                self.i2c.write_byte_data(self.dev,0x00,data)
    
    def OLED_Write_Point(self,data) :
        for i in range(0,len(data),1) :
            self.OLED_Write_Byte(data[i],self.OLED_DATA)        

    def OLED_Set_Pos(self,row,col) :
        col_L = int(col % 16)
        col_H = int(col / 16)
        self.OLED_Write_Byte(0xb0 + row,self.OLED_CMD)             # 设置行
        self.OLED_Write_Byte(0x00 + col_L,self.OLED_CMD)           # 设置列
        self.OLED_Write_Byte(0x10 + col_H,self.OLED_CMD)           # 设置列 col_H *16 + col_L

    def OLED_Display_Clear(self,data) :
        for i in range(0,8,1) :
            self.OLED_Set_Pos(i,0)
            for j in range(0,128,1) :
                self.OLED_Write_Byte(data,self.OLED_DATA)

    def OLED_Display_Chr(self,row,col,data) :
        self.OLED_Set_Pos(row,col)
        self.OLED_Write_Point(data)

    def OLED_Display_Str(self,row,col,data) :
        str_data = []
        str_len  = len(data)
        str_remain = int((128 - col) / 5)                       # 所在行剩余字符
        if(str_len < str_remain) :
            str_line = 1
        else :
            str_line = int((str_len - str_remain) / 25) + 2 
        if(str_line == 1):
            for i in range(0,str_len,1) :
                str_data = str_data + G57ASCII.g57Ascii[ord(data[i]) - 32]
            self.OLED_Set_Pos(row,col)
            self.OLED_Write_Point(str_data) 
        else :
            for i in range(0,str_remain,1) :
                str_data = str_data + G57ASCII.g57Ascii[ord(data[i]) - 32]
            self.OLED_Set_Pos(row,col)
            self.OLED_Write_Point(str_data)
            for i in range(0,str_line - 1,1) :
                str_data = []
                if(i == str_line -2) :
                    str_last = int((str_len - str_remain) % 25)
                    for j in range(0,str_last,1) :
                        str_data = str_data + G57ASCII.g57Ascii[ord(data[j + (str_len - str_last)]) - 32]
                elif((i + row) > 7) :
                    i = str_line - 1
                else :
                    for j in range(0,25,1) :
                        str_data = str_data + G57ASCII.g57Ascii[ord(data[j + i * 25 + str_remain]) - 32]
                self.OLED_Set_Pos(row + 1 + i,0)
                self.OLED_Write_Point(str_data)

    def OLED_Display_Image(self,data) :
        for i in range(0,8,1) :
            self.OLED_Set_Pos(i,0)
            self.OLED_Write_Point(data[i * 128:(i + 1) * 128 -1])
            

    def OLED_Init(self) :
        self.OLED_Write_Byte(0xAE,self.OLED_CMD)          #--turn off oled panel
        self.OLED_Write_Byte(0x00,self.OLED_CMD)          #---set low column address
        self.OLED_Write_Byte(0x10,self.OLED_CMD)          #---set high column address
        self.OLED_Write_Byte(0x40,self.OLED_CMD)          #--set start line address  Set Mapping RAM Display Start Line (0x00~0x3F)
        self.OLED_Write_Byte(0x81,self.OLED_CMD)          #--set contrast control register
        self.OLED_Write_Byte(0xCF,self.OLED_CMD)          #/ Set SEG Output Current Brightness
        self.OLED_Write_Byte(0xA1,self.OLED_CMD)          #--Set SEG/Column Mapping     0xa0左右反置 0xa1正常
        self.OLED_Write_Byte(0xC8,self.OLED_CMD)          #Set COM/Row Scan Direction   0xc0上下反置 0xc8正常
        self.OLED_Write_Byte(0xA6,self.OLED_CMD)          #--set normal display
        self.OLED_Write_Byte(0xA8,self.OLED_CMD)          #--set multiplex ratio(1 to 64)
        self.OLED_Write_Byte(0x3f,self.OLED_CMD)          #--1/64 duty
        self.OLED_Write_Byte(0xD3,self.OLED_CMD)          #-set display offset	Shift Mapping RAM Counter (0x00~0x3F)
        self.OLED_Write_Byte(0x00,self.OLED_CMD)          #-not offset
        self.OLED_Write_Byte(0xd5,self.OLED_CMD)          #--set display clock divide ratio/oscillator frequency
        self.OLED_Write_Byte(0x80,self.OLED_CMD)          #--set divide ratio, Set Clock as 100 Frames/Sec
        self.OLED_Write_Byte(0xD9,self.OLED_CMD)          #--set pre-charge period
        self.OLED_Write_Byte(0xF1,self.OLED_CMD)          #Set Pre-Charge as 15 Clocks & Discharge as 1 Clock
        self.OLED_Write_Byte(0xDA,self.OLED_CMD)          #--set com pins hardware configuration
        self.OLED_Write_Byte(0x12,self.OLED_CMD)          #
        self.OLED_Write_Byte(0xDB,self.OLED_CMD)          #--set vcomh
        self.OLED_Write_Byte(0x40,self.OLED_CMD)          #Set VCOM Deselect Level
        self.OLED_Write_Byte(0x20,self.OLED_CMD)          #-Set Page Addressing Mode (0x00/0x01/0x02)
        self.OLED_Write_Byte(0x02,self.OLED_CMD)          #
        self.OLED_Write_Byte(0x8D,self.OLED_CMD)          #--set Charge Pump enable/disable
        self.OLED_Write_Byte(0x14,self.OLED_CMD)          #--set(0x10) disable
        self.OLED_Write_Byte(0xA4,self.OLED_CMD)          # Disable Entire Display On (0xa4/0xa5)
        self.OLED_Write_Byte(0xA6,self.OLED_CMD)          # Disable Inverse Display On (0xa6/a7) 
        self.OLED_Write_Byte(0xAF,self.OLED_CMD)          #--turn on oled panel
        self.OLED_Display_Clear(0x00)

def main() :
#    oled = OLED("I2C",1)
    oled2 = OLED("SPI",0)
#    time.sleep(1)
#    oled.OLED_Display_Clear(0xff)
#    time.sleep(1)
#    oled.OLED_Display_Clear(0x0f)
#    time.sleep(1)
#    oled.OLED_Display_Clear(0x00)
#    time.sleep(1)
#    oled.OLED_Display_Chr(0,123,G57ASCII.g57Ascii[ord('a') - 32])
#    time.sleep(1)
#    oled.OLED_Display_Str(1,5,"abcdef ,.123456")
#    time.sleep(1)
#    oled.OLED_Display_Str(2,100,"abcdef ,.123456")
#    time.sleep(1)
#    oled.OLED_Display_Str(4,60,"I will test OLED,let's test the code to show more than one line!!!!")
#    time.sleep(1)
#    oled.OLED_Display_Image(G57ASCII.g12864BMP2)
#    time.sleep(1)
#    oled.OLED_Display_Image(G57ASCII.g12864BMP1)
#    time.sleep(1)

    
    time.sleep(1)
    oled2.OLED_Display_Clear(0xff)
    time.sleep(1)
    oled2.OLED_Display_Clear(0x0f)
    time.sleep(1)
    oled2.OLED_Display_Clear(0x00)
    time.sleep(1)
    oled2.OLED_Display_Chr(0,123,G57ASCII.g57Ascii[ord('a') - 32])
    time.sleep(1)
    oled2.OLED_Display_Str(1,5,"abcdef ,.123456")
    time.sleep(1)
    oled2.OLED_Display_Str(2,100,"abcdef ,.123456")
    time.sleep(1)
    oled2.OLED_Display_Str(4,60,"I will test OLED,let's test the code to show more than one line!!!!")
    time.sleep(1)
    oled2.OLED_Display_Image(G57ASCII.g12864BMP2)
    time.sleep(1)
    oled2.OLED_Display_Image(G57ASCII.g12864BMP1)
    time.sleep(1)
    
if __name__ == '__main__' :
	main()

#完善程序：
# 1行跳转（完成）
# 2封装画图模式（完成）
# 3补充I2C_OLED模式（完成）
