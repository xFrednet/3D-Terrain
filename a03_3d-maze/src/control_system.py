import math
import esper
import glm
import pygame
import pygame.locals

import components_3d as com
import ressources as res

def add_systems_1_to_world(world):
    world.add_processor(GameControlSystem())

def add_systems_2_to_world(world):
    world.add_processor(ThirdPersonCameraSystem())
    world.add_processor(FreeCamOrientation())

def clamp(value, m_min, m_max):
    if value <= m_min:
        return m_min
    if value >= m_max:
        return m_max
    return value

class GameControlSystem(esper.Processor):

    def process(self):
        keys = pygame.key.get_pressed()
        controls: res.GameControlState = self.world.controls

        # Swap camera
        if keys[controls.key_swap_camera] and not controls.key_swap_camera_state:
            self._swap_camera()
            # swap camera

        # Reset
        if keys[controls.key_return_to_home] and not controls.key_return_to_home_state:
            for _id, (home, transformation) in self.world.get_components(com.Home, com.Transformation):
                transformation.position = home.position
        
        controls.key_swap_camera_state = keys[controls.key_swap_camera]
        controls.key_return_to_home_state = keys[controls.key_return_to_home]

        self._acknowledge_input()
    
    def _swap_camera(self):
        controls: res.GameControlState = self.world.controls
        if controls.control_mode == res.GameControlState.PLAYER_MODE:
            self.world.camera_id = self.world.free_cam
            controls.control_mode = res.GameControlState.FREE_CAM_MODE
        else:
            self.world.camera_id = self.world.player_cam
            controls.control_mode = res.GameControlState.PLAYER_MODE

    def _acknowledge_input(self):
        controls: res.GameControlState = self.world.controls
        
        if controls.control_mode == res.GameControlState.PLAYER_MODE:
            self._wasd_movement(
                self.world.player_object,
                controls.player_speed,
                controls.player_vertical_speed)
            self._arrow_key_rotation(self.world.player_object)
        else:
            self._wasd_movement(
                self.world.free_cam,
                controls.free_camera_speed,
                controls.free_camera_vertical_speed)
            self._arrow_key_rotation(self.world.free_cam)

    def _wasd_movement(self, entity_id, speed, vertical_speed):
        keys = pygame.key.get_pressed()
        velocity = self.world.component_for_entity(entity_id, com.Velocity)

        # WASD
        direction = glm.vec3()
        if keys[pygame.locals.K_w]:
            direction.y += 1
        if keys[pygame.locals.K_s]:
            direction.y -= 1
        if keys[pygame.locals.K_a]:
            direction.x -= 1
        if keys[pygame.locals.K_d]:
            direction.x += 1

        if glm.length(direction) > 0.001:
            velocity.value = glm.normalize(direction) * speed
        else:
            velocity.value = glm.vec3()

        if keys[pygame.locals.K_SPACE]:
            velocity.value.z += vertical_speed
        if keys[pygame.locals.K_LSHIFT]:
            velocity.value.z -= vertical_speed
    
    def _arrow_key_rotation(self, entity_id):
        transformation = self.world.component_for_entity(entity_id, com.Transformation)

        keys = pygame.key.get_pressed()
        pitch_change = 0.0
        if keys[pygame.locals.K_UP]:
            pitch_change += 0.1
        if keys[pygame.locals.K_DOWN]:
            pitch_change -= 0.1
        transformation.rotation.y = clamp(
            transformation.rotation.y + pitch_change,
            (math.pi - 0.2) / -2,
            (math.pi - 0.2) / 2)

        if keys[pygame.locals.K_LEFT]:
            transformation.rotation.x -= 0.1
        if keys[pygame.locals.K_RIGHT]:
            transformation.rotation.x += 0.1

class ThirdPersonCameraSystem(esper.Processor):
    def process(self):
        for _id, (transformation, orientation, third_person_cam) in self.world.get_components(
                com.Transformation,
                com.CameraOrientation,
                com.ThirdPersonCamera):
            orientation.look_at = self.world.component_for_entity(third_person_cam.target, com.Transformation).position

            yaw = self.world.component_for_entity(third_person_cam.target, com.Transformation).rotation.x
            pitch = third_person_cam.pitch

            dir_height = math.sin(pitch)
            dir_vec = glm.vec3(
                math.sin(yaw) * (1.0 - abs(dir_height)),
                math.cos(yaw) * (1.0 - abs(dir_height)),
                dir_height
            )

            target_pos = self.world.component_for_entity(third_person_cam.target, com.Transformation).position
            transformation.position = target_pos - (dir_vec * third_person_cam.distance)


class FreeCamOrientation(esper.Processor):
    def process(self):
        for _id, (transformation, orientation, _free_cam) in self.world.get_components(
                com.Transformation,
                com.CameraOrientation,
                com.FreeCamera):
            height = math.sin(transformation.rotation.y)
            orientation.look_at = transformation.position + glm.vec3(
                math.sin(transformation.rotation.x) * (1.0 - abs(height)),
                math.cos(transformation.rotation.x) * (1.0 - abs(height)),
                height
            )