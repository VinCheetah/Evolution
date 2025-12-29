import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from evopy.evaluator import NNEvaluator
from evopy.individual import NEATIndividual


class NEATEvaluator(NNEvaluator):

    component_type = "NEAT"

    def __init__(self, options):
        super().__init__(options)
        self.neat_function = options.neat_function
        if not callable(self.neat_function):
            raise ValueError("NEATEvaluator requires a callable 'neat_function' option.")

    def _evaluate(self, individual: NEATIndividual) -> float:
        network = individual.network
        return self.neat_function(network)


    def plot(self, ax, individual: NEATIndividual) -> None:
        """
        Plot the NEAT neural network with the given individual on the given axis.
        """
        # Clear previous plots
        ax.clear()
        ax.axis("off")
        self.set_limits(ax, 0, 1, 0, 1)
        
        # Get nodes and connections
        nodes = individual.nodes
        connections = individual.connections
        
        if not nodes:
            return
            
        # Separate nodes by type
        input_nodes = [node for node in nodes if node.type == "input"]
        output_nodes = [node for node in nodes if node.type == "output"]
        hidden_nodes = [node for node in nodes if node.type == "hidden"]
        
        # Calculate positions
        node_positions = {}
        
        # Position input nodes on the left (centered vertically)
        if input_nodes:
            if len(input_nodes) == 1:
                y_positions = [0.5]  # Center single input node
            else:
                # Center multiple nodes with padding from edges
                y_positions = np.linspace(0.2, 0.8, len(input_nodes))
            for i, node in enumerate(sorted(input_nodes, key=lambda n: n.id)):
                node_positions[node.id] = (0.1, y_positions[i])
        
        # Position output nodes on the right (centered vertically)
        if output_nodes:
            if len(output_nodes) == 1:
                y_positions = [0.5]  # Center single output node
            else:
                # Center multiple nodes with padding from edges
                y_positions = np.linspace(0.2, 0.8, len(output_nodes))
            for i, node in enumerate(sorted(output_nodes, key=lambda n: n.id)):
                node_positions[node.id] = (0.9, y_positions[i])
        
        # Position hidden nodes in the middle (centered)
        if hidden_nodes:
            num_hidden = len(hidden_nodes)
            if num_hidden == 1:
                # Single hidden node centered
                node_positions[hidden_nodes[0].id] = (0.5, 0.5)
            elif num_hidden <= 10:
                # Simple grid for small numbers, centered
                cols = int(np.ceil(np.sqrt(num_hidden)))
                rows = int(np.ceil(num_hidden / cols))
                
                # Center the grid
                grid_width = 0.4  # Total width for hidden nodes
                grid_height = 0.6  # Total height for hidden nodes
                x_start = 0.5 - grid_width / 2
                y_start = 0.5 - grid_height / 2
                
                x_positions = np.linspace(x_start, x_start + grid_width, cols)
                y_positions = np.linspace(y_start, y_start + grid_height, rows)
                
                for i, node in enumerate(sorted(hidden_nodes, key=lambda n: n.id)):
                    row = i // cols
                    col = i % cols
                    if row < len(y_positions) and col < len(x_positions):
                        node_positions[node.id] = (x_positions[col], y_positions[row])
            else:
                # Random positioning for many hidden nodes, centered area
                np.random.seed(42)  # For consistent positioning
                x_positions = np.random.uniform(0.3, 0.7, num_hidden)
                y_positions = np.random.uniform(0.2, 0.8, num_hidden)
                
                for i, node in enumerate(sorted(hidden_nodes, key=lambda n: n.id)):
                    node_positions[node.id] = (x_positions[i], y_positions[i])
        
        # Draw nodes - always create all categories for consistent legend
        # Input nodes
        if input_nodes:
            input_pos = [node_positions[node.id] for node in input_nodes]
            ax.scatter(*zip(*input_pos), c="blue", s=100, label="Input", alpha=0.8)
        else:
            # Create invisible scatter for legend consistency
            ax.scatter([], [], c="blue", s=100, label="Input", alpha=0.8)
        
        # Hidden nodes
        if hidden_nodes:
            hidden_pos = [node_positions[node.id] for node in hidden_nodes]
            ax.scatter(*zip(*hidden_pos), c="green", s=80, label="Hidden", alpha=0.8)
        else:
            # Create invisible scatter for legend consistency
            ax.scatter([], [], c="green", s=80, label="Hidden", alpha=0.8)
        
        # Output nodes
        if output_nodes:
            output_pos = [node_positions[node.id] for node in output_nodes]
            ax.scatter(*zip(*output_pos), c="red", s=100, label="Output", alpha=0.8)
        else:
            # Create invisible scatter for legend consistency
            ax.scatter([], [], c="red", s=100, label="Output", alpha=0.8)
        
        # Draw connections
        if connections:
            enabled_connections = [conn for conn in connections if conn.enabled]
            disabled_connections = [conn for conn in connections if not conn.enabled]
            
            # Get weight range for normalization
            all_weights = [abs(conn.weight) for conn in enabled_connections if conn.weight != 0]
            w_max = max(all_weights) if all_weights else 1.0
            
            # Draw enabled connections
            if enabled_connections:
                lines = []
                colors = []
                linewidths = []
                
                for conn in enabled_connections:
                    if conn.in_node.id in node_positions and conn.out_node.id in node_positions:
                        start_pos = node_positions[conn.in_node.id]
                        end_pos = node_positions[conn.out_node.id]
                        lines.append([start_pos, end_pos])
                        
                        # Color based on weight sign
                        colors.append("darkgreen" if conn.weight > 0 else "darkred")
                        
                        # Line width based on weight magnitude
                        width = max(0.5, min(5.0, abs(conn.weight) / w_max * 3))
                        linewidths.append(width)
                
                if lines:
                    lc = LineCollection(lines, colors=colors, linewidths=linewidths, alpha=0.7)
                    ax.add_collection(lc)
            
            # Draw disabled connections as dashed lines
            if disabled_connections:
                disabled_lines = []
                
                for conn in disabled_connections:
                    if conn.in_node.id in node_positions and conn.out_node.id in node_positions:
                        start_pos = node_positions[conn.in_node.id]
                        end_pos = node_positions[conn.out_node.id]
                        disabled_lines.append([start_pos, end_pos])
                
                if disabled_lines:
                    lc_disabled = LineCollection(disabled_lines, colors="gray", 
                                               linewidths=0.5, linestyles="dashed", alpha=0.3)
                    ax.add_collection(lc_disabled)
        
        # Always show legend in consistent order: Input, Hidden, Output
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.05), ncol=3, 
                 fontsize=8, frameon=False)
        
        # Store positions for future reference
        curves = self.get_curves(ax)
        curves["node_positions"] = node_positions

    def init_plot(self, ax) -> None:
        """
        Initialize the plot of the NEAT neural network on the given axis.
        """
        ax.axis("off")
        self.set_limits(ax, 0, 1, 0, 1)
        
        # Store references for dynamic plotting - will be updated in plot()
        self.set_curves(ax, {
            "input_nodes": None,
            "output_nodes": None, 
            "hidden_nodes": None,
            "connections": None,
            "node_positions": {}
        })


