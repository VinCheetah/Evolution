"""Directed graph algorithm implementations."""


def creates_cycle(connections, test):
    """
    Returns true if the addition of the 'test' connection would create a cycle,
    assuming that no cycle already exists in the graph represented by '_connections'.
    """
    # Handle both tuple and ConnectionGene inputs for test
    if hasattr(test, 'in_node') and hasattr(test, 'out_node'):
        i, o = test.in_node, test.out_node
    else:
        i, o = test
    
    if i == o:
        return True

    visited = {o}
    while True:
        num_added = 0
        for conn in connections:
            # Handle both tuple and ConnectionGene inputs for connections
            if hasattr(conn, 'in_node') and hasattr(conn, 'out_node'):
                a, b = conn.in_node, conn.out_node
            else:
                a, b = conn
                
            if a in visited and b not in visited:
                if b == i:
                    return True

                visited.add(b)
                num_added += 1

        if num_added == 0:
            return False


def required_for_output(inputs, outputs, connections):
    """
    Collect the nodes whose state is required to compute the final network output(s).
    :param inputs: list of the input identifiers
    :param outputs: list of the output node identifiers
    :param connections: list of (input, output) _connections in the network.
    NOTE: It is assumed that the input identifier set and the node identifier set are disjoint.
    By convention, the output node ids are always the same as the output index.

    Returns a set of identifiers of required nodes.
    """
    assert not set(inputs).intersection(outputs)

    required = set(outputs)
    s = set(outputs)
    while 1:
        # Find nodes not in s whose output is consumed by a node in s.
        # Handle both tuple and ConnectionGene inputs
        if connections and hasattr(next(iter(connections)), 'in_node'):
            # ConnectionGene objects
            t = set(c.in_node.id if hasattr(c.in_node, 'id') else c.in_node 
                   for c in connections 
                   if (c.out_node.id if hasattr(c.out_node, 'id') else c.out_node) in s 
                   and (c.in_node.id if hasattr(c.in_node, 'id') else c.in_node) not in s)
        else:
            # Simple tuples
            t = set(c[0] for c in connections if c[1] in s and c[0] not in s)

        if not t:
            break

        layer_nodes = set(x for x in t if x not in inputs)
        if not layer_nodes:
            break

        required = required.union(layer_nodes)
        s = s.union(t)
    return required


def feed_forward_layers(inputs, outputs, connections):
    """
    Collect the layers whose members can be evaluated in parallel in a feed-forward network.
    :param inputs: list of the network input nodes
    :param outputs: list of the output node identifiers
    :param connections: list of (input, output) _connections in the network.

    Returns a list of layers, with each layer consisting of a set of node identifiers.
    Note that the returned layers do not contain nodes whose output is ultimately
    never used to compute the final network output.
    """

    required = required_for_output(inputs, outputs, connections)

    layers = []
    s = set(inputs)
    while 1:
        # Find candidate nodes c for the next layer.  These nodes should connect
        # a node in s to a node not in s.
        # Handle both tuple and ConnectionGene inputs
        if connections and hasattr(next(iter(connections)), 'in_node'):
            # ConnectionGene objects
            c = set((c.out_node.id if hasattr(c.out_node, 'id') else c.out_node) 
                   for c in connections 
                   if (c.in_node.id if hasattr(c.in_node, 'id') else c.in_node) in s 
                   and (c.out_node.id if hasattr(c.out_node, 'id') else c.out_node) not in s)
        else:
            # Simple tuples
            c = set(c[1] for c in connections if c[0] in s and c[1] not in s)
            
        # Keep only the used nodes whose entire input set is contained in s.
        t = set()
        for n in c:
            if n in required:
                # Check if all inputs for node n are in s
                if connections and hasattr(next(iter(connections)), 'in_node'):
                    # ConnectionGene objects
                    all_inputs_ready = all(
                        (c.in_node.id if hasattr(c.in_node, 'id') else c.in_node) in s 
                        for c in connections 
                        if (c.out_node.id if hasattr(c.out_node, 'id') else c.out_node) == n
                    )
                else:
                    # Simple tuples
                    all_inputs_ready = all(c[0] in s for c in connections if c[1] == n)
                    
                if all_inputs_ready:
                    t.add(n)

        if not t:
            break

        layers.append(t)
        s = s.union(t)

    return layers