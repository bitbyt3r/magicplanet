import av
import sys
import moderngl
import numpy as np
from PIL import Image

import settings

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
vao = ctx.simple_vertex_array(prog, vbo, 'in_vert')

def render(frame):
    ctx.clear(1.0, 1.0, 1.0)
    ctx.enable(moderngl.DEPTH_TEST)

    img = frame.to_image().convert('RGB')
    texture = ctx.texture(img.size, 3, img.tobytes())
    texture.build_mipmaps()
    texture.use()

    fbo = ctx.simple_framebuffer((settings.width, settings.height))
    fbo.use()
    fbo.clear(0.0, 0.0, 0.0, 1.0)

    vao.render(moderngl.TRIANGLE_STRIP)
    return np.array(Image.frombytes('RGB', fbo.size, fbo.read(), 'raw', 'RGB', 0, -1))

container = av.open(sys.argv[1])
container.streams.video[0].thread_type = 'AUTO'

out_container = av.open(sys.argv[2], 'w')
out_stream = out_container.add_stream(settings.codec, framerate=container.streams.video[0].framerate)
out_stream.width = settings.width
out_stream.height = settings.height
out_stream.pix_fmt = settings.pix_fmt

if len(container.streams.audio) > 0:
    audio = container.streams.audio[0]
    out_audio = out_container.add_stream(template=audio)
    for packet in container.demux(audio):
        if packet.dts is None:
            continue
        packet.stream = out_audio
        out_container.mux(packet)

container.close()
container = av.open(sys.argv[1])
container.streams.video[0].thread_type = 'AUTO'
for frame in container.decode(video=0):
    out_frame = av.VideoFrame.from_ndarray(render(frame))
    for packet in out_stream.encode(out_frame):
        out_container.mux(packet)

# Flush stream
for packet in out_stream.encode():
    out_container.mux(packet)

# Close the file
out_container.close()
container.close()
