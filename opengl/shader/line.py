# -*- coding: utf-8 -*-
"""GLSL code of the line shader

Attributes:
    fragment (str): fragment code
    geometry (str): geometry code
    vertex (str): vertex code
"""


vertex = """
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
"""

geometry = """
#version 330

layout (points) in;
layout (line_strip, max_vertices = 2) out;

uniform mat4 view;
uniform mat4 projection;
uniform int resolution;

in vec3 point_color[];
in float line_width[];

out vec3 line_color;

const float PI = 3.141592;

void main()
{
    line_color = point_color[0];

    gl_Position = projection * view * vec4(gl_in[0].gl_Position.xy, 0., 1.);
    EmitVertex();

    gl_Position = projection * view * vec4(gl_in[0].gl_Position.zw, 0., 1.);
    EmitVertex();

    EndPrimitive();
}
"""

fragment = """
#version 330

precision highp float;

in vec3 line_color;
out vec4 out_color;

void main()
{
    out_color = vec4(line_color, 1.);
}
"""
