class Sphere:
    'Sphere object that can be raytraced'
    position = None
    radius = None
    color = None
    opacity = None


    def __init__(self, position, radius, color, opacity):
        self.position = position
        self.radius = radius
        self.color = color
        self.opacity = opacity

    def get_position(self):
        return self.position

    def set_position(self, new_position):
        self.position = new_position

    def get_radius(self):
        return self.radius

    def set_radius(self, new_radius):
        self.radius = new_radius

    def get_color(self):
        return self.color

    def get_opacity(self):
        return self.opacity