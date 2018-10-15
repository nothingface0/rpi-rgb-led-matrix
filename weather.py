from os import system
from skimage.io import imread
import numpy as np

fetch_command='''curl -s "https:$(curl -s 'https://www.meteoblue.com/en/weather/forecast/air/meyrin_switzerland_2659667' | grep -oE "data-original='[^']*'" | grep -oE "[^']*meteoblue[^']*" | sed -e 's/&amp;/\&/g' )" > /tmp/weather'''


def fetch():
    return system(fetch_command) == 0

def read():
    return imread("/tmp/weather")

def findStartOffset(img):
    return (img[-12,:,0] < 200).nonzero()[0][0]

def timeScale(img):
    offs = findStartOffset(img)
    width = len(img[0,:,0])
    used = width - 2*offs
    scale = used / (6*11) # 11 blocks of 6h displayed
    def offset(hours):
        return offs + hours * scale
    return offset

def isYellow(pixels):
    return (pixels[:,0]/4 + pixels[:,1]/4) > pixels[:,2]
def isRed(pixels):
    return (pixels[:,1]/2 + pixels[:,2]/2) < pixels[:,0]/4
def isBlue(pixels):
    return (pixels[:,0]/2 + pixels[:,1]/2) < pixels[:,2]/2

#TODO: compute from the image
def sunRange(img):
    return (-22, -90)
def cloudRange(img):
    return (-250, -440)
def rainRange(img):
    return(-470, -540)
def tempRange(img):
    return (-831, -920)
    

def readLine(img, offs, colorTest, r):
    pixels = img[r[0]:r[1]:-1, offs,:]
    y = colorTest(pixels).nonzero()[0]
    val = y[-1] if len(y) > 0 else 0
    return val*1.0/(r[0]-r[1])

def relativeSun(img, offs):
    return readLine(img, offs, isYellow, sunRange(img))

def relativeTemp(img, offs):
    return readLine(img, offs, isRed, tempRange(img))

def relativeHum(img, offs):
    return readLine(img, offs, isBlue, tempRange(img))

def relativeRain(img, offs):
    r = rainRange(img)
    pixels = img[r[0]:r[1]:-1, offs,:]
    y = isBlue(pixels).nonzero()[0]
    val = len(y)
    return val*1.0/(r[0]-r[1])

def greylevel(color):
    m, c = -0.61, 141
    return -1 if color.var() > 1 or color.sum() > 700 else m*color.mean()+c


def clouds(img, offs, points):
    r = cloudRange(img)
    idxs = np.linspace(0, (r[0]-r[1])-1, points, dtype=int)
    pixels = img[r[0]:r[1]:-1, offs,:]
    return [greylevel(pixels[i,:]) for i in idxs]

def weatherimg(img, size, hoursperpixel):
    buf = np.zeros((size, size, 3), dtype=np.uint8)
    scale = timeScale(img)
    for i in range(size):
        offs = int(round(scale(i*hoursperpixel)))
        c = clouds(img, offs, size)
        for y in range(size):
            if c[y] > 0:
                buf[i,y,:] = c[y] * 250

        r = relativeRain(img, offs)*(size-1)
        for y in range(int(round(r))):
            buf[i,y,2] = 200
            buf[i,y,:2] = 0

        s = relativeSun(img, offs)*(size-1)
        y = int(round(s))
        buf[i,y,:2] = 200
        buf[i,y,2] = 0

        t = relativeTemp(img, offs)*(size-1)
        y = int(round(t))
        buf[i,y,0] = 200
        buf[i,y,1:] = 0
    return buf

def toString(buf, col):
    return "\n".join(["".join(map(lambda x: "#" if x > 0 else " ", row)) for row in buf[:,:,col]])
        
