import { useState, useEffect } from 'react';
import axiosInstance from '../api/axios';
import { Container, Box, Typography, Paper, Button, TextField } from '@mui/material';

const LandlordDashboard = () => {
    const [showRegistrationForm, setShowRegistrationForm] = useState(false);
    const [showProfile, setShowProfile] = useState(false);
    const [error, setError] = useState('');
    const [profileData, setProfileData] = useState(null);
    
    const [isRegistered, setIsRegistered] = useState(false);
    const [formData, setFormData] = useState({
        land_type: '',
        acres: '',
        location: '',
        images: []
    });

    const [selectedFiles, setSelectedFiles] = useState([]);

    useEffect(() => {
        checkRegistrationStatus();
    }, []);

    const checkRegistrationStatus = async () => {
        try {
            const loggedInUserId = localStorage.getItem('userId');
            const response = await axiosInstance.get('/landlords', {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
            });
            
            const landlordProfile = response.data.find(landlord => 
                landlord.user_id === Number(loggedInUserId)
            );
            
            if (landlordProfile) {
                setIsRegistered(true);
                setProfileData(landlordProfile);
            } else {
                setIsRegistered(false);
            }
        } catch (err) {
            console.error('Error checking registration status:', err);
            setError('Failed to check registration status.');
        }
    };

    const handleInputChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleFileChange = (e) => {
        setSelectedFiles(Array.from(e.target.files));
    };

    const handleUploadImages = async () => {
        try {
            const formData = new FormData();
            selectedFiles.forEach(file => {
                formData.append('files', file);
            });

            console.log('Files being uploaded:', selectedFiles);

            const response = await axiosInstance.post('/upload/images', formData, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'multipart/form-data'
                }
            });

            console.log('Upload response:', response.data);
            console.log('Image URLs received:', response.data.image_urls);

            return response.data.image_urls;
        } catch (err) {
            console.error('Image upload failed:', err);
            setError('Failed to upload images. Please try again.');
            return [];
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            let imageUrls = [];
            if (selectedFiles.length > 0) {
                console.log('Selected files before upload:', selectedFiles);
                imageUrls = await handleUploadImages();
                console.log('Received image URLs:', imageUrls);
            }
            
            const registrationData = {
                land_type: formData.land_type,
                acres: Number(formData.acres),
                location: formData.location,
                images: imageUrls
            };
            
            console.log('Data being sent to register endpoint:', registrationData);
            
            const response = await axiosInstance.post('/landlord/register', registrationData, {
                headers: { 
                    Authorization: `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                },
            });
            
            console.log('Registration response:', response.data);
            
            setFormData({ land_type: '', acres: '', location: '', images: [] });
            setSelectedFiles([]);
            setShowRegistrationForm(false);
            await checkRegistrationStatus();
        } catch (err) {
            console.error('Registration error:', err);
            setError('Registration failed. Please try again.');
        }
    };

    const handleViewProfile = async () => {
        try {
            const loggedInUserId = localStorage.getItem('userId');
            
            const response = await axiosInstance.get('/landlords', {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
            });
            
            const landlordProfile = response.data.find(landlord => 
                landlord.user_id === Number(loggedInUserId)
            );
            
            if (landlordProfile) {
                setProfileData(landlordProfile);
                setShowProfile(true);
                setShowRegistrationForm(false);
                setError('');
            } else {
                setError('Landlord profile not found. Please register first.');
            }
        } catch (err) {
            console.error('Profile fetch error:', err);
            setError('Failed to load profile. Please try again.');
        }
    };

    return (
        <Container maxWidth="lg">
            <Box mt={8} p={4} boxShadow={3} bgcolor="white">
                <Typography variant="h4" gutterBottom>
                    Landlord Dashboard
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
                            Register as Landlord
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
                                label="Land Type"
                                name="land_type"
                                value={formData.land_type}
                                onChange={handleInputChange}
                                margin="normal"
                                required
                            />
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
                                label="Location"
                                name="location"
                                value={formData.location}
                                onChange={handleInputChange}
                                margin="normal"
                                required
                            />
                            
                            <Box mt={2}>
                                <Typography variant="subtitle1" gutterBottom>
                                    Land Images
                                </Typography>
                                <input
                                    type="file"
                                    multiple
                                    accept="image/*"
                                    onChange={handleFileChange}
                                    style={{ marginBottom: '1rem' }}
                                />
                                {selectedFiles.length > 0 && (
                                    <Typography variant="body2">
                                        Selected files: {selectedFiles.map(file => file.name).join(', ')}
                                    </Typography>
                                )}
                            </Box>

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
                            Landlord Profile
                        </Typography>
                        <Box sx={{ mt: 2 }}>
                            <Typography><strong>Landlord ID:</strong> {profileData.id}</Typography>
                            <Typography><strong>Land Type:</strong> {profileData.land_type}</Typography>
                            <Typography><strong>Acres:</strong> {profileData.acres}</Typography>
                            <Typography><strong>Location:</strong> {profileData.location}</Typography>
                            {profileData.images_list && profileData.images_list.length > 0 && (
                                <Box mt={2}>
                                    <Typography><strong>Images:</strong></Typography>
                                    <Box display="flex" gap={2} mt={1}>
                                        {profileData.images_list.map((image, index) => (
                                            <img 
                                                key={index}
                                                src={image}
                                                alt={`Land image ${index + 1}`}
                                                style={{ maxWidth: '200px', height: 'auto' }}
                                            />
                                        ))}
                                    </Box>
                                </Box>
                            )}
                        </Box>
                    </Paper>
                )}
            </Box>
        </Container>
    );
};

export default LandlordDashboard;
