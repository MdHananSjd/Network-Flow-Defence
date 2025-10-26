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
    if (loading) return (
        <div style={{
            padding: '60px',
            textAlign: 'center',
            color: '#2c3e50',
            fontSize: '24px',
            backgroundColor: '#f8f9fa',
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center'
        }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>🔄</div>
            <div>Loading Network Topology...</div>
            <div style={{ fontSize: '16px', color: '#7f8c8d', marginTop: '10px' }}>
                Generating secure network infrastructure
            </div>
        </div>
    );
    
    if (error) return (
        <div style={{
            padding: '60px',
            textAlign: 'center',
            color: '#e74c3c',
            fontSize: '20px',
            backgroundColor: '#f8f9fa',
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center'
        }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>⚠️</div>
            <div>Network Error</div>
            <div style={{ fontSize: '16px', color: '#7f8c8d', marginTop: '10px' }}>
                {error}
            </div>
        </div>
    );
    
    if (simulationError) return (
        <div style={{
            padding: '60px',
            textAlign: 'center',
            color: '#e74c3c',
            fontSize: '20px',
            backgroundColor: '#f8f9fa',
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center'
        }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>🚨</div>
            <div>Simulation Error</div>
            <div style={{ fontSize: '16px', color: '#7f8c8d', marginTop: '10px' }}>
                {simulationError}
            </div>
        </div>
    );

    return (
        <div style={{ 
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
        }}>
            {/* Header */}
            <div style={{ 
                textAlign: 'center', 
                padding: '20px 0',
                borderBottom: '1px solid rgba(255,255,255,0.1)'
            }}>
                <h1 style={{ 
                    margin: 0,
                    fontSize: '2.2rem',
                    fontWeight: '600',
                    letterSpacing: '-0.02em'
                }}>
                    🛡️ Network Flow Defense Challenge
                </h1>
            </div>
            
            {/* Two-Column Layout */}
            <div style={{ 
                display: 'flex', 
                height: 'calc(100vh - 100px)'
            }}>
                {/* Left Column - Controls Panel (30%) */}
                <div style={{ 
                    width: '30%',
                    minWidth: '350px',
                    padding: '20px',
                    borderRight: '1px solid rgba(255,255,255,0.1)',
                    overflowY: 'auto'
                }}>
                    <GameControls
                        simulationStatus={simulationStatus}
                        tokensLeft={tokensLeft}
                        onStartSimulation={handleStartSimulation}
                        onNewGame={handleNewGame}
                        finalScore={finalScore}
                        loading={loading}
                        gameInitialized={!!graphData}
                    />
                </div>
                
                {/* Right Column - Graph View (70%) */}
                <div style={{ 
                    flex: 1,
                    padding: '20px'
                }}>
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