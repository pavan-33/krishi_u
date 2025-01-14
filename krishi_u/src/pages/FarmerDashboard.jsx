import { useState, useEffect } from 'react';
import axiosInstance from '../api/axios';
import { Container, Box, Typography, Paper, Button, TextField } from '@mui/material';

const FarmerDashboard = () => {
    const [showRegistrationForm, setShowRegistrationForm] = useState(false);
    const [showProfile, setShowProfile] = useState(false);
    const [error, setError] = useState('');
    const [profileData, setProfileData] = useState(null);
    const [isRegistered, setIsRegistered] = useState(false);
    const [formData, setFormData] = useState({
        acres: '',
        previous_experience: ''
    });

    useEffect(() => {
        checkRegistrationStatus();
    }, []);

    const checkRegistrationStatus = async () => {
        try {
            const loggedInUserId = localStorage.getItem('userId');
            const response = await axiosInstance.get(`/farmers/${loggedInUserId}`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
            });
            
            setIsRegistered(true);
            setProfileData(response.data);
        } catch (err) {
            if (err.response && err.response.status === 404) {
                setIsRegistered(false);
                setProfileData(null);
            } else {
                console.error('Error checking registration status:', err);
                setError('Failed to check registration status.');
            }
        }
    };

    const handleInputChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axiosInstance.post('/farmer/register', {
                acres: Number(formData.acres),
                previous_experience: formData.previous_experience
            }, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
            });
            setFormData({ acres: '', previous_experience: '' });
            setShowRegistrationForm(false);
            await checkRegistrationStatus();
        } catch (err) {
            setError('Registration failed. Please try again.');
        }
    };

    const handleViewProfile = async () => {
        try {
            const loggedInUserId = localStorage.getItem('userId');
            const response = await axiosInstance.get(`/farmers/${loggedInUserId}`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
            });
            
            setProfileData(response.data);
            setShowProfile(true);
            setShowRegistrationForm(false);
            setError('');
        } catch (err) {
            console.error('Profile fetch error:', err);
            setError('Failed to load profile. Please try again.');
        }
    };

    return (
        <Container maxWidth="lg">
            <Box mt={8} p={4} boxShadow={3} bgcolor="white">
                <Typography variant="h4" gutterBottom>
                    Farmer Dashboard
                </Typography>

                {error && (
                    <Typography color="error" gutterBottom>
                        {error}
                    </Typography>
                )}

                <Box display="flex" gap={2} justifyContent="center" mt={4} mb={4}>
                    {!isRegistered && (
                        <Button 
                            variant="contained" 
                            color="primary" 
                            onClick={() => {
                                setShowRegistrationForm(true);
                                setShowProfile(false);
                            }}
                        >
                            Register as Farmer
                        </Button>
                    )}
                    {isRegistered && (
                        <Button 
                            variant="contained" 
                            color="secondary" 
                            onClick={handleViewProfile}
                        >
                            View Profile
                        </Button>
                    )}
                </Box>

                {showRegistrationForm && !isRegistered && (
                    <Paper sx={{ p: 3, mt: 3 }}>
                        <form onSubmit={handleSubmit}>
                            <TextField
                                fullWidth
                                label="Acres"
                                name="acres"
                                type="number"
                                value={formData.acres}
                                onChange={handleInputChange}
                                margin="normal"
                                required
                            />
                            <TextField
                                fullWidth
                                label="Previous Experience"
                                name="previous_experience"
                                value={formData.previous_experience}
                                onChange={handleInputChange}
                                margin="normal"
                                multiline
                                rows={4}
                                required
                            />
                            <Box mt={3}>
                                <Button
                                    type="submit"
                                    variant="contained"
                                    color="primary"
                                    sx={{ mr: 2 }}
                                >
                                    Submit
                                </Button>
                                <Button
                                    variant="outlined"
                                    onClick={() => setShowRegistrationForm(false)}
                                >
                                    Cancel
                                </Button>
                            </Box>
                        </form>
                    </Paper>
                )}

                {showProfile && profileData && (
                    <Paper sx={{ p: 3, mt: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Farmer Profile
                        </Typography>
                        <Box sx={{ mt: 2 }}>
                            <Typography><strong>Farmer ID:</strong> {profileData.id}</Typography>
                            <Typography><strong>Acres:</strong> {profileData.acres}</Typography>
                            <Typography><strong>Previous Experience:</strong> {profileData.previous_experience}</Typography>
                        </Box>
                    </Paper>
                )}
            </Box>
        </Container>
    );
};

export default FarmerDashboard;
