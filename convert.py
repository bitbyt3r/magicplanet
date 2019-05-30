import os

import moderngl
import numpy as np
from PIL import Image

ctx = moderngl.create_standalone_context()

prog = ctx.program(
    vertex_shader='''
        #version 330

        in vec2 in_vert;
        out vec2 v_vert;

        void main() {
            gl_Position = vec4(in_vert, 0.0, 1.0);
            v_vert = in_vert;
        }
    ''',
    fragment_shader='''
        #version 330

        uniform sampler2D Texture;
        in vec2 v_vert;
        out vec4 f_color;
        const float PI = 3.1415926535897932384626433832795; 

        void main(void) {
            float r = distance(v_vert, vec2(0.0,0.0));
            float theta = atan(v_vert.y, v_vert.x);
            if (r < 1.0) {
                f_color = texture(Texture, vec2(theta/(2.0*PI), 1.0-2.0*acos(r)/PI));
            } else {
                f_color = vec4(0.0, 0.0, 0.0, 1.0);
            }
        }
    ''',
)

vertices = np.array([
    -1.0, -1.0,
    1.0, -1.0,
    -1.0, 1.0,
    1.0, 1.0,
])
vbo = ctx.buffer(vertices.astype('f4').tobytes())
render_indicies = np.array([
    0, 1, 2,
    1, 2, 3
])
ibo = ctx.buffer(render_indicies.astype('i4').tobytes())
vao = ctx.simple_vertex_array(prog, vbo, 'in_vert', index_buffer=ibo)

def render(frame):
    ctx.clear(1.0, 1.0, 1.0)
    ctx.enable(moderngl.DEPTH_TEST)

    img = frame.convert('RGB')
    texture = ctx.texture(img.size, 3, img.tobytes())
    texture.build_mipmaps()
    texture.use()

    fbo = ctx.simple_framebuffer((512,512))
    fbo.use()
    fbo.clear(0.0, 0.0, 0.0, 1.0)

    vao.render()
    Image.frombytes('RGB', fbo.size, fbo.read(), 'raw', 'RGB', 0, -1).show()

frame = Image.open("./earth.jpg")
render(frame)