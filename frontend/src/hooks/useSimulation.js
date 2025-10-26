import { useState, useEffect, useCallback, useRef } from 'react';

// Primary (via Vite proxy) and fallback (direct to backend) WS URLs
const PRIMARY_WS_PATH = '/api/ws/simulate';
const FALLBACK_WS_ABSOLUTE = 'ws://localhost:8000/api/ws/simulate';

export const useSimulation = () => {
    const [simulationData, setSimulationData] = useState([]);
    const [simulationStatus, setSimulationStatus] = useState('IDLE');
    const [socket, setSocket] = useState(null);
    const [error, setError] = useState(null);
    const socketRef = useRef(null);

    // Function to trigger the backend simulation via WebSocket
    const startSimulation = useCallback(() => {
        if (socket && socket.readyState === WebSocket.OPEN && simulationStatus === 'READY') {
            setSimulationData([]); // Clear previous runs
            setSimulationStatus('RUNNING');
            setError(null);
            // Sends the "START" command that the WebSocket endpoint waits for
            socket.send("START"); 
        } else {
            console.warn('Cannot start simulation: socket not ready');
        }
    }, [socket, simulationStatus]);

    // Function to reset simulation state
    const resetSimulation = useCallback(() => {
        setSimulationData([]);
        setSimulationStatus('IDLE');
        setError(null);
    }, []);

    useEffect(() => {
        let closedByUs = false;

        const connect = (useFallback = false) => {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const url = useFallback
                ? FALLBACK_WS_ABSOLUTE
                : `${protocol}//${window.location.host}${PRIMARY_WS_PATH}`;

            const ws = new WebSocket(url);

            setSocket(ws);
            socketRef.current = ws;

            ws.onopen = () => {
                console.log('WebSocket connected:', url);
                setSimulationStatus('READY');
                setError(null);
            };

            ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.status === 'Simulation_Complete') {
                    setSimulationStatus('COMPLETE');
                } else if (data.step !== undefined) {
                    // If the message is a step, update the data list
                    setSimulationData(prev => [...prev, data]);
                } else if (data.status === 'ERROR') {
                    setError(data.message);
                    setSimulationStatus('ERROR');
                } else {
                    // Handle other message types
                    console.log('Received WebSocket message:', data);
                }
            } catch (err) {
                console.error('Error parsing WebSocket message:', err);
                setError('Failed to parse simulation data');
            }
            };

            ws.onclose = (event) => {
                console.log('WebSocket closed:', event.code, event.reason);
                if (!closedByUs) {
                    // If primary failed, try fallback once
                    if (!useFallback) {
                        console.warn('Retrying WebSocket via backend port...');
                        connect(true);
                    } else {
                        setSimulationStatus('DISCONNECTED');
                        setError('WebSocket connection error');
                    }
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                // Let onclose handle retry logic
            };
        };

        connect(false);

        // Cleanup on unmount
        return () => {
            closedByUs = true;
            const ws = socketRef.current;
            if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
                ws.close();
            }
        };
    }, []); // Empty dependency array ensures this runs once on mount

    return { 
        simulationData, 
        simulationStatus, 
        startSimulation, 
        resetSimulation,
        error 
    };
};