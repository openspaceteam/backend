import random
import json

from json import JSONEncoder

Empty = 0
Occupied = 1
Square = 2
VerticalRectangle = 3
HorizontalRectangle = 4
BigSquare = 5

NORMAL = 0
BIG_CELLS = 1


class GridJSONEncoder(JSONEncoder):
    def default(self, o):
        if hasattr(o, "__dict__"):
            return o.__dict__()
        return JSONEncoder.default(self, o)


class GridElement:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.name = "mem!"

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
    def __init__(self, x, y, w, h, min_value, max_value):
        super(SliderLikeElement, self).__init__(x, y, w, h)
        self.min = min_value
        self.max = max_value

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
    def __init__(self, x, y, w, h, actions_number=3):
        super(Actions, self).__init__(x, y, w, h)
        self.actions = []
        for _ in range(actions_number):
            self.actions.append("becco")

    def __dict__(self):
        return {
            **super(Actions, self).__dict__(),
            **{
                "actions": self.actions
            }
        }


class Switch(GridElement):
    pass

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
    def __init__(self, pool_config=NORMAL):
        self.grid = [
            [Empty, Empty, Empty, Empty],
            [Empty, Empty, Empty, Empty],
            [Empty, Empty, Empty, Empty],
            [Empty, Empty, Empty, Empty]
        ]

        self.objects = []

        while True:
            try:
                y, x = self.get_next_empty()
            except TypeError:
                break
            print("next empties are: %s, %s" % (y, x))
            self.add_random_element(y, x)

    def get_next_empty(self):
        for y in range(4):
            for x in range(4):
                if self.grid[y][x] == Empty:
                    return y, x
        return False

    def add_random_element(self, y, x):
        fsr = self.free_space_right(y, x)

        print("for %s, %s; there's %s spaces to the right." % (y, x, fsr))

        if fsr == 1:
            # No space left on x axis, only Squares and VerticalRectangles allowed
            pool = [Square, VerticalRectangle]
        else:
            # More space, everything can fit
            pool = [Square, VerticalRectangle, HorizontalRectangle, BigSquare]

        # Remove elements already present in that row
        # for element in self.grid[y]:
        #     pool = list(filter(lambda z: z != element, pool))

        if y == 3:
            # No space left on y axis, remove VerticalRectangles and BigSquares from pool
            pool = list(filter(lambda z: z not in [VerticalRectangle, BigSquare], pool))

        # Default size is 1
        length = 1

        # pick something from the pool, or if nothing's left pick a square
        _type = random.choice(pool) if len(pool) != 0 else Square
        print("we picked to insert a type %s object there" % _type)

        # if fsr is > 2 and you picked a horizontalrectangle, decide how long it will be.
        if _type == HorizontalRectangle:
            if fsr > 2:
                length = random.randint(2, 3)
            else:
                length = 2

        # if you picked a verticalrectangle, decide how long it will be.
        if _type == VerticalRectangle:
            if y <= 1:
                length = random.randint(2, 3)
            else:
                length = 2

        # if you picked a bigsquare, decide how big it will be.
        if _type == BigSquare:
            if y <= 1 and x <= 1:
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
            if _type == VerticalRectangle:
                for i in range(y + 1, y + length):
                    self.grid[i][x] = Occupied
            elif _type == HorizontalRectangle:
                for i in range(x + 1, x + length):
                    self.grid[y][i] = Occupied
            elif _type == BigSquare:
                self.grid[y + 1][x] = BigSquare
                self.grid[y][x + 1] = BigSquare
                self.grid[y + 1][x + 1] = BigSquare

        pool = []
        if _type in [Square, BigSquare]:
            pool.append(Button)
            pool.append(Switch)
        if _type == VerticalRectangle and length == 2:
            for _ in range(2):
                pool.append(Actions)
        if _type in [VerticalRectangle, HorizontalRectangle]:
            pool.append(Slider)
        if _type == BigSquare:
            for _ in range(3):
                pool.append(CircularSlider)
        if _type == HorizontalRectangle:
            for _ in range(2):
                pool.append(ButtonsSlider)

        _object = random.choice(pool)

        init_kwargs = {
            "x": x,
            "y": y,
            "w": 1,
            "h": 1
        }

        if _type == VerticalRectangle:
            # Special size for vertical rectangle
            init_kwargs["w"] = 1
            init_kwargs["h"] = length
        elif _type == HorizontalRectangle:
            # Special size for horizontal rectangle
            init_kwargs["w"] = length
            init_kwargs["h"] = 1
        elif _type == BigSquare:
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
            init_kwargs["actions_number"] = random.randint(1, 3)

        self.objects.append(_object(**init_kwargs))

    def free_space_right(self, y, x):
        cnt = 0
        for i in range(x, 4):
            if self.grid[y][i] != Empty:
                return cnt
            cnt += 1
        return cnt

    def jsonify(self):
        return json.dumps(self.objects, cls=GridJSONEncoder)

if __name__ == "__main__":
    print(Grid().jsonify())
