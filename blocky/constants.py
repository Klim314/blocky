import os, sys

blocky_dir = os.path.normpath(os.path.join(__file__, "../"))
units_path = os.path.join(blocky_dir, "data/units.yaml")
test_dir = os.path.normpath(os.path.join(__file__, "../../tests"))
units_path = os.path.join(blocky_dir, "data/units.yaml")

if __name__ == "__main__":
    print(blocky_dir, test_dir)
