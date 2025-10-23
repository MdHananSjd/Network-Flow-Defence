// frontend/src/hooks/useGameData.js
import { useState, useEffect, useCallback } from 'react';
import { gameAPI } from '../utils/apiService';

export const useGameData = () => {
    const [graphData, setGraphData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    // Function to fetch or reset the game state 
    const fetchNewGame = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await gameAPI.getNewGame();
            setGraphData(response.data);
            return response.data;
        } catch (err) {
            setError(err.response ? err.response.data.detail : "Failed to load new game.");
        } finally {
            setLoading(false);
        }
    };
    
    // Hook to handle placing a token (POST request)
    const handlePlaceToken = async (nodeId) => {
        if (!graphData) return;
        
        try {
            const response = await gameAPI.placeToken(nodeId);
            // Update local state with the new state returned from the backend
            setGraphData(response.data); 
        } catch (err) {
            console.error("Defense Error:", err);
            alert("Error placing token: " + (err.response?.data?.detail || "Server Error"));
        }
    };

    // Auto-load game on mount
    useEffect(() => {
        fetchNewGame();
    }, []);

    return { graphData, loading, error, fetchNewGame, handlePlaceToken, setGraphData };
};