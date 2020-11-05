#version 430 core
#define MAX_PARTICLE_COUNT 256

// v for vertex
layout(location = 0) in float in_id;

out int v_sprite_index;

uniform float u_world_time;

uniform float u_emit_times[MAX_PARTICLE_COUNT];
uniform float u_life_times[MAX_PARTICLE_COUNT];
uniform vec3 u_emit_positions[MAX_PARTICLE_COUNT];
uniform vec3 u_target_positions[MAX_PARTICLE_COUNT * 2];
uniform int u_sprite_incices[MAX_PARTICLE_COUNT];

vec3 lerp(vec3 a, vec3 b, float delta) {
    return a * (1.0 - delta) + b * delta;
}

vec3 calc_path(int particle_id, float delta) {
    int base_index = particle_id * 2;
//    vec3 a = u_target_positions[base_index] - u_emit_positions[particle_id];
//    vec3 b = u_target_positions[base_index + 1] - u_target_positions[base_index];

    vec3 a = lerp(u_emit_positions[particle_id], u_target_positions[base_index], delta);
    vec3 b = lerp(u_target_positions[base_index], u_target_positions[base_index + 1], delta);

    return lerp(a, b, delta);
}

void main() {
    int particle_id = int(in_id);
    float life_time = u_world_time - u_emit_times[particle_id];
    float delta = life_time / u_life_times[particle_id];

    v_sprite_index = u_sprite_incices[particle_id];

//    vec3 path = u_target_positions[particle_id * 2] - u_emit_positions[particle_id]; 

    gl_Position = vec4(calc_path(particle_id, delta), 1.0);
    gl_Position.y += life_time;
}