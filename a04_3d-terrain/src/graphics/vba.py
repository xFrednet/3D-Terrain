import ctypes

from OpenGL import GL as gl


class VertexBufferArray:
    def __init__(self, vertex_count):
        self.vba_id = gl.glGenVertexArrays(1)
        self.vertex_count = vertex_count
        self._vertex_buffer = []

    def cleanup(self):
        for vb in self._vertex_buffer:
            gl.glDeleteBuffers(1, [vb])

        gl.glDeleteVertexArrays(1, [self.vertex_array_id])

    def _load_vertex_buffer(self, attr_id, data, items_per_vertex, gl_array_type, gl_type, type_size):
        gl.glBindVertexArray(self.vba_id)

        vertex_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertex_buffer)
        self._vertex_buffer.append(vertex_buffer)

        array_type = (gl_array_type * len(data))
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            len(data) * type_size,
            array_type(*data),
            gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(
            attr_id,  # attribute 0.
            items_per_vertex,  # components per vertex attribute
            gl_type,  # type
            False,  # to be normalized?
            0,  # stride
            None  # array buffer offset
        )

        gl.glBindVertexArray(0)

    def _load_vertex_buffer_f(self, attr_id, data, items_per_vertex):
        self._load_vertex_buffer(
            attr_id,
            data,
            items_per_vertex,
            gl.GLfloat,
            gl.GL_FLOAT,
            ctypes.sizeof(ctypes.c_float))


class TerrainVba(VertexBufferArray):
    POSITION_ATTR = 0
    NORMAL_ATTR = 1

    def __init__(self, vertex_count):
        super().__init__(vertex_count)

    def load_position_data(self, data):
        self._load_vertex_buffer_f(TerrainVba.POSITION_ATTR, data, 3)

    def load_normal_data(self, data):
        self._load_vertex_buffer_f(TerrainVba.NORMAL_ATTR, data, 3)