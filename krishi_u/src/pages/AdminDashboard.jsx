import { useEffect, useState } from 'react';
import axiosInstance from '../api/axios';

import { Container, Box, Typography, Paper, Table, TableBody, TableCell, TableHead, TableRow, Button } from '@mui/material';

const AdminDashboard = () => {
    const [dashboardStats, setDashboardStats] = useState(null);
    const [error, setError] = useState('');
    const [listings, setListings] = useState([]);
    const [showFarmers, setShowFarmers] = useState(false);
    const [showLandlords, setShowLandlords] = useState(false);

    useEffect(() => {
        const fetchDashboardStats = async () => {
            try {
                const response = await axiosInstance.get('/dashboard', {
                    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
                });
                setDashboardStats(response.data);
            } catch (err) {
                setError('Failed to load dashboard statistics. Please try again.');
            }
        };

        fetchDashboardStats();
    }, []);

    const handleFetchListings = async (type) => {
        try {
            const endpoint = type === 'farmers' ? '/farmers' : '/landlords';
            const response = await axiosInstance.get(endpoint, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
            });
            setListings(response.data);
            setShowFarmers(type === 'farmers');
            setShowLandlords(type === 'landlords');
        } catch (err) {
            setError(`Failed to load ${type} data. Please try again.`);
        }
    };

    return (
        <Container maxWidth="lg">
            <Box mt={8} p={4} boxShadow={3} bgcolor="white">
                <Typography variant="h4" gutterBottom>
                    Admin Dashboard
                </Typography>
                
                {error && (
                    <Typography color="error" gutterBottom>
                        {error}
                    </Typography>
                )}

                {dashboardStats && (
                    <>
                        <Paper sx={{ mb: 4 }}>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Statistic</TableCell>
                                        <TableCell>Value</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    <TableRow>
                                        <TableCell>Total Farmers</TableCell>
                                        <TableCell>{dashboardStats.total_farmers}</TableCell>
                                    </TableRow>
                                    <TableRow>
                                        <TableCell>Total Landlords</TableCell>
                                        <TableCell>{dashboardStats.total_landlords}</TableCell>
                                    </TableRow>
                                    <TableRow>
                                        <TableCell>Total Spaces</TableCell>
                                        <TableCell>{dashboardStats.total_spaces}</TableCell>
                                    </TableRow>
                                    <TableRow>
                                        <TableCell>Total Connections</TableCell>
                                        <TableCell>{dashboardStats.total_connections}</TableCell>
                                    </TableRow>
                                    <TableRow>
                                        <TableCell>Total Acres</TableCell>
                                        <TableCell>{dashboardStats.total_acres}</TableCell>
                                    </TableRow>
                                </TableBody>
                            </Table>
                        </Paper>

                        <Box display="flex" gap={2} mb={4}>
                            <Button 
                                variant="contained" 
                                onClick={() => handleFetchListings('farmers')}
                                color={showFarmers ? "primary" : "inherit"}
                            >
                                View All Farmers
                            </Button>
                            <Button 
                                variant="contained" 
                                onClick={() => handleFetchListings('landlords')}
                                color={showLandlords ? "primary" : "inherit"}
                            >
                                View All Landlords
                            </Button>
                        </Box>

                        {(showFarmers || showLandlords) && listings.length > 0 && (
                            <Paper>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>ID</TableCell>
                                            <TableCell>User ID</TableCell>
                                            <TableCell>Land Type</TableCell>
                                            <TableCell>Location</TableCell>
                                            <TableCell>Acres</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {listings.map((item) => (
                                            <TableRow key={item.id}>
                                                <TableCell>{item.id}</TableCell>
                                                <TableCell>{item.user_id}</TableCell>
                                                <TableCell>{item.land_type}</TableCell>
                                                <TableCell>{item.location}</TableCell>
                                                <TableCell>{item.acres}</TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </Paper>
                        )}
                    </>
                )}

                {!dashboardStats && (
                    <Typography variant="body1" color="textSecondary">
                        Loading dashboard statistics...
                    </Typography>
                )}
            </Box>
        </Container>
    );
};

export default AdminDashboard;
