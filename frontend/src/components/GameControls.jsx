import React from 'react';

const GameControls = ({ 
    simulationStatus, 
    tokensLeft, 
    onStartSimulation, 
    onNewGame, 
    finalScore,
    loading 
}) => {
    const isDefensePhase = simulationStatus === 'IDLE' || simulationStatus === 'READY';
    const canStartSimulation = isDefensePhase && tokensLeft === 0;
    const isSimulationRunning = simulationStatus === 'RUNNING';
    const isSimulationComplete = simulationStatus === 'COMPLETE';

    return (
        <div style={{ 
            width: '100%', 
            border: '1px solid #ddd', 
            borderRadius: '8px', 
            padding: '20px',
            backgroundColor: '#f9f9f9'
        }}>
            <h2 style={{ marginTop: 0, color: '#333' }}>Game Controls</h2>
            
            {/* Game Status */}
            <div style={{ marginBottom: '20px' }}>
                <h3>Status: <span style={{ 
                    color: isDefensePhase ? '#28a745' : 
                           isSimulationRunning ? '#ffc107' : 
                           isSimulationComplete ? '#17a2b8' : '#6c757d'
                }}>
                    {simulationStatus}
                </span></h3>
                <p><strong>Tokens Left:</strong> {tokensLeft}</p>
            </div>

            {/* Instructions */}
            <div style={{ marginBottom: '20px' }}>
                {isDefensePhase && tokensLeft > 0 && (
                    <div style={{ 
                        padding: '10px', 
                        backgroundColor: '#d4edda', 
                        border: '1px solid #c3e6cb',
                        borderRadius: '4px',
                        color: '#155724'
                    }}>
                        <strong>Action:</strong> Click nodes on the graph to place firewall tokens.
                    </div>
                )}
                
                {isDefensePhase && tokensLeft === 0 && (
                    <div style={{ 
                        padding: '10px', 
                        backgroundColor: '#fff3cd', 
                        border: '1px solid #ffeaa7',
                        borderRadius: '4px',
                        color: '#856404'
                    }}>
                        <strong>Ready:</strong> All tokens placed. Start simulation to see the infection spread.
                    </div>
                )}

                {isSimulationRunning && (
                    <div style={{ 
                        padding: '10px', 
                        backgroundColor: '#d1ecf1', 
                        border: '1px solid #bee5eb',
                        borderRadius: '4px',
                        color: '#0c5460'
                    }}>
                        <strong>Simulation Running:</strong> Watch the infection spread in real-time.
                    </div>
                )}
            </div>

            {/* Control Buttons */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <button 
                    onClick={onNewGame} 
                    disabled={loading}
                    style={{
                        padding: '12px 24px',
                        backgroundColor: '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        opacity: loading ? 0.6 : 1,
                        fontSize: '16px',
                        fontWeight: 'bold'
                    }}
                >
                    {loading ? 'Loading...' : 'Start New Game'}
                </button>

                {canStartSimulation && (
                    <button 
                        onClick={onStartSimulation}
                        style={{
                            padding: '12px 24px',
                            backgroundColor: '#dc3545',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '16px',
                            fontWeight: 'bold'
                        }}
                    >
                        Start BFS Simulation
                    </button>
                )}
            </div>

            {/* Final Score Display */}
            {isSimulationComplete && finalScore && (
                <div style={{ 
                    marginTop: '20px', 
                    padding: '15px', 
                    backgroundColor: '#d4edda', 
                    border: '2px solid #28a745',
                    borderRadius: '8px',
                    color: '#155724'
                }}>
                    <h3 style={{ marginTop: 0, color: '#155724' }}>🎉 Simulation Complete!</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                        <div>
                            <strong>Your Tokens Used:</strong><br />
                            {finalScore.user_tokens_used}
                        </div>
                        <div>
                            <strong>Optimal (Min-Cut):</strong><br />
                            {finalScore.optimal_tokens_required}
                        </div>
                    </div>
                    <div style={{ 
                        marginTop: '10px', 
                        padding: '10px', 
                        backgroundColor: '#fff', 
                        borderRadius: '4px',
                        textAlign: 'center'
                    }}>
                        <strong style={{ fontSize: '18px' }}>
                            Efficiency Score: {finalScore.efficiency_score.toFixed(2)}%
                        </strong>
                    </div>
                </div>
            )}
        </div>
    );
};

export default GameControls;
