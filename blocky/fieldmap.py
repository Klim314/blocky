"""
Initial code for a 3d tile space with individual cells
"""
import yaml
import logging

from heapdict import heapdict
# from blocky.custom_exceptions import IllegalActionException


class Zone:
    """Overall 3d voxel tactical zone for object placement

        Attributes
    """
    def __init__(self):
        self.dims = (0, 0, 0)
        self.contents = [[[]]]

    # Properties
    @property
    def x_len(self):
        return self.dims[0]

    @property
    def y_len(self):
        return self.dims[1]

    @property
    def z_len(self):
        return self.dims[2]

    # Various initialization tools
    def load_cells(self, cell_anns, cell_matrix):
        """Loads cells given from a cell matrix and cell data annotations
        Arguments:
            cell_anns: Dict. keys = cell codes, item = cell properties
            cell_matrix: 3D list matrix containing cell codes for each cell
        """
        # Dimensions of map in XYZ coordinates
        self.dims = (len(cell_matrix[0][0]), len(cell_matrix[0]), len(cell_matrix))
        if any(i == 0 for i in self.dims):
            raise
        self.contents = [[[None for i in range(self.dims[0])] for j in range(self.dims[1])] for k in range(self.dims[2])]
        for z, plane in enumerate(cell_matrix):
            for y, row in enumerate(plane):
                for x, cell_type in enumerate(row):
                    if not cell_type:
                        cell_type = "v"
                    cell_ann = cell_anns[cell_type]
                    self.contents[z][y][x] = Cell(self,
                                                  None,
                                                  x,
                                                  y,
                                                  z,
                                                  cell_ann["name"],
                                                  cell_ann["properties"],
                                                  cell_type=cell_type)
        return 0

    def load_map(self, cell_anns, map_path):
        """Loads the cell data from a given map path
        """
        def load_plane(plane_string):
            temp = plane_string.split("\n")
            plane_cell_data = [i.split(",") for i in temp]
            return plane_cell_data

        with open(map_path) as f:
            total = f.read().strip()
            planes = total.split("\n\n")
            cell_data = [load_plane(plane) for plane in planes]
        logging.debug((cell_anns, cell_data))
        return self.load_cells(cell_anns, cell_data)

    def check_coords(self, x, y, z):
        """
        Determines if a seet of coordinates are contained within the zone
        """
        for coord, dim in zip((x, y, z), self.dims):
            if coord < 0 or coord >= dim:
                # logging.debug(((x, y, z), self.dims, coord, dim))
                return False
        return True

    def check_empty_at(self, x, y, z):
        return not self.get_cell(x, y, z).has_unit()

    def print_all_planes(self):
        for layer, plane in enumerate(self.contents):
            print("{}:".format(layer))
            print()
            print("\n".join(["".join([cell.cell_type for cell in row]) for row in plane]))
            print()
        return 0

    def get_cell(self, x, y, z):
        if not self.check_coords(x, y, z):
            raise Exception("Illegal coordinates provided")
        return self.contents[z][y][x]

    def get_unit(self, x, y, z):
        if not self.check_coords(x, y, z):
            raise Exception("Illegal coordinates provided")
        return self.contents[z][y][x].contents

    def get_neighbours(self, x, y, z, filters={}):
        """ gets the neighbouring cells of a cell in coordinates of x, y and z        
        args:
            x, y, z: int. Coordiates 
            filters
        returns:
            list of cell objects

        """
        # for coord_id, coord, dim in zip("xyz",
        #                                 (x, y, z),
        #                                 self.dims):
        #     print(coord_id, coord, dim)

        if any(coord > dim or coord < 0 for coord_id, coord, dim in zip("xyz",
                                                                        (x, y, z),
                                                                        self.dims)):
            raise Exception("coord {} = {} illegal in zone of dimensions ({}, {}, {})")
        neighbours = []

        # Generate all the possible direct neighbours (only one index changes by 1)
        for index in range(3):
            # Search +1/-1 indices around the source
            for val in (1, -1):
                temp = [x, y, z]
                temp[index] = temp[index] + val
                temp = tuple(temp)
                # print(temp, self.check_coords(*temp))
                if self.check_coords(*temp):
                    cell = self.get_cell(*temp)
                    if cell.filter(filters):
                        neighbours.append(cell)
        return neighbours

    def add_entity(self, entity, x, y, z):
        if not self.check_empty_at(x, y, z):
            raise Exception("Attempted to add entity to non-empty cell")
        else:
            self.get_cell(x, y, z).contents = entity
        return 0




class Cell:
    """Cell represnting single voxel cell in 3d space

    Attributes:
        properties: Dict. Individual properties of the given cell (Passable, etc)
        sprite: Sprite object to use for rendering
    """
    def __init__(self, parent, sprite, x, y, z, name, properties, cell_type=None):
        self.parent = parent
        self.sprite = sprite
        self.default_properties = properties
        self.mod_properties = set()
        self.pos = (x, y, z)
        self.cell_type = cell_type

        # Units in cell
        self.contents = None

        # General stuff for the pathfinding
        self.prev = None
        self.lowest_cost = 9999999999

    # Properties
    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    @property
    def z(self):
        return self.pos[2]

    @property
    def properties(self):
        return self.default_properties

    def __repr__(self):
        return "<Cell: {} at ({}, {}, {})>".format(self.cell_type, self.x, self.y, self.z)

    def has_unit(self):
        return bool(self.contents)

    def get_neighbours(self, filters={}):
        return self.parent.get_neighbours(self.x, self.y, self.z, filters=filters)

    def filter(self, filters):
        for key, item in filters.items():
            if key not in self.properties or self.properties[key] != item:
                return False
        return True

def pathfind(zone, start, end, filters={"passable": True}):
    """
    Performs a pathfinding search from start cell in zone to end cell in zone using
    dijkstra's algorithm
    args:
        zone
        start: tuple. (x, y, z) in ints. Start cell
        end: tuple. (x, y, z) in ints. End cell
        moves: int. Number of movement points
    """
    # Visited nodes
    visited = set()
    pq = heapdict()
    cell = zone.get_cell(*start)
    pq[cell.pos] = 0 

    while pq:
        cur, cur_pri = pq.popitem()
        cur = zone.get_cell(*cur)
        if cur.pos == end:
            break

        # Get all unvisited passable neighbours and check if they
        neighbours = cur.get_neighbours(filters=filters)
        # print("NEIGH:", cur, neighbours)
        # sleep(0.5)
        for next_cell in neighbours:
            if next_cell.pos in visited:
                continue
            # Calculate the cost of reaching the cell
            next_cost = cur_pri + next_cell.properties["move_cost"]
            # Handle backtrace
            if next_cell.prev is None or next_cost < next_cell.lowest_cost:
                pq[next_cell.pos] = next_cost
                next_cell.prev = cur
        visited.add(cur.pos)
        # print([i for i in pq.items()])
    # print("VISITED:", visited)

    # Backtrack and recover the path
    res = []
    counter = 0
    while cur:
        counter += 1
        if counter > 100:
            raise
        res.append(cur.pos)
        print(cur, cur.prev)
        cur = cur.prev

    # Cleanup the nodes and prepare for future pathfinds
    for coords in visited:
        cell = zone.get_cell(*coords)
        cell.prev = None
    return res


# Modify for flyers, etc
def get_path_cost(zone, path):
    pass


if __name__ == "__main__":
    with open("data/map_ann.yaml") as f:
        map_ann = yaml.load(f)

    sample_zone = [[["g", "g", "g", "g"],
                     ["a", "a", "g", "g"],
                     ["g", "g", "g", "g"]]]

    zone = Zone()
    zone.load_cells(map_ann, sample_zone)
    zone.print_all_planes()
    cell = zone.get_cell(1, 1, 0)
    print(cell)
    print(cell.get_neighbours())
    print(cell.get_neighbours(filters = {"passable": True}))
    print(pathfind(zone, (0, 0, 0), (0, 2, 0)))
