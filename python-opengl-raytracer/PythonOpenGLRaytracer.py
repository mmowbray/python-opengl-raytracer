from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import glfw
import glm
import random

from Camera import Camera
from Sphere import Sphere


class PythonOpenGLRaytracer:
    window_size = [1920, 1080]
    window = None

    spheres = list(range(50))
    lights = list(range(5))
    camera = Camera(30.0)

    first_mouse = True
    last_x = -1
    last_y = -1
    raytracing_max_bounces = 3

    def init_spheres(self):
        for s in range(len(self.spheres)):
            random_position = glm.vec3([random.random() - 0.5, random.random() - 0.5, random.random() - 0.5]) * 7500.0
            random_radius = 200 + (800 * random.random())
            random_color = glm.vec3([random.random(), random.random(), random.random()])
            random_opacity = random.random()
            self.spheres[s] = (Sphere(random_position, random_radius, random_color, random_opacity))

    def window_resize_callback(self, window, width, height):
        glViewport(0, 0, width, height)
        self.window_size[:] = width, height

    def key_callback(self, window, key, scancode, action, mods):

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

        elif key in self.camera.get_keys():
            self.camera.handle_keyboard(key)
        elif key == glfw.KEY_SPACE and action == glfw.PRESS:
            self.init_spheres()
            self.init_lights()
            self.init_polygons()

            glClearColor(random.random(), random.random(), random.random(), 1.0)

        elif action == glfw.PRESS and (key == glfw.KEY_KP_ADD or key == glfw.KEY_KP_SUBTRACT):
            if (key == glfw.KEY_KP_ADD):
                self.raytracing_max_bounces += 1
            else:
                self.raytracing_max_bounces -= 1

            self.raytracing_max_bounces = int(glm.clamp(self.raytracing_max_bounces, 0, 10))

    def update_sphere_positions(self):
        for idx, sphere in enumerate(self.spheres):
            if (idx % 2 == 0):
                new_sphere_position = glm.vec3(
                    glm.rotate(glm.mat4(1.0), 0.00090, glm.vec3(0.0, 1.0, 0.5)) * glm.vec4(sphere.get_position(),
                                                                                           1.0))
            elif (idx % 3 == 0):
                new_sphere_position = glm.vec3(
                    glm.rotate(glm.mat4(1.0), 0.00110, glm.vec3(0.5, 1.0, 1.0)) * glm.vec4(sphere.get_position(),
                                                                                           1.0))
            else:
                new_sphere_position = glm.vec3(
                    glm.rotate(glm.mat4(1.0), -0.00250, glm.vec3(1.0, 1.0, 0.0)) * glm.vec4(sphere.get_position(),
                                                                                            1.0))
            sphere.set_position(new_sphere_position)
            sphere.set_radius(sphere.get_radius() * 1.0 + ((random.random() - 0.5) / 50.0))

    def run(self):
        if not glfw.init():
            return

        self.window = glfw.create_window(self.window_size[0], self.window_size[1], "Python Opengl Raytracer", None,
                                         None)

        if not self.window:
            glfw.terminate()
            return

        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_window_size_callback(self.window, self.window_resize_callback)

        glfw.make_context_current(self.window)

        full_screen = np.array([-1.0, -1.0, 0.0,
                                -1.0, 1.0, 0.0,
                                1.0, 1.0, 0.0,
                                1.0, -1.0, 0.0], dtype=np.float32)

        PASS_THROUGH_FRAGMENT_SHADER = open("shaders/pass_through.vert", "r").read()
        SPHERE_RAY_TRACER_FRAGMENT_SHADER = open("shaders/sphere_ray_tracer.frag", "r").read()

        sphere_ray_tracer_shader_program = None

        try:

            sphere_ray_tracer_shader_program = OpenGL.GL.shaders.compileProgram(
                OpenGL.GL.shaders.compileShader(PASS_THROUGH_FRAGMENT_SHADER, GL_VERTEX_SHADER),
                OpenGL.GL.shaders.compileShader(SPHERE_RAY_TRACER_FRAGMENT_SHADER, GL_FRAGMENT_SHADER))
        except OpenGL.GL.shaders.ShaderCompilationError as e:
            print(str(e.args[0]).replace("\\n", '\n').replace(": 0:", " line "))
            return

        # Create Buffer object in gpu
        quad_VBO = glGenBuffers(1)

        # Bind the buffer
        glBindBuffer(GL_ARRAY_BUFFER, quad_VBO)
        glBufferData(GL_ARRAY_BUFFER, 48, full_screen, GL_STATIC_DRAW)

        position = glGetAttribLocation(sphere_ray_tracer_shader_program, 'position')
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(position)
        glUseProgram(sphere_ray_tracer_shader_program)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.3, 0.3, 0.3, 1.0)

        self.init_spheres()

        camera_position_loc = glGetUniformLocation(sphere_ray_tracer_shader_program, "camera_position")
        camera_look_direction_normalized_loc = glGetUniformLocation(sphere_ray_tracer_shader_program,
                                                                    "camera_look_direction_normalized")
        camera_up_direction_normalized_loc = glGetUniformLocation(sphere_ray_tracer_shader_program,
                                                                  "camera_up_direction_normalized")
        camera_right_direction_normalized_loc = glGetUniformLocation(sphere_ray_tracer_shader_program,
                                                                     "camera_right_direction_normalized")
        raytracing_max_bounces_loc = glGetUniformLocation(sphere_ray_tracer_shader_program, "raytracing_max_bounces")
        window_size_loc = glGetUniformLocation(sphere_ray_tracer_shader_program, "window_size")
        sphere_positions_loc = glGetUniformLocation(sphere_ray_tracer_shader_program, "sphere_positions")
        sphere_radii_loc = glGetUniformLocation(sphere_ray_tracer_shader_program, "sphere_radii")
        sphere_colors_loc = glGetUniformLocation(sphere_ray_tracer_shader_program, "sphere_colors")

        while not glfw.window_should_close(self.window):
            glfw.poll_events()

            self.update_sphere_positions()

            glClear(GL_COLOR_BUFFER_BIT)

            glUniform3fv(camera_position_loc, 1, self.camera.get_position().to_list())
            glUniform3fv(camera_look_direction_normalized_loc, 1, self.camera.get_look_direction().to_list())
            glUniform3fv(camera_up_direction_normalized_loc, 1, self.camera.get_up_direction().to_list())
            glUniform3fv(camera_right_direction_normalized_loc, 1, self.camera.get_right_direction().to_list())
            glUniform1i(raytracing_max_bounces_loc, self.raytracing_max_bounces)
            glUniform2fv(window_size_loc, 1, self.window_size)
            glUniform3fv(sphere_positions_loc, len(self.spheres), list((o.get_position().to_list() for o in self.spheres)))
            glUniform1fv(sphere_radii_loc, len(self.spheres), list((o.get_radius() for o in self.spheres)))
            glUniform3fv(sphere_colors_loc, len(self.spheres), list((o.get_color().to_list() for o in self.spheres)))

            glDrawArrays(GL_QUADS, 0, 4)

            glfw.swap_buffers(self.window)

        glfw.terminate()


if __name__ == "__main__":
    app = PythonOpenGLRaytracer()
    app.run()
