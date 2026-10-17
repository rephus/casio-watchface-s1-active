#!/usr/bin/env python3
"""Validate the Gen2 container and assemble personal installation/source files."""
from pathlib import Path
import hashlib
import json
import struct
import zipfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'watchfaces/casio-time'
DIST=ROOT/'dist'
FACE_ID='917101703'

data=bytearray((PROJECT/'output/CasioTime.face').read_bytes())
assert data[:4]==bytes.fromhex('5aa53412'), 'Not a Xiaomi Gen2 watch face'
assert data[0x1c]==2, 'Expected normal and AOD layouts'
assert 168 < struct.unpack_from('<I',data,0x20)[0] < len(data), 'Invalid preview offset'
# This nine-byte ASCII ID field is also used by Mi Create's WatchfaceBinary.setId.
assert data[40:49].isdigit(), 'Unexpected face ID layout'
data[40:49]=FACE_ID.encode('ascii')
DIST.mkdir(exist_ok=True)
name='casio-time-s1-active-v4'
binary=DIST/(name+'.bin'); binary.write_bytes(data)
with zipfile.ZipFile(DIST/(name+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('CasioTime.bin',data)
    z.writestr('description.xml',f'<?xml version="1.0" encoding="UTF-8"?><watchface><pkgName>{FACE_ID}</pkgName><title>Casio Time</title></watchface>')
    z.write(PROJECT/'preview.png','preview.png')
with zipfile.ZipFile(DIST/(name+'-source.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for folder in (PROJECT,PROJECT/'AOD'):
        for p in sorted(folder.glob('*.fprj'))+sorted((folder/'images').glob('*.png')):
            z.write(p,str(p.relative_to(ROOT)))
    for p in ('build-casio-face.py','compile-casio-face.sh','package-casio-face.py'):
        z.write(ROOT/'scripts'/p,'scripts/'+p)
for folder in (PROJECT,PROJECT/'AOD'):
    tree=ET.parse(next(folder.glob('*.fprj')))
    nums=tree.findall('.//Widget[@Shape="32"]')
    assert [n.get('Value_Src') for n in nums]==['1000911','0911','1211','1111']
    assert all(n.get('Digits')=='1' for n in nums)
    for n in nums:
        assert all((folder/'images'/p).exists() for p in n.get('BitmapList').split('|'))
    battery=tree.findall('.//Widget[@Value_Src="0841"]')
    assert len(battery)==(0 if folder.name=='AOD' else 1)
    for widget in battery:
        frames=[entry.split(':',1)[1] for entry in widget.get('BitmapList').split('|')]
        assert len(frames)==101
        assert all((folder/'images'/p).exists() for p in frames)
report={'target':'Xiaomi S1 / Color 2 Gen2, 466x466','compiler':'m0tral EasyFace v4.23',
        'face_id':FACE_ID,'slots':2,'display':'24-hour HH:MM, weekday/date, battery, Bluetooth and charging; dim Casio AOD with date',
        'physical_watch_verified':False,'transfer_verified':False,
        'compiler_source':'https://github.com/m0tral/EasyFace/releases/tag/v4.23',
        'project_format_source':'https://github.com/ooflet/Mi-Create/tree/d7aa9e682d43a2454363dbaaba809125901f7b06',
        'artifacts':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                     for p in [binary,DIST/(name+'.zip'),DIST/(name+'-source.zip')]}}
(DIST/(name+'-build.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
