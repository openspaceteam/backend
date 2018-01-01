import random
import json

from json import JSONEncoder

from constants import layout_cells

NORMAL = 0
BIG_CELLS = 1


class GridJSONEncoder(JSONEncoder):
    def default(self, o):
        if hasattr(o, "__dict__"):
            return o.__dict__()
        return JSONEncoder.default(self, o)


class GridElement:
    def __init__(self, name, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.name = name

    def __dict__(self):
        _dict = {
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "name": self.name,
        }
        if type(self) in TYPES:
            _dict["type"] = TYPES[type(self)]
        return _dict


class SliderLikeElement(GridElement):
    def __init__(self, name, x, y, w, h, min_value, max_value):
        super(SliderLikeElement, self).__init__(name, x, y, w, h)
        self.min = min_value
        self.max = max_value
        self.value = self.min

    def __dict__(self):
        return {
            **super(SliderLikeElement, self).__dict__(),
            **{
                "min": self.min,
                "max": self.max
            }
        }


class Button(GridElement):
    pass


class Slider(SliderLikeElement):
    pass


class CircularSlider(SliderLikeElement):
    pass


class ButtonsSlider(SliderLikeElement):
    pass


class Actions(GridElement):
    def __init__(self, name, x, y, w, h, actions):
        super(Actions, self).__init__(name, x, y, w, h)
        self.actions = actions

    def __dict__(self):
        return {
            **super(Actions, self).__dict__(),
            **{
                "actions": self.actions
            }
        }


class Switch(GridElement):
    def __init__(self, name, x, y, w, h):
        super(Switch, self).__init__(name, x, y, w, h)
        self.toggled = False

TYPES = {
    Button: "button",
    Slider: "slider",
    CircularSlider: "circular_slider",
    Actions: "actions",
    ButtonsSlider: "buttons_slider",
    Switch: "switch"
}


# we will be using a y,x coordinate system;
# because we're making this for italians not japs:
# so they will be looking at our grid left to right first,
# top to bottom after that.
class Grid:
    def __init__(self, command_name_generator, pool_config=NORMAL):
        self.grid = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        self.objects = []
        self.command_name_generator = command_name_generator

        while True:
            print(self.grid)
            y, x = self.get_next_empty()
            if y < 0 and x < 0:
                break
            print("next empties are: %s, %s" % (y, x))
            self.add_random_element(y, x)

    def get_next_empty(self):
        for y in range(4):
            for x in range(4):
                if self.grid[y][x] == layout_cells.EMPTY:
                    return y, x
        return -1, -1

    def add_random_element(self, y, x):
        fsr = self.free_space_right(y, x)

        print("for %s, %s; there's %s spaces to the right." % (y, x, fsr))

        if fsr == 1:
            # No space left on x axis, only Squares and VerticalRectangles allowed
            pool = [layout_cells.SQUARE, layout_cells.VERTICAL_RECTANGLE]
        else:
            # More space, everything can fit
            pool = [
                layout_cells.SQUARE, layout_cells.VERTICAL_RECTANGLE,
                layout_cells.HORIZONTAL_RECTANGLE, layout_cells.BIG_SQUARE
            ]

        # Remove elements already present in that row
        # for element in self.grid[y]:
        #     pool = list(filter(lambda z: z != element, pool))

        if y == 3:
            # No space left on y axis, remove VerticalRectangles and BigSquares from pool
            pool = list(filter(lambda z: z not in [layout_cells.VERTICAL_RECTANGLE, layout_cells.BIG_SQUARE], pool))

        # Default size is 1
        length = 1

        # pick something from the pool, or if nothing's left pick a square
        _type = random.choice(pool) if len(pool) != 0 else layout_cells.SQUARE
        print("we picked to insert a type %s object there" % _type)

        # if fsr is > 2 and you picked a horizontalrectangle, decide how long it will be.
        if _type == layout_cells.HORIZONTAL_RECTANGLE:
            if fsr > 2:
                length = random.randint(2, 3)
            else:
                length = 2

        # if you picked a verticalrectangle, decide how long it will be.
        if _type == layout_cells.VERTICAL_RECTANGLE:
            if y <= 1:
                length = random.randint(2, 3)
            else:
                length = 2

        # if you picked a bigsquare, decide how big it will be.
        if _type == layout_cells.BIG_SQUARE:
            if y <= 1 and fsr >= 1 and x <= 1:
                length = random.randint(2, 3)
            else:
                length = 2

        print("and the length will be %s" % length)

        # insert the object
        self.insert_object(y, x, _type, length)

    def insert_object(self, y, x, _type, length):
        print("inserting a _type %s object of length %s to %s, %s" % (_type, length, y, x))

        # Only the
        self.grid[y][x] = _type

        if length != 1:
            if _type == layout_cells.VERTICAL_RECTANGLE:
                for i in range(y + 1, y + length):
                    self.grid[i][x] = layout_cells.OCCUPIED
            elif _type == layout_cells.HORIZONTAL_RECTANGLE:
                for i in range(x + 1, x + length):
                    self.grid[y][i] = layout_cells.OCCUPIED
            elif _type == layout_cells.BIG_SQUARE:
                self.grid[y + 1][x] = layout_cells.BIG_SQUARE
                self.grid[y][x + 1] = layout_cells.BIG_SQUARE
                self.grid[y + 1][x + 1] = layout_cells.BIG_SQUARE
                if length == 3:
                    for i in range(3):
                        self.grid[y + 2][x + i] = layout_cells.BIG_SQUARE
                    for i in range(3):
                        self.grid[y + i][x + 2] = layout_cells.BIG_SQUARE

        pool = []
        if _type in [layout_cells.SQUARE, layout_cells.BIG_SQUARE]:
            pool.append(Button)
            pool.append(Switch)
        if _type == layout_cells.VERTICAL_RECTANGLE and length == 2:
            for _ in range(2):
                pool.append(Actions)
        if _type in [layout_cells.VERTICAL_RECTANGLE, layout_cells.HORIZONTAL_RECTANGLE]:
            pool.append(Slider)
        if _type == layout_cells.BIG_SQUARE:
            for _ in range(3):
                pool.append(CircularSlider)
        if _type == layout_cells.HORIZONTAL_RECTANGLE:
            for _ in range(2):
                pool.append(ButtonsSlider)

        _object = random.choice(pool)

        init_kwargs = {
            "x": x,
            "y": y,
            "w": 1,
            "h": 1,
            "name": self.command_name_generator.generate_command_name()
        }

        if _type == layout_cells.VERTICAL_RECTANGLE:
            # Special size for vertical rectangle
            init_kwargs["w"] = 1
            init_kwargs["h"] = length
        elif _type == layout_cells.HORIZONTAL_RECTANGLE:
            # Special size for horizontal rectangle
            init_kwargs["w"] = length
            init_kwargs["h"] = 1
        elif _type == layout_cells.BIG_SQUARE:
            # Special size for big square rectangle
            init_kwargs["w"] = length
            init_kwargs["h"] = length

        if _object in [Slider, ButtonsSlider]:
            # Special kwargs for Sliders
            init_kwargs["min_value"] = 0
            init_kwargs["max_value"] = random.randint(3, 5)
        elif _object is CircularSlider:
            # Special kwargs for Sliders (different values)
            init_kwargs["min_value"] = 0
            init_kwargs["max_value"] = random.randint(4, 7)
        elif _object is Actions:
            # Special kwargs for Action
            init_kwargs["actions"] = [
                self.command_name_generator.generate_action() for _ in range(random.randint(2, 4))
            ]

        self.objects.append(_object(**init_kwargs))

    def free_space_right(self, y, x):
        cnt = 0
        for i in range(x, 4):
            if self.grid[y][i] != layout_cells.EMPTY:
                return cnt
            cnt += 1
        return cnt

    def jsonify(self):
        return json.dumps(self.objects, cls=GridJSONEncoder)

    def __dict__(self):
        result = []
        for i in self.objects:
            result.append(i.__dict__())
        return result

# if __name__ == "__main__":
#     print(Grid().jsonify())
