#!/usr/bin/env python3
"""Generate original Casio-inspired assets and S1/Color2 EasyFace projects."""
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'watchfaces' / 'casio-time'
S = 3
FONT = Path('/System/Library/Fonts/Supplemental')

def canvas(w=466, h=466, color=(0, 0, 0, 255)):
    return Image.new('RGBA', (w*S, h*S), color)

def save(im, path):
    im.resize((im.width//S, im.height//S), Image.Resampling.LANCZOS).save(path)

def text(im, label, xy, size, color, font='Arial Bold.ttf', max_width=None):
    f = ImageFont.truetype(str(FONT/font), size*S)
    box = f.getbbox(label)
    layer = Image.new('RGBA', (box[2]+4*S, box[3]-box[1]+4*S))
    ImageDraw.Draw(layer).text((2*S, 2*S-box[1]), label, font=f, fill=color)
    if max_width and layer.width > max_width*S:
        layer = layer.resize((max_width*S, layer.height), Image.Resampling.LANCZOS)
    im.alpha_composite(layer, (int(xy[0]*S-layer.width/2), int(xy[1]*S-layer.height/2)))

def background(aod=False):
    im = canvas(); d = ImageDraw.Draw(im)
    d.line((49*S,86*S,417*S,86*S), fill='#2785a5', width=3*S)
    text(im,'CASIO',(152,58),38,'#f4f5f2',max_width=160)
    text(im,'F-91W',(333,59),29,'#c6a75c','Arial Bold Italic.ttf')
    text(im,'LIGHT',(84,105),18,'#eeeeeb','Arial Narrow Bold.ttf')
    text(im,'ALARM CHRONOGRAPH',(286,105),21,'#c6a75c','Arial Narrow.ttf',254)
    d.polygon([(43*S,104*S),(57*S,98*S),(57*S,110*S)],fill='#be5e36')
    d.rounded_rectangle((27*S,123*S,439*S,326*S),radius=35*S,outline='#cdd1d1',width=2*S)
    d.rounded_rectangle((35*S,131*S,431*S,318*S),radius=29*S,fill='black' if aod else '#bdc4b7')
    # Recessed LCD glass: dark inner lip and a soft shadow beneath the bezel.
    shadow=canvas(color=(0,0,0,0)); sd=ImageDraw.Draw(shadow)
    sd.rounded_rectangle((38*S,134*S,428*S,315*S),radius=27*S,outline=(40,49,37,115),width=5*S)
    if not aod:
        im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(3*S)))
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((35*S,131*S,431*S,318*S),radius=29*S,outline='#606859',width=S)
    if not aod:
        text(im,'BATT',(80,227),19,'#273025','Arial Narrow Bold Italic.ttf')
    text(im,'MODE',(93,345),19,'#f1f1ed','Arial Narrow Bold.ttf')
    text(im,'ALARM ON • OFF / 24HR',(287,345),19,'#f1f1ed','Arial Narrow.ttf',260)
    d.polygon([(43*S,345*S),(57*S,339*S),(57*S,351*S)],fill='#be5e36')
    d.line((53*S,363*S,172*S,363*S),fill='#2785a5',width=3*S)
    d.line((292*S,363*S,413*S,363*S),fill='#2785a5',width=3*S)
    text(im,'WATER',(115,386),23,'#eeeeeb','Arial Narrow Bold.ttf')
    text(im,'RESIST',(351,386),23,'#eeeeeb','Arial Narrow Bold.ttf')
    d.rounded_rectangle((180*S,364*S,284*S,414*S),radius=5*S,outline='#2785a5',width=2*S)
    text(im,'WR',(232,388),39,'#b95430','Arial Bold Italic.ttf')
    return ImageEnhance.Brightness(im).enhance(.25) if aod else im

SEGMENTS = ['abcdef','bc','abdeg','abcdg','bcfg','acdfg','acdefg','abc','abcdefg','abcdfg']
def digit(n, aod=False):
    im=canvas(72,130,(0,0,0,0)); d=ImageDraw.Draw(im)
    # All electrodes meet the same three rows and two columns. Matching
    # 45-degree mitres leave a small, consistent gap at every junction.
    half, gap = 8, 1.5
    left, right = 10, 54
    top, middle, bottom = 10, 65, 120
    def h(y):
        return [(left+gap,y),(left+half+gap,y-half),
                (right-half-gap,y-half),(right-gap,y),
                (right-half-gap,y+half),(left+half+gap,y+half)]
    def v(x,y1,y2):
        return [(x,y1+gap),(x+half,y1+half+gap),
                (x+half,y2-half-gap),(x,y2-gap),
                (x-half,y2-half-gap),(x-half,y1+half+gap)]
    polys={'a':h(top),'g':h(middle),'d':h(bottom),
           'f':v(left,top,middle),'b':v(right,top,middle),
           'e':v(left,middle,bottom),'c':v(right,middle,bottom)}
    polys={key:[(x+(130-y)*.045,y) for x,y in poly] for key,poly in polys.items()}
    if not aod:
        # Ghost electrodes remain visible when off, as on a passive LCD.
        for poly in polys.values():
            d.polygon([(round(x*S),round(y*S)) for x,y in poly],fill=(54,65,47,24))
        shadow=canvas(72,130,(0,0,0,0)); sd=ImageDraw.Draw(shadow)
        for key in SEGMENTS[n]:
            sd.polygon([(round((x+1.3)*S),round((y+1.8)*S)) for x,y in polys[key]],fill=(31,39,27,90))
        im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(.8*S)))
        d=ImageDraw.Draw(im)
    for key, poly in polys.items():
        if key in SEGMENTS[n]:
            d.polygon([(round(x*S),round(y*S)) for x,y in poly],fill='#61756b' if aod else '#17221c')
    return im

def time_digit(n,aod=False):
    im=digit(n,aod)
    return im.resize((64*S,126*S),Image.Resampling.LANCZOS)

def battery(value):
    # One indexed image for each actual percentage, so 0, 58 and 100 all fit.
    im=canvas(66,30,(0,0,0,0))
    s=str(value); width=len(s)*14+12; left=(66-width)//2
    for i,n in enumerate(s):
        im.alpha_composite(digit(int(n)).resize((14*S,26*S),Image.Resampling.LANCZOS),((left+i*14)*S,S))
    text(im,'%',(left+len(s)*14+6,19),14,'#17221c','Arial Narrow.ttf')
    return im

def bluetooth(connected):
    im=canvas(32,36,(0,0,0,0)); d=ImageDraw.Draw(im)
    color='#17221c' if connected else '#8a9483'
    points=[(8,10),(24,25),(16,32),(16,4),(24,11),(8,26)]
    d.line([(x*S,y*S) for x,y in points],fill=color,width=3*S,joint='curve')
    if not connected:
        d.line([(4*S,4*S),(28*S,32*S)],fill=color,width=2*S)
    return im

def date_label(value, width, aod=False):
    im=canvas(width,26,(0,0,0,0))
    text(im,value,(width/2,13),22,'#47564e' if aod else '#17221c','Courier New Bold.ttf')
    return im

def charging(active):
    im=canvas(18,24,(0,0,0,0))
    if active:
        ImageDraw.Draw(im).polygon([(11*S,1*S),(3*S,13*S),(8*S,13*S),
                                    (6*S,23*S),(16*S,9*S),(10*S,9*S)],fill='#17221c')
    return im

def make_project(aod=False):
    folder=OUT/'AOD' if aod else OUT
    images=folder/'images'; images.mkdir(parents=True,exist_ok=True)
    bg=background(aod)
    # Static colon, with no one-second wakeups.
    d=ImageDraw.Draw(bg)
    colon_x=263
    for y in (213,251):
        if not aod:
            d.rectangle(((colon_x+2)*S,(y+2)*S,(colon_x+9)*S,(y+10)*S),fill='#98a08e')
        d.rectangle((colon_x*S,y*S,(colon_x+7)*S,(y+8)*S),fill='#61756b' if aod else '#17221c')
    save(bg,images/'background.png')
    for n in range(10): save(time_digit(n,aod),images/f'digit{n}.png')
    if not aod:
        for value in range(101): save(battery(value),images/f'battery{value}.png')
        for state in (0,1): save(bluetooth(state),images/f'bluetooth{state}.png')
    weekdays=['SUN','MON','TUE','WED','THU','FRI','SAT']
    for i,label in enumerate(weekdays): save(date_label(label,60,aod),images/f'weekday{i}.png')
    for day in range(32): save(date_label(f'{day:02}',36,aod),images/f'day{day}.png')
    if not aod:
        for state in (0,1): save(charging(state),images/f'charging{state}.png')
    preview=bg.copy()
    preview.alpha_composite(date_label('SAT',60,aod),(205*S,138*S))
    preview.alpha_composite(date_label('17',36,aod),(275*S,138*S))
    positions=(125,193,278,346)
    y=172
    for n,x in zip((1,0,1,0),positions):
        preview.alpha_composite(time_digit(n,aod),(x*S,y*S))
    if not aod:
        preview.alpha_composite(battery(58),(47*S,243*S))
        offline=preview.copy()
        offline.alpha_composite(bluetooth(False),(64*S,174*S))
        save(offline,folder/'preview-disconnected.png')
        preview.alpha_composite(bluetooth(True),(64*S,174*S))
    if not aod:
        charging_preview=preview.copy()
        charging_preview.alpha_composite(charging(True),(71*S,281*S))
        save(charging_preview,folder/'preview-charging.png')
    save(preview,folder/'preview.png')
    preview.resize((246,246),Image.Resampling.LANCZOS).save(images/'preview.png')
    root=ET.Element('FaceProject',DeviceType='3',Id='1731859101')
    screen=ET.SubElement(root,'Screen',Title='Casio Time AOD' if aod else 'Casio Time',Bitmap='preview.png')
    ET.SubElement(screen,'Widget',Shape='30',Name='Background',Bitmap='background.png',X='0',Y='0',Width='466',Height='466',Alpha='255',Visible_Src='0')
    for (name,source),x in zip([('HourTens','1000911'),('HourUnits','0911'),('MinuteTens','1211'),('MinuteUnits','1111')],positions):
        ET.SubElement(screen,'Widget',Shape='32',Name=name,BitmapList='|'.join(f'digit{n}.png' for n in range(10)),X=str(x),Y=str(y),Width='64',Height='126',Alpha='255',Visible_Src='0',Digits='1',Alignment='0',Value_Src=source,Spacing='0',Blanking='0')
    if not aod:
        ET.SubElement(screen,'Widget',Shape='31',Name='BatteryPercent',BitmapList='|'.join(f'({v}):battery{v}.png' for v in range(101)),X='47',Y='243',Width='66',Height='30',Alpha='255',Visible_Src='0',Alignment='0',DefaultIndex='0',Index_Src='0841',Value_Src='0841',Spacing='0',Blanking='0')
        ET.SubElement(screen,'Widget',Shape='31',Name='BluetoothStatus',BitmapList='(0):bluetooth0.png|(1):bluetooth1.png',X='64',Y='174',Width='32',Height='36',Alpha='255',Visible_Src='0',Alignment='0',DefaultIndex='0',Index_Src='2041',Value_Src='2041',Spacing='0',Blanking='0')
    for name,prefix,count,src,x,width in [('Weekday','weekday',7,'2012',205,60),('Day','day',32,'1812',275,36)]:
        ET.SubElement(screen,'Widget',Shape='31',Name=name,BitmapList='|'.join(f'({v}):{prefix}{v}.png' for v in range(count)),X=str(x),Y='138',Width=str(width),Height='26',Alpha='255',Visible_Src='0',Alignment='0',DefaultIndex='0',Index_Src=src,Value_Src=src,Spacing='0',Blanking='0')
    if not aod:
        ET.SubElement(screen,'Widget',Shape='31',Name='Charging',BitmapList='(0):charging0.png|(1):charging1.png',X='71',Y='281',Width='18',Height='24',Alpha='255',Visible_Src='0',Alignment='0',DefaultIndex='0',Index_Src='1041',Value_Src='1041',Spacing='0',Blanking='0')
    ET.indent(root)
    ET.ElementTree(root).write(folder/('AOD.fprj' if aod else 'CasioTime.fprj'),encoding='utf-8',xml_declaration=True)
    return preview.resize((466,466),Image.Resampling.LANCZOS)

if __name__=='__main__':
    normal=make_project(); aod=make_project(True)
    sheet=Image.new('RGB',(972,526),'#121719')
    sheet.paste(Image.open(OUT/'preview-charging.png'),(10,10)); sheet.paste(aod,(496,10))
    d=ImageDraw.Draw(sheet); f=ImageFont.truetype(str(FONT/'Arial.ttf'),18)
    d.text((243,495),'NORMAL · CHARGING',font=f,anchor='mm',fill='#c4cdce')
    d.text((729,495),'ALWAYS ON',font=f,anchor='mm',fill='#c4cdce')
    sheet.save(OUT/'preview-pair.png')
    sheet.paste(Image.open(OUT/'preview-disconnected.png'),(496,10))
    d.rectangle((0,477,972,526),fill='#121719')
    d.text((243,495),'BLUETOOTH CONNECTED',font=f,anchor='mm',fill='#c4cdce')
    d.text((729,495),'DISCONNECTED',font=f,anchor='mm',fill='#c4cdce')
    sheet.save(OUT/'preview-bluetooth.png')
    print(OUT)
