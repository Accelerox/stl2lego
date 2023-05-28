# STL2Lego

Python code for converting a STL to a Lego version.

### Output
- A numpy voxel array in where bricks are to be places layer by layer
- This voxel array can be sent to Catia via Visual Basic to be instantiated.

## Features
- Choose size of Lego resolution.
- Choose what brick sizes can be used.
- Tries to minimize the number of bricks.

## Installation
```
pip3 install -r requirements.txt
```
```
python3 stl2lego.py
```

## Authors
- Mats Gard & Max Idermark

## Known bugs
- Sometimes floating (non supported) lego parts can occur.