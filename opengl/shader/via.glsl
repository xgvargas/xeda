
//=============================================== BLOCK: VERTEX
#version 330

layout (location = 0) in vec4 position;

void main()
{
    gl_Position = position;
}

//=============================================== BLOCK: GEOMETRY
#version 330

precision highp float;

layout (points) in;
layout (triangle_strip, max_vertices = 80) out;

uniform mat4 view;
uniform mat4 projection;
// uniform int resolution;
const float resolution = 32;

const float PI = 3.141592;

void main()
{
    vec2 center = gl_in[0].gl_Position.xy;
    float or = gl_in[0].gl_Position.z / 2;
    float ir = gl_in[0].gl_Position.w / 2;

    float ang;
    float delta = 2.0 * PI / resolution;

    for(int i = 0; i <= resolution; i++)
    {
        ang =  delta * i;
        vec2 a = vec2(cos(ang) * or, sin(ang) * or);
        vec2 b = vec2(cos(ang) * ir, sin(ang) * ir);

        gl_Position = projection * view * vec4(center + a, 0., 1.);
        EmitVertex();

        gl_Position = projection * view * vec4(center + b, 0., 1.);
        EmitVertex();
    }

    EndPrimitive();
}


//=============================================== BLOCK: FRAGMENT
#version 330

precision highp float;

out vec4 out_color;

void main()
{
    out_color = vec4(.5, .5, .5, .7);
}
