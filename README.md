# fbm-gcode-safety-analyzer

Just a small script I wrote for my thesis research. I'm working on 2.5D Feature-Based Machining (FBM) and deep learning. 

The main goal here is to do some basic geometric rule checking and safety analysis on the generated G-code before throwing it into the machine, mostly because I want to prevent crash/collisions during testing.

## What it does now:
* Checks G00 rapid movements (warns me if Z axis goes too low, currently set threshold at 2.0mm to avoid crashes).
* Checks if G01/G02/G03 cutting commands have Spindle speed (S) and Feed rate (F) defined. It throws an error if missing.

## How to run
I'm using Python 3.10, no extra packages needed for now.
```bash
python main.py
```

## TODO / Next steps (For my thesis)
- [ ] Connect this parser with my PyTorch feature extraction model outputs
- [ ] Add support for Siemens/Heidenhain macros (right now it only handles basic Fanuc style)
- [ ] Fix some regex bugs when parsing files with heavy comments
