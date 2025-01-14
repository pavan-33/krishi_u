import { useState } from 'react';
import axiosInstance from '../api/axios';
import { useNavigate } from 'react-router-dom';
import {
    TextField,
    Button,
    Box,
    Typography,
    Container,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Paper,
    Stepper,
    Step,
    StepLabel,
    CircularProgress,
    Link,
    Alert,
    IconButton,
    InputAdornment
} from '@mui/material';
import {
    Person as PersonIcon,
    Email as EmailIcon,
    Phone as PhoneIcon,
    Lock as LockIcon,
    Visibility as VisibilityIcon,
    VisibilityOff as VisibilityOffIcon,
    CloudUpload as CloudUploadIcon
} from '@mui/icons-material';

const Register = () => {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        role: '',
        phone_number: '',
        land_handling_capacity: '',
        preferred_locations: '',
        soil_type: '',
        acres: '',
        location: '',
    });

    const [selectedFiles, setSelectedFiles] = useState([]);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const navigate = useNavigate();

    const handleInputChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleFileChange = (e) => {
        setSelectedFiles(Array.from(e.target.files));
    };

    const handleUploadImages = async (token) => {
        try {
            const formData = new FormData();
            selectedFiles.forEach(file => {
                formData.append('files', file);
            });

            console.log('Files being uploaded:', selectedFiles);

            const response = await axiosInstance.post('/upload/images', formData, {
                headers: {
                    'Authorization': `Bearer ${token}`,
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

    const handleRegister = async () => {
        setLoading(true);
        setError('');
        try {
            const userResponse = await axiosInstance.post('/register', {
                email: formData.email,
                password: formData.password,
                role: formData.role
            });

            console.log('User registration response:', userResponse.data);

            if (!userResponse.data.id) {
                throw new Error('User ID not received from registration');
            }

            if (formData.role === 'farmer') {
                const farmerData = {
                    user_id: userResponse.data.id,
                    phone_number: formData.phone_number,
                    land_handling_capacity: Number(formData.land_handling_capacity),
                    preferred_locations: formData.preferred_locations.split(',').map(loc => loc.trim())
                };
                
                await axiosInstance.post('/farmer/register', farmerData, {
                    headers: { Authorization: `Bearer ${userResponse.data.token}` }
                });
            } else if (formData.role === 'landlord') {
                let imageUrls = [];
                if (selectedFiles.length > 0) {
                    imageUrls = await handleUploadImages(userResponse.data.token);
                }
                
                const landlordData = {
                    user_id: userResponse.data.id,
                    phone_number: formData.phone_number,
                    soil_type: formData.soil_type,
                    acres: Number(formData.acres),
                    location: formData.location,
                    images: imageUrls
                };
                
                await axiosInstance.post('/landlord/register', landlordData, {
                    headers: { 
                        Authorization: `Bearer ${userResponse.data.token}`,
                        'Content-Type': 'application/json'
                    },
                });
            }

            setSuccess('Registration successful!');
            navigate('/login');
            
        } catch (err) {
            console.error('Registration error:', err);
            setLoading(false);
            setError(err.message || 'Registration failed. Please try again.');
        }
    };

    const isFormValid = () => {
        const baseFieldsValid = formData.email && formData.password && formData.role;
        
        if (!baseFieldsValid) return false;

        if (formData.role === 'farmer') {
            return formData.phone_number && 
                   formData.land_handling_capacity && 
                   formData.preferred_locations;
        }

        if (formData.role === 'landlord') {
            return formData.phone_number && 
                   formData.soil_type && 
                   formData.acres && 
                   formData.location;
        }

        return baseFieldsValid;
    };

    return (
        <Box
            sx={{
                minHeight: '100vh',
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: '#f0f2f5',
                p: 2
            }}
        >
            <Container 
                maxWidth="md" 
                sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                }}
            >
                <Paper
                    elevation={3}
                    sx={{
                        width: '100%',
                        maxWidth: 800,
                        p: { xs: 3, md: 6 },
                        borderRadius: 2,
                        bgcolor: '#ffffff',
                    }}
                >
                    <Box sx={{ mb: 4, textAlign: 'center' }}>
                        <Typography
                            variant="h4"
                            component="h1"
                            sx={{
                                fontWeight: 700,
                                color: 'primary.main',
                                mb: 2
                            }}
                        >
                            Create Your Account
                        </Typography>
                        <Typography
                            variant="body1"
                            color="text.secondary"
                            sx={{ mb: 3 }}
                        >
                            Join our platform to connect farmers and landlords
                        </Typography>
                    </Box>

                    {error && (
                        <Alert severity="error" sx={{ mb: 3 }}>
                            {error}
                        </Alert>
                    )}

                    {success && (
                        <Alert severity="success" sx={{ mb: 3 }}>
                            {success}
                        </Alert>
                    )}

                    <Box component="form" noValidate sx={{ mt: 1 }}>
                        <TextField
                            label="Email"
                            name="email"
                            fullWidth
                            required
                            value={formData.email}
                            onChange={handleInputChange}
                            sx={{ mb: 2 }}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <EmailIcon color="action" />
                                    </InputAdornment>
                                ),
                            }}
                        />

                        <TextField
                            label="Password"
                            name="password"
                            type={showPassword ? 'text' : 'password'}
                            fullWidth
                            required
                            value={formData.password}
                            onChange={handleInputChange}
                            sx={{ mb: 2 }}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <LockIcon color="action" />
                                    </InputAdornment>
                                ),
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <IconButton
                                            onClick={() => setShowPassword(!showPassword)}
                                            edge="end"
                                        >
                                            {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                                        </IconButton>
                                    </InputAdornment>
                                ),
                            }}
                        />

                        <FormControl fullWidth sx={{ mb: 3 }}>
                            <InputLabel>Role *</InputLabel>
                            <Select
                                name="role"
                                value={formData.role}
                                onChange={handleInputChange}
                                label="Role *"
                                startAdornment={
                                    <InputAdornment position="start">
                                        <PersonIcon color="action" />
                                    </InputAdornment>
                                }
                            >
                                <MenuItem value="admin">Admin</MenuItem>
                                <MenuItem value="farmer">Farmer</MenuItem>
                                <MenuItem value="landlord">Landlord</MenuItem>
                            </Select>
                        </FormControl>

                        {formData.role && formData.role !== 'admin' && (
                            <Paper
                                variant="outlined"
                                sx={{ p: 3, mb: 3, borderRadius: 2 }}
                            >
                                <Typography
                                    variant="h6"
                                    gutterBottom
                                    sx={{ color: 'primary.main', fontWeight: 600 }}
                                >
                                    {formData.role.charAt(0).toUpperCase() + formData.role.slice(1)} Details
                                </Typography>

                                <TextField
                                    label="Phone Number"
                                    name="phone_number"
                                    fullWidth
                                    required
                                    value={formData.phone_number}
                                    onChange={handleInputChange}
                                    placeholder="+1234567890"
                                    sx={{ mb: 2 }}
                                    InputProps={{
                                        startAdornment: (
                                            <InputAdornment position="start">
                                                <PhoneIcon color="action" />
                                            </InputAdornment>
                                        ),
                                    }}
                                />

                                {formData.role === 'farmer' && (
                                    <>
                                        <TextField
                                            label="Land Handling Capacity (acres)"
                                            name="land_handling_capacity"
                                            type="number"
                                            fullWidth
                                            required
                                            value={formData.land_handling_capacity}
                                            onChange={handleInputChange}
                                            sx={{ mb: 2 }}
                                        />
                                        <TextField
                                            label="Preferred Locations"
                                            name="preferred_locations"
                                            fullWidth
                                            required
                                            value={formData.preferred_locations}
                                            onChange={handleInputChange}
                                            helperText="Enter locations separated by commas"
                                            sx={{ mb: 2 }}
                                        />
                                    </>
                                )}

                                {formData.role === 'landlord' && (
                                    <>
                                        <TextField
                                            label="Soil Type"
                                            name="soil_type"
                                            fullWidth
                                            required
                                            value={formData.soil_type}
                                            onChange={handleInputChange}
                                            sx={{ mb: 2 }}
                                        />
                                        <TextField
                                            label="Acres"
                                            name="acres"
                                            type="number"
                                            fullWidth
                                            required
                                            value={formData.acres}
                                            onChange={handleInputChange}
                                            sx={{ mb: 2 }}
                                        />
                                        <TextField
                                            label="Location"
                                            name="location"
                                            fullWidth
                                            required
                                            value={formData.location}
                                            onChange={handleInputChange}
                                            sx={{ mb: 2 }}
                                        />
                                        
                                        <Box
                                            sx={{
                                                p: 3,
                                                border: '1px dashed',
                                                borderColor: 'primary.main',
                                                borderRadius: 2,
                                                textAlign: 'center'
                                            }}
                                        >
                                            <input
                                                type="file"
                                                multiple
                                                accept="image/*"
                                                onChange={handleFileChange}
                                                style={{ display: 'none' }}
                                                id="land-images-input"
                                            />
                                            <label htmlFor="land-images-input">
                                                <Button
                                                    variant="outlined"
                                                    component="span"
                                                    startIcon={<CloudUploadIcon />}
                                                >
                                                    Upload Land Images
                                                </Button>
                                            </label>
                                            {selectedFiles.length > 0 && (
                                                <Typography
                                                    variant="body2"
                                                    color="primary"
                                                    sx={{ mt: 2 }}
                                                >
                                                    Selected files: {selectedFiles.map(file => file.name).join(', ')}
                                                </Typography>
                                            )}
                                        </Box>
                                    </>
                                )}
                            </Paper>
                        )}

                        <Button
                            variant="contained"
                            fullWidth
                            size="large"
                            onClick={handleRegister}
                            disabled={!isFormValid() || loading}
                            sx={{
                                py: 1.5,
                                fontSize: '1.1rem',
                                fontWeight: 'bold',
                                mb: 2
                            }}
                        >
                            {loading ? (
                                <CircularProgress size={24} color="inherit" />
                            ) : (
                                'Register'
                            )}
                        </Button>

                        <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="body2" color="text.secondary">
                                Already have an account?{' '}
                                <Link
                                    component="button"
                                    variant="body2"
                                    onClick={() => navigate('/login')}
                                    sx={{ fontWeight: 600 }}
                                >
                                    Sign in
                                </Link>
                            </Typography>
                        </Box>
                    </Box>
                </Paper>
            </Container>
        </Box>
    );
};

export default Register;
