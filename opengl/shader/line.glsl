
//=============================================== BLOCK: VERTEX
#version 330

layout (location = 0) in vec4 position;
layout (location = 1) in vec4 color;
layout (location = 2) in float width;

out vec4 point_color;
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
layout (triangle_strip, max_vertices = 64) out;

uniform mat4 view;
uniform mat4 projection;
uniform int resolution;

in vec4 point_color[];
in float line_width[];

out vec4 line_color;

const float PI = 3.141592;

float deltaRad = PI/resolution;
float radius = line_width[0]/2;

void cap(vec2 pos, float start)
{
    float ang = start;

    for(int i = 0; i <= resolution/4; i++) {

        vec2 offset = vec2(cos(ang) * radius, sin(ang) * radius);
        gl_Position = projection * view * vec4(pos + offset, 0., 1.);
        EmitVertex();
        ang += deltaRad;

        offset = vec2(cos(ang) * radius, sin(ang) * radius);
        gl_Position = projection * view * vec4(pos + offset, 0., 1.);
        EmitVertex();
        ang += deltaRad;

        gl_Position = projection * view * vec4(pos, 0., 1.);
        EmitVertex();

        offset = vec2(cos(ang) * radius, sin(ang) * radius);
        gl_Position = projection * view * vec4(pos + offset, 0., 1.);
        EmitVertex();
        ang += deltaRad;

        offset = vec2(cos(ang) * radius, sin(ang) * radius);
        gl_Position = projection * view * vec4(pos + offset, 0., 1.);
        EmitVertex();
        // ang += deltaRad;
    }

    EndPrimitive();
}

float atan2(float y, float x)
{
    return x == 0.0 ? sign(y)*PI/2 : atan(y, x);
}

// float atan2(float y, float x)
// {
//     if(abs(x) > abs(y))
//         return PI/2 - atan(x, y);

//     return atan(y, x);
//     // bool s = (abs(x) > abs(y));
//     // return mix(PI/2.0 - atan(x,y), atan(y,x), s);
// }

void main()
{
    line_color = point_color[0];

    vec2 tmp = gl_in[0].gl_Position.xy - gl_in[0].gl_Position.zw;

    float a = atan2(tmp.y, tmp.x);

    float b = a + PI/2;
    float c = b - PI;

    vec2 da = vec2(cos(b)*radius, sin(b)*radius);
    vec2 db = vec2(cos(c)*radius, sin(c)*radius);

    // line_color = vec3(1,.5,.5);
    gl_Position = projection * view * vec4(gl_in[0].gl_Position.xy + da, 0., 1.);
    EmitVertex();
    // line_color = vec3(.5,1,.5);
    gl_Position = projection * view * vec4(gl_in[0].gl_Position.xy + db, 0., 1.);
    EmitVertex();
    // line_color = vec3(.5,.5,1);
    gl_Position = projection * view * vec4(gl_in[0].gl_Position.zw + da, 0., 1.);
    EmitVertex();
    // line_color = vec3(1,1,.5);
    gl_Position = projection * view * vec4(gl_in[0].gl_Position.zw + db, 0., 1.);
    EmitVertex();

    EndPrimitive();

    cap(gl_in[0].gl_Position.xy, c);
    cap(gl_in[0].gl_Position.zw, b);
}


//=============================================== BLOCK: FRAGMENT
#version 330

precision highp float;

in vec4 line_color;
out vec4 out_color;

void main()
{
    out_color = line_color;
}
