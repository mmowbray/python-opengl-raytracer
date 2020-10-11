#version 330

#define ASPECT_RATIO window_size.x / window_size.y

uniform vec2 window_size;
uniform vec3 camera_position;
uniform vec3 camera_look_direction_normalized;
uniform vec3 camera_up_direction_normalized;
uniform vec3 camera_right_direction_normalized;
uniform int raytracing_max_bounces;

uniform vec3[50] sphere_positions;
uniform float[50] sphere_radii;
uniform vec3[50] sphere_colors;

struct ray_t
{
    vec3 position;
    vec3 direction;
};

struct hit_t
{
    bool hit;
    float t;
    int sphere;
};

vec3 getPositionWorldCoordinates(ray_t ray, float t)
{
	return ray.position + t * ray.direction;
}

float getSphereIntersection(ray_t ray, int sphere)
{
	float b = 2 * (ray.direction.x * (ray.position.x - sphere_positions[sphere].x) + ray.direction.y * (ray.position.y - sphere_positions[sphere].y) + ray.direction.z * (ray.position.z - sphere_positions[sphere].z));
	float c = pow(ray.position.x - sphere_positions[sphere].x, 2) + pow(ray.position.y - sphere_positions[sphere].y, 2) + pow(ray.position.z - sphere_positions[sphere].z, 2) - pow(sphere_radii[sphere], 2);

    float beta = sqrt(pow(b, 2) - 4 * c);
	float t0 = (-b + beta) / 2.0f;
	float t1 = (-b - beta) / 2.0f;

	return min(t0, t1);
}

vec3 getSpherePointNormal(vec3 point, int sphere)
{
	return normalize(point - sphere_positions[sphere]);
}

hit_t getNearestSphereIntersection(ray_t ray)
{
    float t = 1000000.0f;
    int nearest_sphere = -1;

    for(int s = 0; s < sphere_positions.length(); ++s) {
        float current_t = getSphereIntersection(ray, s);
        if(current_t > 0.01 &&  current_t < t) {
            t = current_t;
            nearest_sphere = s;
        }
    }

   return hit_t(nearest_sphere != -1, t, nearest_sphere);
}

void main() {

    float normalized_i = (gl_FragCoord.x / window_size.x - 0.5) * 2.0 * ASPECT_RATIO;
    float normalized_j = (gl_FragCoord.y / window_size.y - 0.5) * 2.0;
    vec3 image_point = camera_position + camera_look_direction_normalized + normalized_i * camera_right_direction_normalized + normalized_j * camera_up_direction_normalized;

    ray_t primary_ray = ray_t(camera_position, normalize(image_point - camera_position));

    vec4 final_color = vec4(0.0f);
    uint bounce = 0;
    while (bounce < raytracing_max_bounces) {

        hit_t hit = getNearestSphereIntersection(primary_ray);

        if(hit.hit) {
            //take the color
            if(bounce == 0)
                final_color = vec4((vec3(1.0) + getSpherePointNormal(primary_ray.position, hit.sphere))/2.0f, 1.0f);
            else
                final_color = vec4(mix(final_color.rgb, getSpherePointNormal(primary_ray.position, hit.sphere), 0.1), 1.0f);
                final_color = vec4((vec3(1.0) + getSpherePointNormal(primary_ray.position, hit.sphere))/2.0f, 1.0f);
            //final_color = vec4(getSceneObjectColor(hit.object), 1.0f);

            //update the ray position and direction
            primary_ray.position = getPositionWorldCoordinates(primary_ray, hit.t);
            primary_ray.direction = reflect(primary_ray.direction, getSpherePointNormal(primary_ray.position, hit.sphere));

            ++bounce;
        }
        else{
            break;
        }
    }

    gl_FragColor = final_color;
}