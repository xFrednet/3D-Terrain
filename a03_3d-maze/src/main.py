import pygame
import esper
from OpenGL import GL as gl


from vertex_buffer_array import StandardShaderVertexArray
import render_systems as rsys
import physic_systems as psys
import components as com

RESOLUTION = 720, 480
FPS = 60

class World(esper.World):
    def __init__(self):
        super().__init__()

        self.thingy = None

        # Systems
        self.add_processor(psys.MovementSystem(), priority=2000)
        self.add_processor(rsys.PrepareFrameSystem(), priority=1010)
        self.add_processor(rsys.TranslationMatricesSystem(), priority=1009)
        self.add_processor(rsys.StandardRenderSystem(), priority=1008)
        self.add_processor(rsys.FinishFrameSystem(), priority=1007)

        self._populate()

    def cleanup(self):
        """
        cleanup... cleanup so what's the story behind this cleanup method why wouldn't I just use `__del__`?
        Well let me tell you the stupidest thing I've found in Python so far... Do you think that
        `del object` calls `object.__del__`? Well you would be kind of right because it does... but not right away.
        YES yes trust me. It queues the `__del__` call. This is usually fine but not here do you want to guess why?
        Well the `__del__` of the VBOs get called after the destruction of PyOpenGL. Now HOW, tell me HOW should I
        destruct a VBO if the OpenGL bindings are unavailable????

        Now calm down and be happy that you've solved this bug after 4 total hours of debugging...... 
        ~ xFrednet 
        """
        for _entity, vbo in self.get_component(StandardShaderVertexArray):
            vbo.cleanup()

        self.get_processor(rsys.StandardRenderSystem).cleanup()

        print("World: Cleanup complete")
    
    def _populate(self):
        # Crappy mixed entity, OOP is a thing... well actually an object...
        # WTF. I'm always amazed by the comments I leave in my code. ~xFrednet 2020.09.23
        vba2 = StandardShaderVertexArray(6)
        vba2.load_position_data([
            -0.1,  0.1, 0.1,
            -0.1, -0.1, 0.1,
            0.1, -0.1, 0.1,
            -0.1,  0.1, 0.1,
            0.1, -0.1, 0.1,
            0.1,  0.1, 0.1])
        vba2.load_color_data([
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
            1.0, 0.0, 0.0,
            0.0, 0.0, 1.0,
            0.0, 1.0, 0.0])

        entity = self.create_entity()
        self.add_component(entity, vba2)
        self.add_component(entity, com.Position())
        self.add_component(entity, com.Velocity(0.001, 0.001))
        self.add_component(entity, com.Scale())
        self.add_component(entity, com.TransformationMatrix())


def game_loop(world):
    clock = pygame.time.Clock()
    last_millis = pygame.time.get_ticks()

    while True:
        # Delta timing. See https://en.wikipedia.org/wiki/Delta_timing
        # Trust me, this gets important in larger games
        # Pygame implementation stolen from: https://stackoverflow.com/questions/24039804/pygame-current-time-millis-and-delta-time
        millis = pygame.time.get_ticks()
        delta = (millis - last_millis) / 1000.0
        last_millis = millis
        
        # Get events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.locals.K_ESCAPE:
                    return

        # Update
        world.process()

        clock.tick(FPS)

def main():
    pygame.init()
    pygame.display.init()
    pygame.display.set_mode(RESOLUTION, pygame.DOUBLEBUF|pygame.OPENGL)
    pygame.display.set_caption("Le 3D maze of time")

    world = World()
    
    game_loop(world)

    world.cleanup()

if __name__ == '__main__':
    main()
    pygame.quit()
