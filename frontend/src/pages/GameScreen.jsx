import React, { useState, useEffect } from 'react';
import { useGameData } from '../hooks/useGameData';
import { useSimulation } from '../hooks/useSimulation';
import { gameAPI } from '../utils/apiService';
import GraphView from '../components/GraphView';
import GameControls from '../components/GameControls';

const GameScreen = () => {
    const { 
        graphData, 
        loading, 
        error, 
        fetchNewGame, 
        handlePlaceToken, // Function to call backend POST
        setGraphData 
    } = useGameData();
    
    const { 
        simulationData, 
        simulationStatus, 
        startSimulation,
        resetSimulation,
        error: simulationError
    } = useSimulation();

    const [finalScore, setFinalScore] = useState(null);
    const [tokensLeft, setTokensLeft] = useState(3);

    // --- STATE SYNC & PHASE CONTROL ---
    
    // Sync local state when graphData updates from the backend (POST or GET)
    useEffect(() => {
        if (graphData) {
            setTokensLeft(graphData.metadata.tokens_left);
            // If simulation data exists, update graph state to show firewalls
            // This part needs logic to merge firewall state from simulation if needed
            
            // Reset score when a new game loads
            setFinalScore(null); 
        }
    }, [graphData]);

    // Fetch Final Score once simulation is COMPLETE
    useEffect(() => {
        if (simulationStatus === 'COMPLETE') {
            gameAPI.getFinalScore().then(response => {
                setFinalScore(response.data);
            }).catch(e => console.error("Failed to fetch score:", e));
        }
    }, [simulationStatus]);
    
    // --- HANDLERS ---
    const handleNodeClick = async (nodeId) => {
        // Only allow clicks during the Defense Phase (IDLE or READY)
        if (simulationStatus === 'IDLE' || simulationStatus === 'READY') {
            await handlePlaceToken(nodeId); // Calls backend POST and updates graphData hook
        } else {
            console.log("Cannot interact during simulation or scoring.");
        }
    };

    const handleStartSimulation = () => {
        if (graphData && simulationStatus === 'READY') {
            startSimulation(); // Triggers WebSocket stream
        }
    };
    
    const handleNewGame = () => {
        fetchNewGame(); // Resets all state via backend call
        resetSimulation(); // Clears simulation visual history
        setFinalScore(null);
    };

    // --- RENDERING ---
    if (loading) return <div style={{padding: '20px'}}>Loading Initial Network...</div>;
    if (error) return <div style={{padding: '20px', color: 'red'}}>Error: {error}</div>;
    if (simulationError) return <div style={{padding: '20px', color: 'red'}}>Simulation Error: {simulationError}</div>;

    return (
        <div style={{ padding: '20px' }}>
            <h1 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
                Network Defense Challenge
            </h1>

            <div style={{ display: 'flex', gap: '20px', minHeight: '600px' }}>
                
                {/* --- Controls & Status Panel --- */}
                <div style={{ width: '300px', flexShrink: 0 }}>
                    <GameControls
                        simulationStatus={simulationStatus}
                        tokensLeft={tokensLeft}
                        onStartSimulation={handleStartSimulation}
                        onNewGame={handleNewGame}
                        finalScore={finalScore}
                        loading={loading}
                    />
                </div>

                {/* --- Graph View --- */}
                <div style={{ flex: 1, minWidth: 0 }}>
                    <GraphView 
                        data={graphData} 
                        onNodeClick={handleNodeClick} 
                        simulationSteps={simulationData}
                        simulationStatus={simulationStatus}
                    />
                </div>
            </div>
        </div>
    );
};

export default GameScreen;