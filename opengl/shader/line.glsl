
//=============================================== BLOCK: VERTEX
#version 330

layout (location = 0) in vec4 position;
layout (location = 1) in vec3 color;
layout (location = 2) in float width;

out vec3 point_color;
out float line_width;

void main()
{
    gl_Position = position;
    point_color = color;
    line_width = width;
}

//=============================================== BLOCK: GEOMETRY
#version 330

layout (points) in;
layout (line_strip, max_vertices = 64) out;

uniform mat4 view;
uniform mat4 projection;
uniform int resolution;

in vec3 point_color[];
in float line_width[];

out vec3 line_color;

const float PI = 3.141592;

void cap(in vec2 pos, in float start)
{
    float radius = line_width[0]/2;

    float rad = PI/resolution;
    float ang = start;

    for(int i = 0; i <= resolution; i++) {

        vec2 offset = vec2(cos(ang) * radius, sin(ang) * radius);

        gl_Position = projection * view * vec4(pos + offset, 0., 1.);
        EmitVertex();

        ang += rad;
    }

    EndPrimitive();
}

float atan2(in float y, in float x)
{
    return x == 0.0 ? sign(y)*PI/2 : atan(y, x);
}

void main()
{
    line_color = point_color[0];

    vec2 tmp = gl_in[0].gl_Position.xy - gl_in[0].gl_Position.zw;

    float a = atan2(tmp.y, tmp.x);

    float b = a+PI/2;
    float c = b-PI;

    float width = line_width[0]/2;

    vec2 da = vec2(cos(b)*width, sin(b)*width);
    vec2 db = vec2(cos(c)*width, sin(c)*width);

    vec4 p1 = vec4(gl_in[0].gl_Position.xy + da, 0., 1.);
    vec4 p2 = vec4(gl_in[0].gl_Position.xy + db, 0., 1.);

    vec4 p3 = vec4(gl_in[0].gl_Position.zw + da, 0., 1.);
    vec4 p4 = vec4(gl_in[0].gl_Position.zw + db, 0., 1.);

    gl_Position = projection * view * vec4(gl_in[0].gl_Position.xy, 0., 1.);
    EmitVertex();
    gl_Position = projection * view * vec4(gl_in[0].gl_Position.zw, 0., 1.);
    EmitVertex();
    EndPrimitive();

    line_color = vec3(1,.5,.5);
    gl_Position = projection * view * p1;
    EmitVertex();
    line_color = vec3(.5,1,.5);
    gl_Position = projection * view * p2;
    EmitVertex();
    line_color = vec3(.5,.5,1);
    gl_Position = projection * view * p4;
    EmitVertex();
    line_color = vec3(1,1,.5);
    gl_Position = projection * view * p3;
    EmitVertex();
    line_color = vec3(1,.5,.5);
    gl_Position = projection * view * p1;
    EmitVertex();

    EndPrimitive();

    // cap(gl_in[0].gl_Position.xy, c);
    cap(gl_in[0].gl_Position.zw, b);
}


//=============================================== BLOCK: FRAGMENT
#version 330

precision highp float;

in vec3 line_color;
out vec4 out_color;

void main()
{
    out_color = vec4(line_color, 1.);
}
