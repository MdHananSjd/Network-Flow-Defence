import { useState, useEffect, useCallback, useRef } from 'react';

// Use a relative path. The browser will automatically use the correct protocol (ws/wss) 
// and port (5173), relying on the Vite proxy to route /api/ws to the backend's 8000 port.
const SOCKET_URL = '/api/ws/simulate';

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
        // Create WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${protocol}//${window.location.host}${SOCKET_URL}`); 
        
        setSocket(ws);
        socketRef.current = ws;

        ws.onopen = () => {
            console.log('WebSocket connected');
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
            setSimulationStatus('DISCONNECTED');
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            setError('WebSocket connection error');
            setSimulationStatus('ERROR');
        };

        // Cleanup function runs when the component unmounts
        return () => {
            if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
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