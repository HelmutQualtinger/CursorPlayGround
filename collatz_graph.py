import networkx as nx
import matplotlib.pyplot as plt
import math

def collatz_sequence(n):
    """Generate Collatz sequence starting from number n."""
    start = n
    sequence = [n]
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        sequence.append(n)
    return sequence

def create_collatz_graph(max_start=20):
    """Create a directed graph of Collatz sequences up to max_start."""
    G = nx.DiGraph()
    
    # Generate sequences for numbers 1 through max_start
    # Add title to graph
    G.graph['title'] = f'Collatz Numbers up to {max_start}'
    
    for i in range(1, max_start + 1):
        sequence = collatz_sequence(i)
        # Add edges between consecutive numbers in the sequence
        for j in range(len(sequence) - 1):
            G.add_edge(sequence[j], sequence[j + 1])
    return G

def visualize_collatz_graph(max_start=20):
    """Create and visualize the Collatz graph."""
    # Create the graph
    G = create_collatz_graph(max_start)
    
    # Set up the plot
    plt.figure(figsize=(12, 8))
    
    # Position nodes horizontally based on their value
    # Calculate sequence length for each node
    sequence_lengths = {}
    for node in G.nodes():
        sequence = collatz_sequence(node)
        sequence_lengths[node] = len(sequence)
    
    # Position nodes vertically based on sequence length and horizontally by value
    pos = {node: (node, -sequence_lengths[node]) for node in G.nodes()}
    # Normalize vertical positions to avoid overlap
    max_sequence_length = max(sequence_lengths.values())
    pos = {node: ((node), -(sequence_lengths[node] / max_sequence_length) * 10) for node in G.nodes()}
    # Determine edge colors based on direction
    edge_colors = []
    for edge in G.edges():
        if edge[1] > edge[0]:  # Rising edge (next number is larger)
            edge_colors.append('green')
        else:  # Following edge (next number is smaller)
            edge_colors.append('red')
    
    # Draw the graph
    plt.title(G.graph['title'])
    nx.draw(G, pos,
            node_color='orange',
            node_size=500,
            node_shape='d',
            with_labels=True,
            arrows=True,
            edge_color=edge_colors,
            arrowsize=10, 
            edgecolors='black')
    
    plt.title(f'Collatz Sequences Graph (1 to {max_start})')
    plt.savefig('graph.png')
    plt.show()

if __name__ == "__main__":
    # Visualize Collatz sequences for numbers 1 through 20
    visualize_collatz_graph(20) 