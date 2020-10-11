import glfw
import glm
import math


class Camera:
    'A camera in a 3D environment.'
    position = glm.vec3([0.0, 0.0, 1000.0])
    look_direction = glm.vec3([0.0, 0.0, -1.0])
    up_direction = glm.vec3([0.0, 1.0, 0.0])
    right_direction = glm.vec3([1.0, 0.0, 0.0])
    yaw = 0.0
    pitch = 0.0

    speed = None
    mouse_sensitivity = 0.08

    def __init__(self, speed):
        self.speed = speed

    def get_position(self):
        return self.position

    def get_look_direction(self):
        return self.look_direction

    def get_up_direction(self):
        return self.up_direction

    def get_right_direction(self):
        return self.right_direction

    def get_keys(self):
        return [glfw.KEY_W, glfw.KEY_A, glfw.KEY_S, glfw.KEY_D]

    def handle_keyboard(self, key):

        if key == glfw.KEY_W:
            self.position += self.look_direction * self.speed
        elif key == glfw.KEY_A:
            self.position -= self.right_direction * self.speed
        elif key == glfw.KEY_S:
            self.position -= self.look_direction * self.speed
        elif key == glfw.KEY_D:
            self.position += self.right_direction * self.speed

    def handle_mouse(self, x_offset, y_offset):

        self.yaw += x_offset * self.mouse_sensitivity
        self.pitch += y_offset * self.mouse_sensitivity

        # make sure that when pitch is out of bounds, screen doesn't get flipped
        self.pitch = glm.clamp(self.pitch, -89, 89)

        # update Front, Right and Up Vectors using the updated Euler angles
        self.__update_camera_vectors()

    def __update_camera_vectors(self):
        # calculate the new Front vector
        self.look_direction.x = math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        self.look_direction.y = math.sin(glm.radians(self.pitch))
        self.look_direction.z = math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        self.look_direction = glm.normalize(self.look_direction)
        self.right_direction = glm.normalize(glm.cross(self.look_direction, self.up_direction))
        self.up_direction = glm.normalize(glm.cross(self.right_direction, self.look_direction))
