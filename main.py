import re
import os

class GCodeChecker:
    def __init__(self, filename):
        self.filename = filename
        self.errors = []
        self.warnings = []

    def run_check(self):
        if not os.path.exists(self.filename):
            print(f"Error: file {self.filename} not found")
            return

        with open(self.filename, 'r') as f:
            lines = f.readlines()

        has_s = False
        has_f = False

        for idx, line in enumerate(lines, 1):
            cleaned = line.strip().upper()
            if not cleaned or cleaned.startswith('('):
                continue # skip blank lines and comments

            # check spindle and feed
            if 'S' in cleaned: has_s = True
            if 'F' in cleaned: has_f = True

            # dangerous G00 check
            if 'G00' in cleaned or 'G0' in cleaned:
                z_find = re.search(r'Z(-?\d+\.?\d*)', cleaned)
                if z_find:
                    z_val = float(z_find.group(1))
                    if z_val < 2.0:
                        self.warnings.append(f"Line {idx}: G00 Z is too low ({z_val}mm)! Risk of collision.")

            # cutting without speed check
            if any(g in cleaned for g in ['G01', 'G1', 'G02', 'G2', 'G03', 'G3']):
                if not has_s:
                    self.errors.append(f"Line {idx}: Cutting command found but spindle speed (S) not set yet.")
                if not has_f:
                    self.errors.append(f"Line {idx}: Cutting command found but feed rate (F) not set yet.")

        return self.errors, self.warnings

if __name__ == "__main__":
    # TODO: replace with real test file path later
    test_file = "test.nc"
    print("--- Starting G-Code Safety Analyzer ---")
    checker = GCodeChecker(test_file)
    print("Done checking.")
