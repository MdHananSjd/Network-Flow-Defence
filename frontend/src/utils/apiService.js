import axios from 'axios';

// base URL is /api 
const API = axios.create({
    baseURL: '/api', 
});

export const gameAPI = {
    // Hanan's Generator: GET /api/graph/new
    getNewGame: () => API.get('/graph/new'),
    
    // Gohul's State Mutator: POST /api/defense/{node_id}
    placeToken: (nodeId) => API.post(`/defense/${nodeId}`),
    
    // Gohul/Hanan Scoring Integration: GET /api/score/final
    getFinalScore: () => API.get('/score/final'),
    
    // ML Predictions: GET /api/ml/predictions
    getMLPredictions: () => API.get('/ml/predictions'),
};