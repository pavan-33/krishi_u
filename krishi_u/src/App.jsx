import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './styles/index.css';

// Import pages
import Login from './pages/Login';
import Register from './pages/Register';
import AdminDashboard from './pages/AdminDashboard';
import FarmerDashboard from './pages/FarmerDashboard';
import LandlordDashboard from './pages/LandlordDashboard';
import CollaborationSpace from './pages/CollaborationSpace';

function App() {
    // State to track authentication status
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    return (
        <Router>
            <Routes>
                <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
                <Route path="/register" element={<Register />} />
                <Route path="/admin" element={<AdminDashboard />} />
                <Route path="/farmer" element={<FarmerDashboard />} />
                <Route path="/landlord" element={<LandlordDashboard />} />
                <Route path="/collaboration/:id" element={<CollaborationSpace />} />
            </Routes>
        </Router>
    );
}

export default App;
