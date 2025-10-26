import React, { useEffect, useRef } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';

const style = { 
    width: '100%', 
    height: '100%', 
    border: '1px solid rgba(255,255,255,0.2)',
    borderRadius: '8px',
    backgroundColor: 'rgba(255,255,255,0.05)',
    boxShadow: '0 4px 16px rgba(0,0,0,0.1)'
};

const GraphView = ({ data, onNodeClick, simulationSteps, simulationStatus }) => {
    const cyRef = useRef(null);

    if (!data) return (
        <div style={{
            textAlign: 'center', 
            padding: '60px', 
            color: 'rgba(255,255,255,0.8)',
            fontSize: '18px',
            backgroundColor: 'rgba(255,255,255,0.05)',
            borderRadius: '8px',
            border: '1px dashed rgba(255,255,255,0.2)',
            boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
            fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
        }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>🕸️</div>
            <div style={{ fontWeight: '600', marginBottom: '10px' }}>Network Defense Challenge</div>
            <div style={{ fontSize: '14px', color: 'rgba(255,255,255,0.6)' }}>Loading network topology...</div>
        </div>
    );

    // Function to determine if a node is currently infected in the simulation
    const isCurrentlyInfected = (nodeId) => {
        if (simulationSteps.length === 0) return false;
        // Check the very last step received for currently infected nodes
        const lastStep = simulationSteps[simulationSteps.length - 1];
        return lastStep && lastStep.infected_nodes && lastStep.infected_nodes.includes(nodeId);
    };

    // Convert API data to Cytoscape elements format
    const elements = [
        ...data.nodes.map(node => ({
            data: { 
                id: node.id, 
                label: node.label, 
                is_firewall: node.is_firewall,
                is_source: node.is_source,
                is_target: node.is_target,
                centrality: node.betweenness_centrality.toFixed(3),
                is_infected: isCurrentlyInfected(node.id)
            },
            // Use backend-provided layout when available to avoid clutter
            position: (node.pos_x != null && node.pos_y != null)
                ? { x: node.pos_x * 800 + 50, y: node.pos_y * 600 + 50 }
                : { x: Math.random() * 800, y: Math.random() * 600 }
        })),
        ...data.edges.map(edge => ({
            data: { source: edge.source, target: edge.target }
        }))
    ];

    const stylesheet = [
        // Base node styling
        { 
            selector: 'node', 
            style: { 
                'label': 'data(label)', 
                'color': 'white', 
                'text-valign': 'center', 
                'text-halign': 'center',
                'font-size': '11px',
                'font-weight': '600',
                'text-outline-width': 1,
                'text-outline-color': 'rgba(0,0,0,0.8)',
                'width': 35,
                'height': 35,
                'background-color': '#6b7280',
                'border-width': 2,
                'border-color': '#4b5563',
                'cursor': 'pointer',
                'transition-property': 'background-color, border-color, width, height, opacity',
                'transition-duration': '0.2s'
            } 
        },
        // Base edge styling
        { 
            selector: 'edge', 
            style: { 
                'width': 2, 
                'line-color': 'rgba(255,255,255,0.4)', 
                'target-arrow-color': 'rgba(255,255,255,0.4)',
                'target-arrow-shape': 'triangle',
                'target-arrow-size': 6,
                'curve-style': 'bezier',
                'opacity': 0.6,
                'transition-property': 'line-color, opacity',
                'transition-duration': '0.2s'
            } 
        },
        
        // === INITIAL STATE: Source and Target nodes ===
        { 
            selector: '[is_source = true]', 
            style: { 
                'background-color': '#ef4444', // Bright Red
                'border-width': 4, 
                'border-color': '#dc2626',
                'width': 50,
                'height': 50,
                'font-size': '12px',
                'label': 'SOURCE',
                'background-opacity': 1,
                'border-opacity': 1
            } 
        },
        { 
            selector: '[is_target = true]', 
            style: { 
                'background-color': '#3b82f6', // Bright Blue
                'border-width': 4, 
                'border-color': '#2563eb',
                'width': 50,
                'height': 50,
                'font-size': '12px',
                'label': 'TARGET',
                'background-opacity': 1,
                'border-opacity': 1
            } 
        },
        
        // === DEFENSE PHASE: Firewall nodes ===
        { 
            selector: '[is_firewall = true]', 
            style: { 
                'background-color': '#22c55e', // Bright Green
                'border-width': 6, 
                'border-color': '#16a34a',
                'width': 45,
                'height': 45,
                'font-size': '11px',
                'label': 'FIREWALL',
                'background-opacity': 1,
                'border-opacity': 1,
                'box-shadow': '0 0 10px rgba(34, 197, 94, 0.5)'
            } 
        },
        
        // === SIMULATION PHASE: Infection animation ===
        { 
            selector: '[is_infected = true]', 
            style: { 
                'background-color': '#f59e0b', // Yellow/Orange for flash
                'border-width': 5, 
                'border-color': '#d97706',
                'width': 40,
                'height': 40,
                'font-size': '10px',
                'label': 'INFECTED',
                'background-opacity': 1,
                'border-opacity': 1,
                'animation': 'pulse 0.5s ease-in-out'
            } 
        },
        
        // Hover effects
        { 
            selector: 'node:hover', 
            style: { 
                'border-width': 5,
                'border-color': '#fbbf24',
                'background-opacity': 0.9,
                'width': 'data(width) * 1.1',
                'height': 'data(height) * 1.1'
            } 
        },
        
        // Selected nodes
        { 
            selector: 'node:selected', 
            style: { 
                'border-width': 6,
                'border-color': '#f59e0b',
                'background-opacity': 0.9,
                'width': 'data(width) * 1.15',
                'height': 'data(height) * 1.15'
            } 
        }
    ];

    // Update node states when simulation data changes with animation
    useEffect(() => {
        if (cyRef.current && simulationSteps.length > 0) {
            const cy = cyRef.current;
            
            // Get the latest step for current infection state
            const latestStep = simulationSteps[simulationSteps.length - 1];
            if (latestStep && latestStep.infected_nodes) {
                // Clear all previous infection states
                cy.nodes().forEach(node => {
                    node.data('is_infected', false);
                });
                
                // Apply infection animation to newly infected nodes
                latestStep.infected_nodes.forEach(nodeId => {
                    const node = cy.getElementById(nodeId);
                    if (node.length > 0) {
                        // Flash animation for newly infected nodes
                        node.data('is_infected', true);
                        
                        // Create a pulsing effect
                        node.animate({
                            style: {
                                'background-color': '#f59e0b',
                                'border-color': '#d97706',
                                'width': 45,
                                'height': 45
                            }
                        }, {
                            duration: 300,
                            complete: () => {
                                node.animate({
                                    style: {
                                        'background-color': '#dc2626',
                                        'border-color': '#b91c1c',
                                        'width': 40,
                                        'height': 40
                                    }
                                }, {
                                    duration: 200
                                });
                            }
                        });
                    }
                });
            }
            
            // Refresh the layout to show changes
            cy.style().update();
        }
    }, [simulationSteps]);

    return (
        <CytoscapeComponent 
            elements={elements} 
            style={style} 
            cy={(cy) => {
                cyRef.current = cy;
                
                // Attach the click handler to fire when a node is tapped
                cy.on('tap', 'node', (event) => {
                    const nodeId = event.target.id();
                    if (onNodeClick && simulationStatus !== 'RUNNING') {
                        onNodeClick(nodeId); 
                    }
                });

                        // If backend provided positions, just fit; else run layout
                        const anyHasPos = data.nodes.some(n => n.pos_x != null && n.pos_y != null);
                        if (anyHasPos) {
                            cy.fit(undefined, 40);
                        } else {
                            cy.layout({
                                name: 'cose',
                                animate: true,
                                animationDuration: 1200,
                                fit: true,
                                padding: 60,
                                nodeRepulsion: 6000,
                                idealEdgeLength: 120,
                                edgeElasticity: 0.5,
                                gravity: 0.2,
                                numIter: 800,
                                randomize: true
                            }).run();
                        }
            }}
            stylesheet={stylesheet}
        />
    );
};

export default GraphView;