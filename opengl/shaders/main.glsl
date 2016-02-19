
//=============================================== BLOCK: VERTEX
#version 330

layout (location = 0) in vec2 position;
layout (location = 1) in int color;

uniform mat4 view;
uniform mat4 projection;
uniform vec4 palette[32];  // manter esse valor em dia!

out vec4 vcolor;

void main()
{
	vcolor = vec4(palette[color]);
    gl_Position = projection * view * vec4(position, 0, 1);
}

//=============================================== BLOCK: FRAGMENT
#version 330

// precision highp float;

in vec4 vcolor;

out vec4 frag_color;

void main()
{
    frag_color = vcolor;
}
