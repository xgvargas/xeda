
//=============================================== BLOCK: VERTEX
#version 330

layout (location = 0) in vec2 position;

uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * vec4(position, 0, 1);
}

//=============================================== BLOCK: FRAGMENT
#version 330

precision highp float;

out vec4 out_color;

void main()
{
    out_color = vec4(.5, .5, .5, .7);
}
