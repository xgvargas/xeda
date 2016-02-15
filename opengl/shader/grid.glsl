
//=============================================== BLOCK: VERTEX
#version 330

layout (location = 0) in vec4 position;

uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * position;
}

//=============================================== BLOCK: FRAGMENT
#version 330

precision highp float;

uniform vec3 color;

out vec4 line_color;

void main()
{
    line_color = vec4(color, 1);
}
