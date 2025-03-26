import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.collections import LineCollection
import colorsys

class MandalaCreator:
    def __init__(self):
        # Set up the figure and axes
        self.fig = plt.figure(figsize=(12, 10))
        self.fig.patch.set_facecolor('#111111')
        
        # Main mandala display area
        self.ax = plt.axes([0.1, 0.25, 0.8, 0.7])
        self.ax.set_facecolor('#222222')
        self.ax.set_aspect('equal')
        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.axis('off')
        
        # Control area
        self.ax_symmetry = plt.axes([0.25, 0.12, 0.65, 0.03])
        self.ax_line_width = plt.axes([0.25, 0.08, 0.65, 0.03])
        self.ax_rotation = plt.axes([0.25, 0.04, 0.65, 0.03])
        self.ax_reset = plt.axes([0.1, 0.04, 0.1, 0.05])
        self.ax_save = plt.axes([0.8, 0.16, 0.1, 0.05])
        self.ax_palette = plt.axes([0.1, 0.16, 0.1, 0.05])
        
        # Define color palettes
        self.palettes = {
            'Fire': ['#ff4500', '#ff8c00', '#ffd700', '#ff0000'],
            'Ocean': ['#00008b', '#0000cd', '#00bfff', '#87ceeb'],
            'Forest': ['#006400', '#228b22', '#32cd32', '#90ee90'],
            'Sunset': ['#ff4500', '#ff6347', '#ff7f50', '#ffa07a'],
            'Rainbow': ['#ff0000', '#ff7f00', '#ffff00', '#00ff00', '#0000ff', '#4b0082', '#9400d3'],
            'Monochrome': ['#ffffff', '#cccccc', '#999999', '#666666', '#333333']
        }
        self.current_palette = 'Rainbow'
        
        # Sliders
        self.symmetry_slider = Slider(
            self.ax_symmetry, 'Symmetry Axes', 3, 24, 
            valinit=8, valstep=1, 
            color='#ff6347'
        )
        self.line_width_slider = Slider(
            self.ax_line_width, 'Line Width', 0.5, 5.0, 
            valinit=2.0, 
            color='#ff6347'
        )
        self.rotation_slider = Slider(
            self.ax_rotation, 'Rotation', 0, 360, 
            valinit=0, 
            color='#ff6347'
        )
        
        # Buttons
        self.reset_button = Button(self.ax_reset, 'Reset', color='#333333', hovercolor='#666666')
        self.save_button = Button(self.ax_save, 'Save', color='#333333', hovercolor='#666666')
        self.palette_button = Button(self.ax_palette, self.current_palette, color='#333333', hovercolor='#666666')
        
        # Initialize variables
        self.symmetry = 8
        self.line_width = 2.0
        self.rotation = 0
        self.drawing = False
        self.points = []
        self.mandala_segments = []
        self.mandala_colors = []
        self.current_segment = []
        
        # Connect events
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.symmetry_slider.on_changed(self.update_symmetry)
        self.line_width_slider.on_changed(self.update_line_width)
        self.rotation_slider.on_changed(self.update_rotation)
        self.reset_button.on_clicked(self.reset)
        self.save_button.on_clicked(self.save)
        self.palette_button.on_clicked(self.cycle_palette)
        
        # Draw the initial mandala guide
        self.draw_symmetry_guide()
        
        # Set title
        plt.figtext(0.5, 0.95, 'Interactive Mandala Creator', fontsize=20, 
                   ha='center', color='white')
        plt.figtext(0.5, 0.92, 'Draw with your mouse to create a mandala design', 
                   fontsize=12, ha='center', color='#cccccc')
    
    def draw_symmetry_guide(self):
        """Draw guide lines showing the symmetry axes"""
        # Clear any existing guide lines
        self.ax.cla()
        self.ax.set_facecolor('#222222')
        self.ax.set_aspect('equal')
        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.axis('off')
        
        # Draw a circle
        theta = np.linspace(0, 2*np.pi, 100)
        x = np.cos(theta)
        y = np.sin(theta)
        self.ax.plot(x, y, color='#444444', linestyle='--', alpha=0.5)
        
        # Draw symmetry axes
        rotation_rad = np.radians(self.rotation)
        for i in range(self.symmetry):
            angle = rotation_rad + i * (2*np.pi/self.symmetry)
            self.ax.plot([0, np.cos(angle)], [0, np.sin(angle)], 
                        color='#444444', linestyle='--', alpha=0.3)
        
        # Redraw any existing mandala segments
        self.redraw_mandala()
    
    def get_color(self, segment_index=None):
        """Get a color from the current palette"""
        palette = self.palettes[self.current_palette]
        if segment_index is None:
            segment_index = len(self.mandala_segments)
        return palette[segment_index % len(palette)]
    
    def redraw_mandala(self):
        """Redraw all mandala segments"""
        for segment, color in zip(self.mandala_segments, self.mandala_colors):
            self.draw_symmetrical_segment(segment, color)
    
    def draw_symmetrical_segment(self, segment, color):
        """Draw a segment with symmetry around the center"""
        if not segment:
            return
            
        # Convert segment to numpy array for easier manipulation
        segment = np.array(segment)
        
        # Draw the segment in each symmetric position
        rotation_rad = np.radians(self.rotation)
        for i in range(self.symmetry):
            angle = i * (2*np.pi/self.symmetry) + rotation_rad
            
            # Create rotation matrix
            rot_matrix = np.array([
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)]
            ])
            
            # Rotate the segment
            rotated_segment = np.matmul(segment, rot_matrix.T)
            
            # Draw the rotated segment
            if len(rotated_segment) > 1:
                line = LineCollection([rotated_segment], linewidths=self.line_width, 
                                     color=color, alpha=0.8, zorder=2)
                self.ax.add_collection(line)
    
    def on_press(self, event):
        """Handle mouse button press event"""
        if event.inaxes != self.ax or event.button != 1:
            return
            
        self.drawing = True
        self.current_segment = []
        # Convert mouse coordinates to be relative to center
        self.current_segment.append((event.xdata, event.ydata))
    
    def on_motion(self, event):
        """Handle mouse motion event"""
        if not self.drawing or event.inaxes != self.ax:
            return
            
        # Add the point to the current segment
        self.current_segment.append((event.xdata, event.ydata))
        
        # Clear the axis and redraw
        self.ax.cla()
        self.ax.set_facecolor('#222222')
        self.ax.set_aspect('equal')
        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.axis('off')
        
        # Redraw symmetry guide
        theta = np.linspace(0, 2*np.pi, 100)
        x = np.cos(theta)
        y = np.sin(theta)
        self.ax.plot(x, y, color='#444444', linestyle='--', alpha=0.5)
        
        rotation_rad = np.radians(self.rotation)
        for i in range(self.symmetry):
            angle = rotation_rad + i * (2*np.pi/self.symmetry)
            self.ax.plot([0, np.cos(angle)], [0, np.sin(angle)], 
                        color='#444444', linestyle='--', alpha=0.3)
        
        # Draw previous segments
        self.redraw_mandala()
        
        # Draw current segment with symmetry
        color = self.get_color()
        self.draw_symmetrical_segment(self.current_segment, color)
        
        # Update the canvas
        self.fig.canvas.draw_idle()
    
    def on_release(self, event):
        """Handle mouse button release event"""
        if self.drawing and len(self.current_segment) > 1:
            self.mandala_segments.append(self.current_segment)
            self.mandala_colors.append(self.get_color(len(self.mandala_segments)-1))
            self.drawing = False
    
    def update_symmetry(self, val):
        """Update the number of symmetry axes"""
        self.symmetry = int(val)
        self.draw_symmetry_guide()
        self.fig.canvas.draw_idle()
    
    def update_line_width(self, val):
        """Update the line width"""
        self.line_width = val
        self.draw_symmetry_guide()
        self.fig.canvas.draw_idle()
    
    def update_rotation(self, val):
        """Update the rotation of the mandala"""
        self.rotation = val
        self.draw_symmetry_guide()
        self.fig.canvas.draw_idle()
    
    def reset(self, event):
        """Reset the mandala"""
        self.mandala_segments = []
        self.mandala_colors = []
        self.draw_symmetry_guide()
        self.fig.canvas.draw_idle()
    
    def save(self, event):
        """Save the mandala as an image"""
        # Hide the controls for the saved image
        self.ax_symmetry.set_visible(False)
        self.ax_line_width.set_visible(False)
        self.ax_rotation.set_visible(False)
        self.ax_reset.set_visible(False)
        self.ax_save.set_visible(False)
        self.ax_palette.set_visible(False)
        
        # Make the mandala take up the whole figure
        self.ax.set_position([0.05, 0.05, 0.9, 0.9])
        
        # Draw a clean version for saving
        self.ax.cla()
        self.ax.set_facecolor('#222222')
        self.ax.set_aspect('equal')
        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.axis('off')
        self.redraw_mandala()
        
        # Draw the mandala
        self.fig.canvas.draw()
        
        # Save the figure
        filename = f'mandala_{self.symmetry}_axes.png'
        self.fig.savefig(filename, facecolor=self.fig.get_facecolor(), 
                         bbox_inches='tight', pad_inches=0.1, dpi=300)
        
        # Restore the controls
        self.ax_symmetry.set_visible(True)
        self.ax_line_width.set_visible(True)
        self.ax_rotation.set_visible(True)
        self.ax_reset.set_visible(True)
        self.ax_save.set_visible(True)
        self.ax_palette.set_visible(True)
        
        # Restore the axis
        self.ax.set_position([0.1, 0.25, 0.8, 0.7])
        
        # Redraw
        self.draw_symmetry_guide()
        self.fig.canvas.draw_idle()
        
        print(f"Mandala saved as {filename}")
    
    def cycle_palette(self, event):
        """Cycle through the available color palettes"""
        palettes = list(self.palettes.keys())
        current_index = palettes.index(self.current_palette)
        next_index = (current_index + 1) % len(palettes)
        self.current_palette = palettes[next_index]
        
        # Update the button text
        self.palette_button.label.set_text(self.current_palette)
        
        # Update colors for all segments
        self.mandala_colors = [self.get_color(i) for i in range(len(self.mandala_segments))]
        
        # Redraw
        self.draw_symmetry_guide()
        self.fig.canvas.draw_idle()
    
    def run(self):
        """Run the application"""
        plt.show()


if __name__ == "__main__":
    app = MandalaCreator()
    app.run() 