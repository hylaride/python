#!/usr/local/bin/python
#
# Copyright (c) 2004 Christopher Hawkins Hylarides
#
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#  3. The name Christopher Hawkins Hylarides may not be used to endorse
#     or promote products derived from this software without specific
#     prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY CHRISTOPHER HAWKINS HYLARIDES "AS IS" AND ANY
#  EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED.  IN NO EVENT SHALL CHRISTOPHER HAWKINS HYLARIDES BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
#  OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
#  OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#  SUCH DAMAGE.
#

# This is an LED moving sign script I wrote circa 2003ish to write to an 8 horiziontal
# line shift-register LED sign via the serial output.  It simply reads from a message
# posted to a URL via a separate CGI script, scrolls it, and then displays the time.


import serial, urllib
from time import strftime

#The "8" bit values that make up the fonts
#Credit to Dan Fraser for creating most of these.
font = {'!' : [0,0,103,111,103], \
'\"' : [3,7,3,0,3,7,3], \
'#' : [20,20,127,20,127,20,20], \
'$' : [38,73,73,127,73,73,50], \
'%' : [71,37,23,8,116,82,113], \
'&' : [48,74,77,77,18,32,80], \
'\47' : [0,0,11,7,3], \
'(' : [0,28,34,65,65], \
')' : [0,0,65,65,34,28], \
'*' : [8,42,28,8,28,42,8], \
'+' : [0,8,8,62,8,8,], \
',' : [0,0,88,56,24], \
'-' : [0,8,8,8,8,8,], \
'.' : [0,0,112,112,112], \
'/' : [64,32,16,8,4,2,1], \
'0' : [28,34,65,65,65,34,28], \
'1' : [0,68,66,127,64,64,0], \
'2' : [114,73,73,73,73,73,70], \
'3' : [34,73,73,73,73,73,54], \
'4' : [31,16,16,16,16,126,16], \
'5' : [47,73,73,73,73,73,49], \
'6' : [62,73,73,73,73,73,50], \
'7' : [3,1,113,9,5,3,1], \
'8' : [54,73,73,73,73,73,54], \
'9' : [38,73,73,73,73,73,62], \
':' : [0,34,119,34,0], \
';' : [0,0,91,59,27], \
'<' : [0,8,20,34,65], \
'=' : [0,20,20,20,20,20], \
'>' : [0,0,65,34,20,8], \
'?' : [2,1,1,89,9,9,6], \
'@' : [62,65,93,93,93,81,14], \
'A' : [120,20,18,17,18,20,120], \
'B' : [127,73,73,73,73,73,54], \
'C' : [62,65,65,65,65,65,34], \
'D' : [127,65,65,65,65,65,62], \
'E' : [127,73,73,73,73,65,65], \
'F' : [127,9,9,9,9,1,1], \
'G' : [62,65,65,73,73,73,58], \
'H' : [127,8,8,8,8,8,127], \
'I' : [0,0,65,127,65], \
'J' : [48,64,64,64,64,64,63], \
'K' : [127,8,8,20,34,65], \
'L' : [127,64,64,64,64,64,64], \
'M' : [127,2,4,8,4,2,127], \
'N' : [127,2,4,8,16,32,127], \
'O' : [127,65,65,65,65,65,127], \
'P' : [127,9,9,9,9,9,6], \
'Q' : [62,65,65,65,81,33,94], \
'R' : [127,9,9,9,25,41,70], \
'S' : [38,73,73,73,73,73,50], \
'T' : [1,1,1,127,1,1,1], \
'U' : [63,64,64,64,64,64,63], \
'V' : [15,16,32,64,32,16,15], \
'W' : [63,64,64,62,64,64,63], \
'X' : [65,34,20,8,20,34,65], \
'Y' : [1,2,4,120,4,2,1], \
'Z' : [65,97,81,73,69,67,65], \
'\[' : [0,127,65,65,65,65], \
'\\' : [1,2,4,8,16,32,64], \
'\]' : [0,65,65,65,65,127], \
'^' : [0,4,2,1,2,4], \
'_' : [64,64,64,64,64,64,64], \
'`' : [0,0,3,7,11], \
'a' : [0,120,20,18,18,20,120], \
'b' : [0,126,74,74,74,74,52], \
'c' : [0,60,66,66,66,66,36], \
'd' : [0,126,66,66,66,66,60], \
'e' : [0,126,74,74,74,74,66], \
'f' : [0,126,10,10,10,10,2], \
'g' : [0,60,66,66,82,82,52], \
'h' : [0,126,8,8,8,8,126], \
'i' : [0,126], \
'j' : [0,32,64,64,64,64,62], \
'k' : [0,126,8,8,24,36,66], \
'l' : [0,126,64,64,64,64,64], \
'm' : [0,126,4,8,8,4,126], \
'n' : [0,126,4,8,16,32,126], \
'o' : [0,60,66,66,66,66,60], \
'p' : [0,126,18,18,18,18,12], \
'q' : [0,60,66,66,82,34,92], \
'r' : [0,126,18,18,18,50,76], \
's' : [0,36,74,74,74,74,48], \
't' : [2,2,126,2,2], \
'u' : [0,62,64,64,64,64,62], \
'v' : [0,30,32,64,64,32,30], \
'w' : [0,126,32,16,16,32,126], \
'x' : [0,66,36,24,24,36,66], \
'y' : [0,2,4,120,4,2], \
'z' : [0,66,98,82,74,70,66], \
'{' : [8,62,65,65,65], \
'|' : [0,0,0,119], \
'}' : [0,0,65,65,65,62,8], \
'~' : [2,1,1,2,4,4,2], \
' ' : [0,0,0,0,0], \
'\n' : [0,0,0,0,0], \
'\t' : [0]}

temp=[]
message = ""
message2 = []
diamonds = "Forever"

ser = serial.Serial('/dev/tty01', 19200, timeout=1)

#blank the screen
def blank(nothing):
    ser.write(chr(200))
    a = range(84)
    for x in a:
        ser.write(chr(0))
    ser.write(chr(200))

#add some whitespace to the beginning of the scroll
def white(nothing):
    num = 0
    while num <= 84:
        temp.append(0)
        num = num + 1

blank(0)
white(0)

#permenant while loop.  Because diamonds are forever. ;-)
while diamonds:
    message = ""
    message2 = []
    count = 10 #number of seconds to display the clock
    content = urllib.urlopen("http://some.place.com/message.txt")
    message = content.read()
    content.close()

    #Get the message and put it into an list
    length = len(message)
    for x in range(length):
        message2.append(message[x])

    #Take the list and convert it into the binary font for output
    for w in range(len(message2)):
        move = (font[message2[w]])
        for x in range(len(move)):
            temp.append(move[x])

    #Add trailing whitespace for clarity!
    num = 0
    while num <= 86:
        temp.append(0)
        num = num+1

    #Write to the serial port, knocking of the lead "byte - 1"
    w = 0
    while temp:
        while w <= 84:
            ser.write(chr(temp[w]))
            if len(temp) == 84:
                temp.append(0)
                for t in range(len(temp)):
                    ser.write(chr(temp[t]))
                    temp.append(0)
                    temp.pop(0)
                break
            w = w + 1
        w = 0
        ser.write(chr(200))
        temp.pop(0)
        if len(temp) == 84:
            break
    ser.write(chr(200))

    #Clock shit
    time2 = strftime('%X')
    while count != 0:
        ser.write(chr(200))
        time = strftime('%X')
        message = []
        code = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        #Get the message and put it into an list
        length = len(time)
        for x in range(length):
            message.append(time[x])

        #Take the list and convert it into the binary font for output
        for w in range(len(message)):
            move = (font[message[w]])
            for x in range(len(move)):
                code.append(move[x])

        #Add trailing whitespace.  That way if there is an error
        #it gets wiped out on the next update
        v=0
        while v == 0:
            if len(code) != 84:
                code.append(0)
            else:
                v=1

        #Only update the sign if the time has changed (to the nearest
        #second of course :)
        x = 0
        if time != time2:
            while x <= 83:
                ser.write(chr(code[x]))
                x = x+1
            count = count - 1
        time2 = time

    blank(0)
ser.close()
