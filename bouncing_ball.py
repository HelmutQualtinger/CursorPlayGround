import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, Rectangle, Polygon
import math


# Constants
WIDTH, HEIGHT = 10, 10  # Size of the window
BALL_RADIUS = 0.3
TRIANGLE_SIZE = 6.0  # Size of the triangle
FPS = 60  # Frames per second
DURATION = 10  # Animation duration in seconds
TOTAL_FRAMES = FPS * DURATION

# Initial positions and velocities - place ball in the center of triangle
ball_x, ball_y = 0, 0  # Center of the triangle
velocity_x, velocity_y = 0.15, 0.2
rotation_speed = 0.01  # Radians per frame

# Setup the figure and axis
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(-WIDTH/2, WIDTH/2)
ax.set_ylim(-HEIGHT/2, HEIGHT/2)
ax.set_aspect('equal')
ax.set_title('Ball Bouncing in a Rotating Triangle')
ax.axis('off')

# Create triangle vertices
triangle_vertices = np.array([
    [0, TRIANGLE_SIZE/2],  # Top
    [-TRIANGLE_SIZE/2, -TRIANGLE_SIZE/2],  # Bottom left
    [TRIANGLE_SIZE/2, -TRIANGLE_SIZE/2]  # Bottom right
])

# Create the objects
ball = Circle((ball_x, ball_y), BALL_RADIUS, color='red', zorder=2)
triangle = Polygon(triangle_vertices, color='lightskyblue', alpha=0.5, zorder=1, 
                   fill=True, edgecolor='blue', linewidth=2)

# Add objects to the axis
ax.add_patch(ball)
ax.add_patch(triangle)

# Track for plotting the ball's path
path_x, path_y = [], []
path_line, = ax.plot([], [], 'r-', alpha=0.7, linewidth=5)

# Current rotation angle
angle = 0

def is_inside_triangle(point, triangle_vertices):
    """Check if a point is inside a triangle using barycentric coordinates."""
    x, y = point
    x1, y1 = triangle_vertices[0]
    x2, y2 = triangle_vertices[1]
    x3, y3 = triangle_vertices[2]
    
    # Calculate area of the triangle
    area = 0.5 * abs((x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2)))
    
    # Calculate barycentric coordinates
    alpha = abs((x2*y3 - x3*y2) + (y2-y3)*x + (x3-x2)*y) / (2 * area)
    beta = abs((x1*y3 - x3*y1) + (y1-y3)*x + (x3-x1)*y) / (2 * area)
    gamma = 1 - alpha - beta
    
    # Check if the point is inside
    return 0 <= alpha <= 1 and 0 <= beta <= 1 and 0 <= gamma <= 1

def init():
    """Initialize the animation."""
    ball.center = (ball_x, ball_y)
    # Set the triangle vertices
    triangle.set_xy(triangle_vertices)
    path_line.set_data([], [])
    return ball, triangle, path_line

def update(frame):
    """Update animation for each frame."""
    global ball_x, ball_y, velocity_x, velocity_y, angle
    
    # Rotate the triangle
    angle += rotation_speed
    transform = plt.matplotlib.transforms.Affine2D().rotate_around(0, 0, angle) + ax.transData
    triangle.set_transform(transform)
    
    # Get the corners of the rotated triangle
    corners = triangle_vertices.copy()
    
    # Rotate the corners
    rotated_corners = np.zeros_like(corners)
    for i, (x, y) in enumerate(corners):
        rotated_corners[i, 0] = x * math.cos(angle) - y * math.sin(angle)
        rotated_corners[i, 1] = x * math.sin(angle) + y * math.cos(angle)
    
    # Calculate new position
    new_ball_x = ball_x + velocity_x
    new_ball_y = ball_y + velocity_y
    
    # Update ball position
    ball_x = new_ball_x
    ball_y = new_ball_y
    
    collision_occurred = False
    
    # Check for collisions with the sides of the rotated triangle
    for i in range(3):
        # Get two consecutive corners (wrapping around to the first for the last edge)
        corner1 = rotated_corners[i]
        corner2 = rotated_corners[(i + 1) % 3]
        
        # Vector from corner1 to corner2
        edge_vector = corner2 - corner1
        edge_length = np.linalg.norm(edge_vector)
        edge_unit = edge_vector / edge_length
        
        # Vector from corner1 to ball
        to_ball = np.array([ball_x, ball_y]) - corner1
        
        # Project to_ball onto the edge
        projection_length = np.dot(to_ball, edge_unit)
        projection = corner1 + projection_length * edge_unit if 0 <= projection_length <= edge_length else None
        
        if projection is not None:
            # Distance from projection to ball
            distance = np.linalg.norm(np.array([ball_x, ball_y]) - projection)
            
            # Check if the ball is colliding with this edge
            if distance < BALL_RADIUS:
                collision_occurred = True
                # Normal vector to the edge (perpendicular)
                normal = np.array([-edge_unit[1], edge_unit[0]])
                
                # Make sure the normal is pointing outward
                if np.dot(normal, to_ball) < 0:
                    normal = -normal
                
                # Reflect velocity across the normal
                velocity = np.array([velocity_x, velocity_y])
                reflection = velocity - 2 * np.dot(velocity, normal) * normal
                velocity_x, velocity_y = reflection
                
                # Move the ball slightly away from the edge to prevent sticking
                ball_x, ball_y = projection + normal * BALL_RADIUS * 1.01
    
    # If no collision occurred, check if the ball is still inside the triangle
    if not collision_occurred:
        if not is_inside_triangle((ball_x, ball_y), rotated_corners):
            # Ball has somehow escaped, reset to center
            ball_x, ball_y = 0, 0
    
    # Update the ball's position
    ball.center = (ball_x, ball_y)
    
    # Update path
    path_x.append(ball_x)
    path_y.append(ball_y)
    path_line.set_data(path_x[-1000:], path_y[-1000:])  # Keep only the last 1000 points
    
    return ball, triangle, path_line

# Create the animation
ani = FuncAnimation(fig, update, frames=TOTAL_FRAMES,
                    init_func=init, blit=True, interval=1000/FPS)

# Update path with thicker line and longer history
path_line.set_linewidth(3)  # Make the line thicker

plt.tight_layout()
plt.show() 