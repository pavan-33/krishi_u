import { useEffect, useState } from 'react';
import axiosInstance from '../api/axios';

import { Container, Box, Typography, Paper, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';

const CollaborationSpace = () => {
    const [collaborations, setCollaborations] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchCollaborations = async () => {
            try {
                
                const response = await axiosInstance.get('/api/collaborations', {
                    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
                });
                setCollaborations(response.data);
            } catch (err) {
                setError('Failed to load collaborations. Please try again.');
            }
        };

        fetchCollaborations();
    }, []);

    return (
        <Container maxWidth="lg">
            <Box mt={8} p={4} boxShadow={3} bgcolor="white">
                <Typography variant="h4" gutterBottom>
                    Collaboration Space
                </Typography>
                {error && <Typography color="error">{error}</Typography>}
                <Paper>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Farmer</TableCell>
                                <TableCell>Landlord</TableCell>
                                <TableCell>Crop</TableCell>
                                <TableCell>Status</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {collaborations.map((collaboration) => (
                                <TableRow key={collaboration.id}>
                                    <TableCell>{collaboration.farmer}</TableCell>
                                    <TableCell>{collaboration.landlord}</TableCell>
                                    <TableCell>{collaboration.crop}</TableCell>
                                    <TableCell>{collaboration.status}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </Paper>
            </Box>
        </Container>
    );
};

export default CollaborationSpace;
