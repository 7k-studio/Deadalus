# Vertex shader for OpenGL rendering
# This shader transforms vertex positions and passes them to the fragment shader.

# Vertex shader code
# version 330 core
layout(location = 0) in vec3 position; // Vertex position input
layout(location = 1) in vec3 color;    // Vertex color input

out vec3 fragColor; // Output color to fragment shader

uniform mat4 model;  // Model transformation matrix
uniform mat4 view;   // View transformation matrix
uniform mat4 projection; // Projection transformation matrix

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0); // Transform vertex position
    fragColor = color; // Pass color to fragment shader
}