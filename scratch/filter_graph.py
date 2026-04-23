import json
import os

def improve_graph():
    graph_path = "/Users/sxd/Desktop/StudyIntel/graphify-out/graph.json"
    if not os.path.exists(graph_path):
        print("graph.json not found")
        return

    with open(graph_path, 'r') as f:
        data = json.load(f)

    # Main files as identified in .graphify_detect.json
    main_file_ids = ["app_py", "create_db_py", "readme_en_linux", "mac_balanced_image", "image2_moonlit_mountain_landscape"]
    
    # Let's find nodes that are explicitly marked as 'code', 'document', 'image', etc. and represent the file itself
    # Usually these have the filename as the label or normalized label.
    
    kept_nodes = []
    kept_node_ids = set()
    
    for node in data['nodes']:
        # If it's one of the main files OR if it's a "community" summary node (optional, but user said "main files only")
        if node.get('id') in main_file_ids or node.get('file_type') in ['code', 'document', 'image'] and '.' in node.get('label', ''):
             # Double check if it's a file node by checking if it has source_location L1 or null
             if node.get('source_location') in ['L1', None]:
                kept_nodes.append(node)
                kept_node_ids.add(node['id'])

    # Map entity nodes back to their source files to preserve connections
    entity_to_file = {}
    for node in data['nodes']:
        if node['id'] not in kept_node_ids:
            source_file = node.get('source_file')
            if source_file:
                # Find the file node ID for this source file
                for file_node in kept_nodes:
                    if file_node.get('source_file') == source_file:
                        entity_to_file[node['id']] = file_node['id']
                        break

    # Filter links
    kept_links = []
    seen_links = set()
    
    for link in data.get('links', []):
        src = link['source']
        tgt = link['target']
        
        # Resolve to file IDs if possible
        resolved_src = src if src in kept_node_ids else entity_to_file.get(src)
        resolved_tgt = tgt if tgt in kept_node_ids else entity_to_file.get(tgt)
        
        if resolved_src and resolved_tgt and resolved_src != resolved_tgt:
            link_key = tuple(sorted([resolved_src, resolved_tgt]))
            if link_key not in seen_links:
                new_link = link.copy()
                new_link['source'] = resolved_src
                new_link['target'] = resolved_tgt
                new_link['weight'] = 1.0
                kept_links.append(new_link)
                seen_links.add(link_key)

    # Update data
    data['nodes'] = kept_nodes
    data['links'] = kept_links
    # Remove hyperedges as they might clutter the simple view
    data['graph']['hyperedges'] = []
    data['hyperedges'] = []

    with open(graph_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Graph improved: {len(kept_nodes)} nodes, {len(kept_links)} links.")

if __name__ == "__main__":
    improve_graph()
