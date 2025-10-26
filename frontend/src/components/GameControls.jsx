import React from 'react';

const GameControls = ({ 
    simulationStatus, 
    tokensLeft, 
    onStartSimulation, 
    onNewGame, 
    finalScore,
    loading,
    gameInitialized
}) => {
    const isDefensePhase = simulationStatus === 'IDLE' || simulationStatus === 'READY';
    const canStartSimulation = isDefensePhase && tokensLeft === 0;
    const isSimulationRunning = simulationStatus === 'RUNNING';
    const isSimulationComplete = simulationStatus === 'COMPLETE';

    return (
        <div style={{ 
            width: '100%',
            fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
        }}>
            {/* Game Phase Indicator */}
            <div style={{ 
                marginBottom: '20px',
                padding: '15px',
                backgroundColor: 'rgba(255,255,255,0.1)',
                borderRadius: '8px',
                border: '1px solid rgba(255,255,255,0.2)'
            }}>
                <h3 style={{ 
                    margin: '0 0 10px 0',
                    color: 'white',
                    fontSize: '16px',
                    fontWeight: '500'
                }}>
                    Current Phase: <span style={{ 
                        color: isDefensePhase ? '#4ade80' : 
                               isSimulationRunning ? '#fbbf24' : 
                               isSimulationComplete ? '#60a5fa' : '#9ca3af',
                        fontWeight: '600'
                    }}>
                        {isDefensePhase ? 'DEFENSE' : 
                         isSimulationRunning ? 'SIMULATION' : 
                         isSimulationComplete ? 'COMPLETE' : 'IDLE'}
                    </span>
                </h3>
                <p style={{ 
                    margin: '0',
                    fontSize: '14px',
                    color: 'rgba(255,255,255,0.8)'
                }}>
                    <strong>🛡️ Tokens Left:</strong> 
                    <span style={{ 
                        color: tokensLeft > 0 ? '#4ade80' : '#f87171',
                        fontWeight: '600',
                        fontSize: '16px'
                    }}> {tokensLeft}</span>
                </p>
            </div>

            {/* Phase Instructions */}
            <div style={{ marginBottom: '20px' }}>
                {isDefensePhase && tokensLeft > 0 && (
                    <div style={{ 
                        padding: '12px', 
                        backgroundColor: 'rgba(74, 222, 128, 0.1)', 
                        border: '1px solid rgba(74, 222, 128, 0.3)',
                        borderRadius: '6px',
                        color: 'rgba(255,255,255,0.9)',
                        fontSize: '14px'
                    }}>
                        <strong>Strategy Phase:</strong> Click nodes on the graph to place firewall tokens.
                    </div>
                )}
                
                {isDefensePhase && tokensLeft === 0 && (
                    <div style={{ 
                        padding: '12px', 
                        backgroundColor: 'rgba(251, 191, 36, 0.1)', 
                        border: '1px solid rgba(251, 191, 36, 0.3)',
                        borderRadius: '6px',
                        color: 'rgba(255,255,255,0.9)',
                        fontSize: '14px'
                    }}>
                        <strong>Ready:</strong> All tokens placed. Start simulation to see the infection spread.
                    </div>
                )}

                {isSimulationRunning && (
                    <div style={{ 
                        padding: '12px', 
                        backgroundColor: 'rgba(96, 165, 250, 0.1)', 
                        border: '1px solid rgba(96, 165, 250, 0.3)',
                        borderRadius: '6px',
                        color: 'rgba(255,255,255,0.9)',
                        fontSize: '14px'
                    }}>
                        <strong>Simulation Phase:</strong> Watch the infection spread in real-time.
                    </div>
                )}
            </div>

            {/* Control Buttons */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
                {/* Start New Game Button - Always Visible */}
                <button 
                    onClick={onNewGame} 
                    disabled={loading}
                    style={{
                        padding: '12px 20px',
                        backgroundColor: 'rgba(255,255,255,0.1)',
                        color: 'white',
                        border: '1px solid rgba(255,255,255,0.2)',
                        borderRadius: '6px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        opacity: loading ? 0.6 : 1,
                        fontSize: '14px',
                        fontWeight: '500',
                        transition: 'all 0.2s ease',
                        width: '100%'
                    }}
                    onMouseOver={(e) => {
                        if (!loading) {
                            e.target.style.backgroundColor = 'rgba(255,255,255,0.2)';
                        }
                    }}
                    onMouseOut={(e) => {
                        if (!loading) {
                            e.target.style.backgroundColor = 'rgba(255,255,255,0.1)';
                        }
                    }}
                >
                    {loading ? '🔄 Loading...' : '🎮 Start New Game'}
                </button>

                {/* Start Simulation Button - Only visible when tokens = 0 and status = READY/IDLE */}
                {canStartSimulation && (
                    <button 
                        onClick={onStartSimulation}
                        style={{
                            padding: '12px 20px',
                            backgroundColor: 'rgba(239, 68, 68, 0.8)',
                            color: 'white',
                            border: '1px solid rgba(239, 68, 68, 0.3)',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: '500',
                            transition: 'all 0.2s ease',
                            width: '100%'
                        }}
                        onMouseOver={(e) => {
                            e.target.style.backgroundColor = 'rgba(239, 68, 68, 1)';
                        }}
                        onMouseOut={(e) => {
                            e.target.style.backgroundColor = 'rgba(239, 68, 68, 0.8)';
                        }}
                    >
                        🚀 Start Simulation
                    </button>
                )}
            </div>

            {/* Final Score Display - Only visible when simulation is COMPLETE */}
            {isSimulationComplete && finalScore && (
                <div style={{ 
                    marginTop: '20px', 
                    padding: '16px', 
                    backgroundColor: 'rgba(34, 197, 94, 0.1)', 
                    border: '1px solid rgba(34, 197, 94, 0.3)',
                    borderRadius: '8px',
                    color: 'rgba(255,255,255,0.9)'
                }}>
                    <h3 style={{ 
                        marginTop: 0, 
                        color: 'white',
                        fontSize: '16px',
                        textAlign: 'center',
                        marginBottom: '12px',
                        fontWeight: '600'
                    }}>🎉 Simulation Complete!</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                        <div style={{ fontSize: '12px' }}>
                            <strong>Your Tokens:</strong><br />
                            <span style={{ fontSize: '14px', fontWeight: '600' }}>{finalScore.user_tokens_used}</span>
                        </div>
                        <div style={{ fontSize: '12px' }}>
                            <strong>Optimal (Min-Cut):</strong><br />
                            <span style={{ fontSize: '14px', fontWeight: '600' }}>{finalScore.optimal_tokens_required}</span>
                        </div>
                    </div>
                    <div style={{ 
                        padding: '8px', 
                        backgroundColor: 'rgba(255,255,255,0.1)', 
                        borderRadius: '4px',
                        textAlign: 'center'
                    }}>
                        <strong style={{ fontSize: '14px' }}>
                            Efficiency Score: {finalScore.efficiency_score.toFixed(2)}%
                        </strong>
                    </div>
                    
                    {/* AI Alignment Score */}
                    {finalScore.ml_alignment_score !== undefined && finalScore.ml_alignment_score !== "Pending ML Model Integration" && (
                        <div style={{ 
                            marginTop: '8px', 
                            padding: '8px', 
                            backgroundColor: 'rgba(59, 130, 246, 0.1)', 
                            border: '1px solid rgba(59, 130, 246, 0.3)',
                            borderRadius: '4px',
                            textAlign: 'center'
                        }}>
                            <strong style={{ fontSize: '12px', color: 'rgba(255,255,255,0.9)' }}>
                                🤖 AI Alignment: {finalScore.ml_alignment_score}%
                            </strong>
                        </div>
                    )}
                </div>
            )}
            
            {/* Feature Data Section - Empty placeholder */}
            <div style={{ 
                marginTop: '20px', 
                padding: '16px', 
                backgroundColor: 'rgba(255,255,255,0.05)', 
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px',
                color: 'rgba(255,255,255,0.6)',
                fontSize: '12px',
                textAlign: 'center'
            }}>
                <strong>Feature Data</strong><br />
                <span style={{ fontSize: '10px' }}>Analytical metrics will appear here</span>
            </div>
        </div>
    );
};

export default GameControls;
