import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap
import mpld3
import webbrowser
import os
import tempfile

def collatz_sequence(n):
    """Generate the Collatz sequence for a given number n."""
    sequence = [n]
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        sequence.append(n)
    return sequence

def create_collatz_graph(sequence):
    """Create a directed graph from the Collatz sequence."""
    G = nx.DiGraph()
    for i in range(len(sequence) - 1):
        G.add_edge(sequence[i], sequence[i + 1])
    return G

def plot_collatz_graph(G):
    """Plot the Collatz graph using matplotlib and display in web browser."""
    # Create a dark style figure
    plt.style.use('dark_background')
    # Make figure wider for better browser fit
    fig, ax = plt.subplots(figsize=(16, 9))  # Wider 16:9 aspect ratio for browser windows
    fig.patch.set_facecolor('#222222')
    ax.set_facecolor('#333333')
    
    # Create a custom layout
    pos = {}
    
    # Find all distinct paths (sequences)
    sequences = []
    start_nodes = []
    
    # Identify start nodes (no incoming edges)
    for node in G.nodes():
        if G.in_degree(node) == 0:
            start_nodes.append(node)
    
    # For each start node, trace the sequence
    for start_node in start_nodes:
        sequence = [start_node]
        current = start_node
        while G.out_degree(current) > 0:
            # Get the successor (in Collatz sequence there's only one)
            successors = list(G.successors(current))
            if successors:
                current = successors[0]
                sequence.append(current)
            else:
                break
        sequences.append(sequence)
    
    # Find the maximum node value for scaling
    max_node_value = max(G.nodes())
    
    # Assign positions based on sequence and logarithmic value
    all_positioned_nodes = set()
    
    for i, sequence in enumerate(sequences):
        for j, node in enumerate(sequence):
            # Position: X by log(value), Y by sequence position
            if node <= 0:
                horizontal_pos = 0
            else:
                # Use logarithmic scale for x position
                horizontal_pos = np.log10(node) / np.log10(max_node_value)
            
            # Increase vertical spacing for better readability
            vertical_pos = -j * 0.6 - i * 2.5  # More vertical space
            pos[node] = (horizontal_pos, vertical_pos)
            all_positioned_nodes.add(node)
    
    # Handle any orphaned nodes
    for node in G.nodes():
        if node not in all_positioned_nodes:
            if node <= 0:
                horizontal_pos = 0
            else:
                horizontal_pos = np.log10(node) / np.log10(max_node_value)
            pos[node] = (horizontal_pos, 0)
    
    # Draw edges with curved arrows
    for edge in G.edges():
        source, target = edge
        x0, y0 = pos[source]
        x1, y1 = pos[target]
        
        # Create a curved arrow
        rad = 0.1  # Curvature of the arrow
        arrow = FancyArrowPatch(
            (x0, y0), (x1, y1),
            connectionstyle=f'arc3,rad={rad}',
            arrowstyle='-|>',
            mutation_scale=10,  # Size of arrow head
            lw=1,
            alpha=0.7,
            color='#FF6B00',  # Orange color
            zorder=1
        )
        ax.add_patch(arrow)
    
    # Draw nodes
    node_sizes = []
    node_colors = []
    
    # Create a custom colormap that goes from dark orange to light orange
    cmap = LinearSegmentedColormap.from_list('OrangeMap', ['#FF6B00', '#FFAB00'], N=256)
    
    for node in G.nodes():
        # Size nodes based on value (with some minimum size)
        size = max(100, 300 * np.log10(node) / np.log10(max_node_value) if node > 1 else 100)
        node_sizes.append(size)
        
        # Color can be based on sequence position for visual interest
        # Find the position in any sequence
        for seq in sequences:
            if node in seq:
                color_val = seq.index(node) / len(seq)
                break
        else:
            color_val = 0.5  # Default for nodes not in a sequence
            
        node_colors.append(color_val)
    
    # Draw nodes with size based on value
    nodes = nx.draw_networkx_nodes(
        G, pos,
        node_size=node_sizes,
        node_color=node_colors,
        cmap=cmap,
        alpha=0.9,
        linewidths=1,
        edgecolors='white',
        ax=ax
    )
    
    # Draw node labels with much larger font size
    nx.draw_networkx_labels(
        G, pos,
        font_size=14,  # Increased from 8 to 14
        font_weight='bold',  # Make text bold for better visibility
        font_color='white',
        verticalalignment='center',  # Center align text
        horizontalalignment='center',  # Center align text
        ax=ax
    )
    
    # Set plot limits with some padding
    ax.set_xlim(-0.1, 1.1)
    
    # Calculate y limits based on node positions
    y_values = [pos[node][1] for node in G.nodes()]
    min_y, max_y = min(y_values), max(y_values)
    padding = (max_y - min_y) * 0.2  # 20% padding
    ax.set_ylim(min_y - padding, max_y + padding)
    
    # Set axis titles
    ax.set_title('Collatz Sequence Graph (Logarithmic Scale)', color='white', fontsize=18, pad=20)
    ax.text(0.5, -0.05, 'Node Value (Log Scale →)', transform=ax.transAxes, 
            ha='center', va='center', color='white', fontsize=14)
    ax.text(-0.05, 0.5, 'Sequence Position (Increasing ↓)', transform=ax.transAxes, 
            ha='center', va='center', color='white', fontsize=14, rotation=90)
    
    # Remove axis ticks and spines
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout()
    
    # Generate HTML with a responsive container
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #222222;
                font-family: Arial, sans-serif;
            }}
            .container {{
                width: 100%;
                height: 100vh;
                display: flex;
                flex-direction: column;
            }}
            .header {{
                padding: 10px;
                text-align: center;
                color: white;
            }}
            .graph-container {{
                flex: 1;
                overflow: hidden;
            }}
            .graph-container svg {{
                width: 100%;
                height: 100%;
            }}
        </style>
        <title>Collatz Sequence Graph</title>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Collatz Sequence Graph</h2>
            </div>
            <div class="graph-container">
                {plot_html}
            </div>
        </div>
    </body>
    </html>
    """
    
    # Convert the matplotlib figure to HTML
    plot_html = mpld3.fig_to_html(fig)
    
    # Insert the plot HTML into our custom template
    full_html = html_template.format(plot_html=plot_html)
    
    # Create a temporary HTML file
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp:
        temp_path = temp.name
        temp.write(full_html.encode('utf-8'))
    
    # Open the HTML file in the default web browser
    webbrowser.open('file://' + temp_path)
    
    # Close the matplotlib figure to free resources
    plt.close(fig)

# Example usage
if __name__ == "__main__":
    user_input = int(input("Enter a positive integer to generate its Collatz sequence: "))
    sequence = collatz_sequence(user_input)
    G = create_collatz_graph(sequence)
    plot_collatz_graph(G)
