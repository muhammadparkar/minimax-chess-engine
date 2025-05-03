import pygame as p
import math

# Constants for visualization
NODE_RADIUS = 15
LEVEL_HEIGHT = 80
NODE_HORIZONTAL_SPACING = 40
MAX_VISIBLE_DEPTH = 4  # Limit visualization to reasonable depth
TEXT_SIZE = 12
TITLE_SIZE = 18

# Colors
BACKGROUND_COLOR = p.Color("black")
MAX_NODE_COLOR = p.Color(220, 100, 100)  # Red
MIN_NODE_COLOR = p.Color(100, 100, 220)  # Blue
PRUNED_COLOR = p.Color(100, 100, 100)    # Gray
TEXT_COLOR = p.Color("white")
LINE_COLOR = p.Color(150, 150, 150)      # Light gray
CURRENT_NODE_COLOR = p.Color("yellow")
BEST_PATH_COLOR = p.Color(100, 220, 100) # Green

class TreeNode:
    def __init__(self, move=None, score=None, depth=0, is_max=True):
        self.move = move
        self.score = score
        self.children = []
        self.depth = depth
        self.is_max = is_max
        self.pruned = False
        self.x = 0  # Will be set during layout
        self.y = 0  # Will be set during layout
        self.parent = None
        self.is_best_child = False
        self.alpha = float('-inf') if is_max else float('inf')
        self.beta = float('inf') if is_max else float('-inf')
        self.width = 0  # Width of subtree, set during layout
        
    def add_child(self, child):
        self.children.append(child)
        child.parent = self
        return child

class MinimaxVisualizer:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.root = None
        self.current_node = None
        self.surface = p.Surface((width, height))
        # Fonts will be initialized later
        self.font = None
        self.large_font = None
        self.initialized = False
        self.best_leaf = None
        self.node_count = 0
        
    def initialize(self):
        """Initialize fonts after pygame is started"""
        if not self.initialized:
            self.font = p.font.SysFont("Arial", TEXT_SIZE)
            self.large_font = p.font.SysFont("Arial", TITLE_SIZE, bold=True)
            self.initialized = True
        
    def reset(self):
        """Reset the visualizer for a new search"""
        self.root = TreeNode(depth=0, is_max=True)
        self.current_node = self.root
        self.best_leaf = None
        self.node_count = 1
        return self.root
        
    def record_evaluation(self, move, score, depth, is_max, alpha, beta, is_leaf=False, pruned=False):
        """Record a node evaluation during minimax search"""
        # Find or create nodes as needed
        if depth == 0:
            # Root node
            self.reset()
            self.root.move = move
            self.root.score = score
            self.root.alpha = alpha
            self.root.beta = beta
            return self.root
            
        if not self.current_node:
            # Something went wrong
            self.reset()
        
        # If we're going deeper, add children to current node
        if self.current_node.depth == depth - 1:
            # Create new child node
            node = TreeNode(move, score, depth, is_max)
            node.alpha = alpha
            node.beta = beta
            node.pruned = pruned
            
            # Add to parent and update current
            self.current_node.add_child(node)
            self.current_node = node
            self.node_count += 1
            
            # Store best leaf for highlighting the path
            if is_leaf and self.best_leaf is None:
                self.best_leaf = node
                
            return node
        
        # If we're going back up, find appropriate parent
        elif self.current_node.depth > depth - 1:
            # Find the correct ancestor at the right depth
            node = self.current_node
            while node and node.depth > depth - 1:
                node = node.parent
            
            if node:
                # Create new sibling node
                new_node = TreeNode(move, score, depth, is_max)
                new_node.alpha = alpha
                new_node.beta = beta
                new_node.pruned = pruned
                
                # Add to parent and update current
                if node.parent:
                    node.parent.add_child(new_node)
                    self.current_node = new_node
                    self.node_count += 1
                    return new_node
        
        # Something unexpected
        return None
        
    def mark_best_path(self):
        """Mark the path from root to the best leaf node"""
        if not self.best_leaf:
            # Find a leaf node with the best score
            best_score = float('-inf') if self.root.is_max else float('inf')
            best_node = None
            
            def find_best_leaf(node):
                nonlocal best_score, best_node
                if not node.children:  # Leaf node
                    if (node.is_max and node.score > best_score) or (not node.is_max and node.score < best_score):
                        best_score = node.score
                        best_node = node
                for child in node.children:
                    find_best_leaf(child)
                    
            find_best_leaf(self.root)
            self.best_leaf = best_node
            
        # Mark the path
        current = self.best_leaf
        while current and current.parent:
            current.is_best_child = True
            current = current.parent
    
    def layout_tree(self):
        """Compute layout positions for the tree nodes"""
        if not self.root:
            return
        
        # Set vertical positions first (based on depth)
        max_depth = 0
        
        def set_y_positions(node, depth):
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            node.depth = depth
            node.y = 50 + depth * LEVEL_HEIGHT
            for child in node.children:
                set_y_positions(child, depth + 1)
                
        set_y_positions(self.root, 0)
        
        # Calculate tree width using a post-order traversal
        def calculate_width(node):
            if not node.children:
                node.width = 2 * NODE_RADIUS
                return node.width
                
            width = 0
            for child in node.children:
                width += calculate_width(child)
                
            # Add some spacing between children
            width += NODE_HORIZONTAL_SPACING * (len(node.children) - 1)
            node.width = max(width, 2 * NODE_RADIUS)
            return node.width
            
        calculate_width(self.root)
        
        # Set horizontal positions using an in-order traversal
        def set_x_positions(node, left_edge):
            if not node.children:
                node.x = left_edge + NODE_RADIUS
                return left_edge + 2 * NODE_RADIUS
                
            # Position children
            current_x = left_edge
            for child in node.children:
                current_x = set_x_positions(child, current_x)
                current_x += NODE_HORIZONTAL_SPACING
                
            # Position this node centered over its children
            if node.children:
                first_child = node.children[0]
                last_child = node.children[-1]
                node.x = (first_child.x + last_child.x) / 2
                
            return left_edge + node.width
            
        # Position the root centered in the available space
        root_x = (self.width - self.root.width) / 2
        set_x_positions(self.root, root_x)
        
        # Limit visible depth to avoid overcrowding
        def trim_deep_nodes(node, depth):
            if depth > MAX_VISIBLE_DEPTH:
                node.children = []
                return
                
            for child in node.children[:]:
                trim_deep_nodes(child, depth + 1)
                
        #trim_deep_nodes(self.root, 0)
    
    def draw(self):
        """Draw the current state of the minimax tree"""
        self.initialize()  # Make sure we're initialized
        self.surface.fill(BACKGROUND_COLOR)
        
        # First mark the best path if not already done
        if self.root and self.root.children and not any(node.is_best_child for node in self.root.children):
            self.mark_best_path()
        
        # Recalculate layout
        self.layout_tree()
        
        # Draw connections between nodes first (lines)
        def draw_connections(node):
            for child in node.children:
                # Determine line color
                line_color = BEST_PATH_COLOR if child.is_best_child else LINE_COLOR
                line_width = 2 if child.is_best_child else 1
                
                # Draw line to child
                p.draw.line(self.surface, line_color, 
                            (int(node.x), int(node.y)), 
                            (int(child.x), int(child.y)), 
                            line_width)
                
                # Recursive call
                draw_connections(child)
                
        if self.root:
            draw_connections(self.root)
        
        # Then draw the nodes themselves
        def draw_nodes(node):
            # Skip overflow nodes
            if node.y > self.height - 20:
                return
                
            # Determine node color
            if node.pruned:
                node_color = PRUNED_COLOR
            elif node.is_max:
                node_color = MAX_NODE_COLOR
            else:
                node_color = MIN_NODE_COLOR
                
            # Highlight best path
            if node.is_best_child:
                p.draw.circle(self.surface, BEST_PATH_COLOR, 
                             (int(node.x), int(node.y)), 
                             NODE_RADIUS + 2)
            
            # Draw node circle
            p.draw.circle(self.surface, node_color, 
                         (int(node.x), int(node.y)), 
                         NODE_RADIUS)
            
            # Draw score if available
            if node.score is not None:
                # Format score to fit
                score_str = str(node.score)
                if abs(node.score) > 999:
                    if node.score > 0:
                        score_str = "WIN"
                    else:
                        score_str = "LOSS"
                        
                score_text = self.font.render(score_str, True, TEXT_COLOR)
                self.surface.blit(
                    score_text, 
                    (node.x - score_text.get_width() // 2, 
                     node.y - score_text.get_height() // 2)
                )
            
            # Draw move below node if available and at top levels
            if node.move and node.depth < 3:
                try:
                    notation = node.move.getChessNotation()
                    move_text = self.font.render(notation, True, TEXT_COLOR)
                    self.surface.blit(
                        move_text, 
                        (node.x - move_text.get_width() // 2, 
                         node.y + NODE_RADIUS + 2)
                    )
                except:
                    pass
            
            # Recursively draw children
            for child in node.children:
                draw_nodes(child)
                
        if self.root:
            draw_nodes(self.root)
        
        # Draw legend
        legends = [
            ("Max Player (White)", MAX_NODE_COLOR),
            ("Min Player (Black)", MIN_NODE_COLOR),
            ("Pruned Node", PRUNED_COLOR),
            ("Best Path", BEST_PATH_COLOR)
        ]
        
        legend_y = self.height - 80
        for text, color in legends:
            p.draw.circle(self.surface, color, (20, legend_y), 8)
            legend_text = self.font.render(text, True, TEXT_COLOR)
            self.surface.blit(legend_text, (35, legend_y - 6))
            legend_y += 20
            
        # Draw title and stats
        title = self.large_font.render("Minimax Algorithm Visualization", True, TEXT_COLOR)
        self.surface.blit(title, (self.width // 2 - title.get_width() // 2, 10))
        
        stats_text = self.font.render(f"Nodes generated: {self.node_count}", True, TEXT_COLOR)
        self.surface.blit(stats_text, (10, 10))
        
        return self.surface