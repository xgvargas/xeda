
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

uniform vec4 color;

out vec4 frag_color;

void main()
{
    frag_color = color;
}
