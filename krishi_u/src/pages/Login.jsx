import { useState } from 'react';
import axiosInstance from '../api/axios';
import { useNavigate } from 'react-router-dom';
import { TextField, Button, Box, Typography, Container } from '@mui/material';

import PropTypes from 'prop-types';

const Login = ({ setIsAuthenticated }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async () => {
        try {
            // Make the API request
            const response = await axiosInstance.post('/login', { email, password });

            // Extract token and user details from response
            const { access_token, user } = response.data;

            // Save token to local storage and mark as authenticated
            if (access_token) {
                localStorage.setItem('token', access_token);
                localStorage.setItem('user', JSON.stringify(user)); // Save complete user info
                localStorage.setItem('userId', user.id); // Explicitly store user ID for easier access
                setIsAuthenticated(true);

                // Redirect based on user role
                if (user.role === 'admin') {
                    navigate('/admin');
                } else if (user.role === 'farmer') {
                    navigate('/farmer');
                } else if (user.role === 'landlord') {
                    navigate('/landlord');
                } else {
                    setError('Unexpected role. Please contact support.');
                }
            } else {
                setError('Invalid credentials. Please try again.');
            }
        } catch (err) {
            // Handle error response from backend
            const errorMessage = err.response?.data?.detail || 'Login failed. Please try again.';
            setError(errorMessage);
        }
    };

    return (
        <Container maxWidth="sm">
            <Box mt={8} p={4} boxShadow={3} bgcolor="white">
                <Typography variant="h4" gutterBottom>
                    Login
                </Typography>
                {error && (
                    <Typography color="error" gutterBottom>
                        {error}
                    </Typography>
                )}
                <TextField
                    label="Email"
                    fullWidth
                    margin="normal"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <TextField
                    label="Password"
                    type="password"
                    fullWidth
                    margin="normal"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    onClick={handleLogin}
                    sx={{ mt: 2 }}
                >
                    Login
                </Button>
            </Box>
        </Container>
    );
};

Login.propTypes = {
    setIsAuthenticated: PropTypes.func.isRequired,
};

export default Login;
