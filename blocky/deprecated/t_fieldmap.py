from fieldmap import Zone
import yaml


with open("data/map_ann.yaml") as f:
    map_ann = yaml.load(f)
print(map_ann)

# Check basic loading of 2d map (1 layer)
target = "data/maps/map1.map"
zone = Zone()
zone.load_map(map_ann, target)
zone.print_all_planes()
assert(zone.get_cell(0, 0, 0).cell_type == "g")
assert(zone.get_cell(0, 1, 0).cell_type == "a")
assert(zone.dims == (5, 3, 1))

# Check basic loading of 3d map (2 layer)
target = "data/maps/map2_3d.map"
zone = Zone()
zone.load_map(map_ann, target)
zone.print_all_planes()
assert(zone.get_cell(0, 0, 0).cell_type == "g")
assert(zone.get_cell(0, 1, 0).cell_type == "a")
assert(zone.get_cell(0, 0, 1).cell_type == "a")
assert(zone.dims == (5, 3, 2))
