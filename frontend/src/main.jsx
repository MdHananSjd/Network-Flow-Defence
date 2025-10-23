// frontend/src/main.jsx (or main.js)
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
// Import any global CSS here if necessary

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);