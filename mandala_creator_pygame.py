import pygame
import numpy as np
import sys
import os
import math
import colorsys
from datetime import datetime

class MandalaCreator:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Interactive Mandala Creator")
        
        # Colors
        self.BLACK = (10, 10, 10)
        self.DARK_GRAY = (34, 34, 34)
        self.LIGHT_GRAY = (180, 180, 180)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 100, 100)
        self.BLUE = (100, 100, 255)
        
        # Define color palettes
        self.palettes = {
            'Fire': [(255, 69, 0), (255, 140, 0), (255, 215, 0), (255, 0, 0)],
            'Ocean': [(0, 0, 139), (0, 0, 205), (0, 191, 255), (135, 206, 235)],
            'Forest': [(0, 100, 0), (34, 139, 34), (50, 205, 50), (144, 238, 144)],
            'Sunset': [(255, 69, 0), (255, 99, 71), (255, 127, 80), (255, 160, 122)],
            'Rainbow': [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), 
                        (0, 0, 255), (75, 0, 130), (148, 0, 211)],
            'Monochrome': [(255, 255, 255), (204, 204, 204), (153, 153, 153), 
                          (102, 102, 102), (51, 51, 51)]
        }
        self.current_palette = 'Rainbow'
        
        # Drawing settings
        self.line_width = 2
        self.symmetry = 8
        self.rotation = 0
        self.drawing = False
        self.mandala_segments = []
        self.mandala_colors = []
        self.current_segment = []
        
        # Canvas settings (centered in screen)
        self.canvas_size = min(self.screen_width, self.screen_height) - 200
        self.canvas_center_x = self.screen_width // 2
        self.canvas_center_y = (self.screen_height - 100) // 2
        
        # UI elements
        self.font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 30, bold=True)
        
        # Controls
        self.symmetry_slider = {"x": 100, "y": self.screen_height - 80, 
                               "width": 300, "height": 20, "min": 3, "max": 24, 
                               "value": self.symmetry, "color": self.RED, "name": "Symmetry Axes"}
        
        self.line_width_slider = {"x": 500, "y": self.screen_height - 80, 
                                 "width": 300, "height": 20, "min": 1, "max": 10, 
                                 "value": self.line_width, "color": self.RED, "name": "Line Width"}
        
        self.rotation_slider = {"x": 100, "y": self.screen_height - 40, 
                              "width": 300, "height": 20, "min": 0, "max": 360, 
                              "value": self.rotation, "color": self.RED, "name": "Rotation"}
        
        self.reset_button = {"x": 900, "y": self.screen_height - 80, 
                           "width": 100, "height": 30, "color": self.DARK_GRAY, 
                           "text": "Reset", "text_color": self.WHITE}
        
        self.save_button = {"x": 900, "y": self.screen_height - 40, 
                          "width": 100, "height": 30, "color": self.DARK_GRAY, 
                          "text": "Save", "text_color": self.WHITE}
        
        self.palette_button = {"x": 500, "y": self.screen_height - 40, 
                             "width": 200, "height": 30, "color": self.DARK_GRAY, 
                             "text": self.current_palette, "text_color": self.WHITE}
        
        # Mouse state
        self.active_slider = None
        self.active_button = None
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down(event)
                
                if event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_up(event)
                
                if event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event)
            
            # Update the display
            self.screen.fill(self.BLACK)
            self.draw_canvas()
            self.draw_ui()
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def draw_canvas(self):
        """Draw the mandala canvas area with symmetry guides"""
        # Draw canvas background
        pygame.draw.circle(self.screen, self.DARK_GRAY, 
                          (self.canvas_center_x, self.canvas_center_y), 
                          self.canvas_size // 2)
        
        # Draw boundary circle
        pygame.draw.circle(self.screen, self.LIGHT_GRAY, 
                          (self.canvas_center_x, self.canvas_center_y), 
                          self.canvas_size // 2, 1)
        
        # Draw symmetry axes
        rotation_rad = math.radians(self.rotation)
        for i in range(self.symmetry):
            angle = rotation_rad + i * (2*math.pi/self.symmetry)
            end_x = self.canvas_center_x + (self.canvas_size // 2) * math.cos(angle)
            end_y = self.canvas_center_y + (self.canvas_size // 2) * math.sin(angle)
            pygame.draw.line(self.screen, self.LIGHT_GRAY, 
                            (self.canvas_center_x, self.canvas_center_y), 
                            (end_x, end_y), 1)
        
        # Draw existing mandala segments
        self.draw_mandala()
    
    def draw_mandala(self):
        """Draw all mandala segments with symmetry"""
        for segment, color in zip(self.mandala_segments, self.mandala_colors):
            self.draw_symmetrical_segment(segment, color)
        
        # Draw current segment if drawing
        if self.drawing and len(self.current_segment) > 1:
            # Get color from palette
            color_idx = len(self.mandala_segments) % len(self.palettes[self.current_palette])
            color = self.palettes[self.current_palette][color_idx]
            self.draw_symmetrical_segment(self.current_segment, color)
    
    def draw_symmetrical_segment(self, segment, color):
        """Draw a segment with symmetry around the center"""
        if not segment or len(segment) < 2:
            return
        
        # Draw the segment in each symmetric position
        rotation_rad = math.radians(self.rotation)
        for i in range(self.symmetry):
            angle = i * (2*math.pi/self.symmetry) + rotation_rad
            
            # Create rotation matrix
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            
            # Draw lines connecting the points
            for j in range(1, len(segment)):
                # Get original points relative to canvas center
                x1, y1 = segment[j-1]
                x2, y2 = segment[j]
                
                # Rotate the points
                x1_rot = x1 * cos_a - y1 * sin_a
                y1_rot = x1 * sin_a + y1 * cos_a
                x2_rot = x2 * cos_a - y2 * sin_a
                y2_rot = x2 * sin_a + y2 * cos_a
                
                # Convert back to screen coordinates
                x1_screen = self.canvas_center_x + x1_rot
                y1_screen = self.canvas_center_y + y1_rot
                x2_screen = self.canvas_center_x + x2_rot
                y2_screen = self.canvas_center_y + y2_rot
                
                # Draw the line
                pygame.draw.line(self.screen, color, 
                               (x1_screen, y1_screen), 
                               (x2_screen, y2_screen), 
                               self.line_width)
    
    def draw_ui(self):
        """Draw all UI elements"""
        # Draw title
        title_text = self.title_font.render("Interactive Mandala Creator", True, self.WHITE)
        self.screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 10))
        
        subtitle_text = self.font.render("Draw with your mouse to create a mandala design", True, self.LIGHT_GRAY)
        self.screen.blit(subtitle_text, (self.screen_width // 2 - subtitle_text.get_width() // 2, 50))
        
        # Draw sliders
        self.draw_slider(self.symmetry_slider)
        self.draw_slider(self.line_width_slider)
        self.draw_slider(self.rotation_slider)
        
        # Draw buttons
        self.draw_button(self.reset_button)
        self.draw_button(self.save_button)
        self.draw_button(self.palette_button)
        
        # Show current palette as small color squares
        palette = self.palettes[self.current_palette]
        palette_x = self.palette_button["x"] + self.palette_button["width"] + 20
        palette_y = self.palette_button["y"]
        square_size = 20
        for i, color in enumerate(palette):
            pygame.draw.rect(self.screen, color, 
                           (palette_x + i * (square_size + 5), palette_y, square_size, square_size))
    
    def draw_slider(self, slider):
        """Draw a slider control"""
        # Draw slider background
        pygame.draw.rect(self.screen, self.DARK_GRAY, 
                        (slider["x"], slider["y"], slider["width"], slider["height"]))
        
        # Calculate handle position
        handle_pos = slider["x"] + int((slider["value"] - slider["min"]) / 
                                     (slider["max"] - slider["min"]) * slider["width"])
        
        # Draw slider handle
        pygame.draw.rect(self.screen, slider["color"], 
                        (handle_pos - 5, slider["y"] - 5, 10, slider["height"] + 10))
        
        # Draw slider label
        label_text = self.font.render(f"{slider['name']}: {slider['value']}", True, self.WHITE)
        self.screen.blit(label_text, (slider["x"], slider["y"] - 25))
    
    def draw_button(self, button):
        """Draw a button control"""
        pygame.draw.rect(self.screen, button["color"], 
                        (button["x"], button["y"], button["width"], button["height"]))
        
        # Draw button text
        text = self.font.render(button["text"], True, button["text_color"])
        text_x = button["x"] + (button["width"] - text.get_width()) // 2
        text_y = button["y"] + (button["height"] - text.get_height()) // 2
        self.screen.blit(text, (text_x, text_y))
    
    def handle_mouse_down(self, event):
        """Handle mouse button down event"""
        x, y = event.pos
        
        # Check if clicking in canvas area for drawing
        canvas_x = x - self.canvas_center_x
        canvas_y = y - self.canvas_center_y
        distance_from_center = math.sqrt(canvas_x**2 + canvas_y**2)
        
        if distance_from_center <= (self.canvas_size // 2):
            self.drawing = True
            self.current_segment = [(canvas_x, canvas_y)]
            return
        
        # Check sliders
        for slider in [self.symmetry_slider, self.line_width_slider, self.rotation_slider]:
            if (slider["x"] <= x <= slider["x"] + slider["width"] and
                slider["y"] <= y <= slider["y"] + slider["height"]):
                self.active_slider = slider
                # Update slider value based on position
                self.update_slider_value(slider, x)
                return
        
        # Check buttons
        for button in [self.reset_button, self.save_button, self.palette_button]:
            if (button["x"] <= x <= button["x"] + button["width"] and
                button["y"] <= y <= button["y"] + button["height"]):
                if button == self.reset_button:
                    self.reset_mandala()
                elif button == self.save_button:
                    self.save_mandala()
                elif button == self.palette_button:
                    self.cycle_palette()
                return
    
    def handle_mouse_up(self, event):
        """Handle mouse button up event"""
        if self.drawing:
            if len(self.current_segment) > 1:
                # Get color from palette
                color_idx = len(self.mandala_segments) % len(self.palettes[self.current_palette])
                color = self.palettes[self.current_palette][color_idx]
                
                self.mandala_segments.append(self.current_segment)
                self.mandala_colors.append(color)
            
            self.drawing = False
            self.current_segment = []
        
        self.active_slider = None
    
    def handle_mouse_motion(self, event):
        """Handle mouse motion event"""
        x, y = event.pos
        
        # If drawing, add point to current segment
        if self.drawing:
            canvas_x = x - self.canvas_center_x
            canvas_y = y - self.canvas_center_y
            distance_from_center = math.sqrt(canvas_x**2 + canvas_y**2)
            
            # Keep drawing within canvas area
            if distance_from_center <= (self.canvas_size // 2):
                self.current_segment.append((canvas_x, canvas_y))
        
        # If dragging a slider, update its value
        if self.active_slider:
            self.update_slider_value(self.active_slider, x)
    
    def update_slider_value(self, slider, x):
        """Update a slider's value based on x position"""
        # Calculate the new value based on position
        ratio = (x - slider["x"]) / slider["width"]
        ratio = max(0, min(1, ratio))  # Clamp between 0 and 1
        
        new_value = slider["min"] + ratio * (slider["max"] - slider["min"])
        
        # Round and clamp
        if slider == self.symmetry_slider:
            new_value = int(round(new_value))  # Integer for symmetry
        elif slider == self.line_width_slider:
            new_value = int(round(new_value))  # Integer for line width
        elif slider == self.rotation_slider:
            new_value = round(new_value)  # Integer for rotation
        
        # Update the actual value
        slider["value"] = new_value
        
        # Update corresponding property
        if slider == self.symmetry_slider:
            self.symmetry = new_value
        elif slider == self.line_width_slider:
            self.line_width = new_value
        elif slider == self.rotation_slider:
            self.rotation = new_value
    
    def reset_mandala(self):
        """Clear the mandala"""
        self.mandala_segments = []
        self.mandala_colors = []
    
    def save_mandala(self):
        """Save the mandala as a PNG image"""
        # Create a timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"mandala_{self.symmetry}_axes_{timestamp}.png"
        
        # Save the current surface
        pygame.image.save(self.screen, filename)
        print(f"Saved mandala as {filename}")
    
    def cycle_palette(self):
        """Switch to the next color palette"""
        palettes = list(self.palettes.keys())
        current_index = palettes.index(self.current_palette)
        next_index = (current_index + 1) % len(palettes)
        self.current_palette = palettes[next_index]
        
        # Update the button text
        self.palette_button["text"] = self.current_palette
        
        # Update colors for all segments
        for i in range(len(self.mandala_colors)):
            color_idx = i % len(self.palettes[self.current_palette])
            self.mandala_colors[i] = self.palettes[self.current_palette][color_idx]


if __name__ == "__main__":
    app = MandalaCreator()
    app.run() 