import React, { useEffect, useRef } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';

const style = { 
    width: '100%', 
    height: '600px', 
    border: '2px solid #e0e0e0',
    borderRadius: '8px',
    backgroundColor: '#fafafa'
};

const GraphView = ({ data, onNodeClick, simulationSteps, simulationStatus }) => {
    const cyRef = useRef(null);

    if (!data) return (
        <div style={{
            textAlign: 'center', 
            padding: '40px', 
            color: '#666',
            fontSize: '18px',
            backgroundColor: '#f9f9f9',
            borderRadius: '8px',
            border: '2px dashed #ddd'
        }}>
            🕸️ Waiting for network graph...
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
            // For initial layout, we set random positions (better layout management is done via styling/layout engine)
            position: { x: Math.random() * 800, y: Math.random() * 600 } 
        })),
        ...data.edges.map(edge => ({
            data: { source: edge.source, target: edge.target }
        }))
    ];

    const stylesheet = [
        { 
            selector: 'node', 
            style: { 
                'label': 'data(label)', 
                'color': 'white', 
                'text-valign': 'center', 
                'text-halign': 'center',
                'font-size': '14px',
                'font-weight': 'bold',
                'text-outline-width': 3,
                'text-outline-color': '#000',
                'width': 35,
                'height': 35,
                'background-color': '#6c757d',
                'border-width': 2,
                'border-color': '#495057',
                'cursor': 'pointer'
            } 
        },
        { 
            selector: 'edge', 
            style: { 
                'width': 3, 
                'line-color': '#adb5bd', 
                'target-arrow-color': '#adb5bd',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'opacity': 0.8
            } 
        },
        
        // State Styling
        { 
            selector: '[is_source = true]', 
            style: { 
                'background-color': '#dc3545', 
                'border-width': 4, 
                'border-color': '#a71e2a',
                'width': 50,
                'height': 50,
                'font-size': '16px',
                'label': '🔥 SOURCE'
            } 
        },
        { 
            selector: '[is_target = true]', 
            style: { 
                'background-color': '#007bff', 
                'border-width': 4, 
                'border-color': '#0056b3',
                'width': 50,
                'height': 50,
                'font-size': '16px',
                'label': '🎯 TARGET'
            } 
        },
        { 
            selector: '[is_firewall = true]', 
            style: { 
                'background-color': '#28a745', 
                'border-width': 4, 
                'border-color': '#1e7e34',
                'width': 45,
                'height': 45,
                'font-size': '15px',
                'label': '🛡️ FIREWALL'
            } 
        },
        // Infected nodes during simulation
        { 
            selector: '[is_infected = true]', 
            style: { 
                'background-color': '#fd7e14', 
                'border-width': 4, 
                'border-color': '#e8590c',
                'width': 40,
                'height': 40,
                'font-size': '14px',
                'label': '💀 INFECTED'
            } 
        },
        // Hover effects
        { 
            selector: 'node:hover', 
            style: { 
                'border-width': 5,
                'border-color': '#ffc107',
                'background-opacity': 0.8
            } 
        },
        // Selected nodes
        { 
            selector: 'node:selected', 
            style: { 
                'border-width': 6,
                'border-color': '#ffc107',
                'background-opacity': 0.9
            } 
        }
    ];

    // Update node states when simulation data changes
    useEffect(() => {
        if (cyRef.current && simulationSteps.length > 0) {
            const cy = cyRef.current;
            
            // Update infected nodes
            simulationSteps.forEach(step => {
                if (step.infected_nodes) {
                    step.infected_nodes.forEach(nodeId => {
                        const node = cy.getElementById(nodeId);
                        if (node.length > 0) {
                            node.data('is_infected', true);
                        }
                    });
                }
            });
            
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

                // Apply layout with basic algorithm
                cy.layout({
                    name: 'cose',
                    animate: true,
                    animationDuration: 1000,
                    fit: true,
                    padding: 30
                }).run();
            }}
            stylesheet={stylesheet}
        />
    );
};

export default GraphView;