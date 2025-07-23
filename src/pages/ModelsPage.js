// src/pages/ModelsPage.js
import React, { useState, useEffect } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getMyModels, getPublicModels } from '../services/firebaseService';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import {
    Container, Typography, Button, Box, Grid, Card, CardContent, CardActions, Divider, Paper
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import PublicIcon from '@mui/icons-material/Public';

const ModelList = ({ models }) => (
    <Grid container spacing={3}>
        {models.map((model) => (
            <Grid item xs={12} sm={6} md={4} key={model.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <CardContent sx={{ flexGrow: 1 }}>
                        <Typography variant="h5" component="h2" gutterBottom>
                            {model.name} {model.isPublic && <PublicIcon fontSize="small" color="disabled" />}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" noWrap>
                            Provider: {model.provider} | Model: {model.modelString}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1, display: '-webkit-box', WebkitBoxOrient: 'vertical', WebkitLineClamp: 2, overflow: 'hidden' }}>
                            {model.description || 'No description provided.'}
                        </Typography>
                    </CardContent>
                    <CardActions>
                        <Button size="small" component={RouterLink} to={`/model/${model.id}`}>
                            View
                        </Button>
                        <Button size="small" component={RouterLink} to={`/model/${model.id}/edit`}>
                            Edit
                        </Button>
                    </CardActions>
                </Card>
            </Grid>
        ))}
    </Grid>
);

const ModelsPage = () => {
    const { currentUser } = useAuth();
    const navigate = useNavigate();
    const [myModels, setMyModels] = useState([]);
    const [publicModels, setPublicModels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!currentUser) return;
        const fetchModels = async () => {
            try {
                setLoading(true);
                const [userModels, pubModels] = await Promise.all([
                    getMyModels(currentUser.uid),
                    getPublicModels(currentUser.uid)
                ]);
                setMyModels(userModels);
                setPublicModels(pubModels);
            } catch (err) {
                console.error("Error fetching models:", err);
                setError("Failed to load models.");
            } finally {
                setLoading(false);
            }
        };
        fetchModels();
    }, [currentUser]);

    if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}><LoadingSpinner /></Box>;

    return (
        <Container maxWidth="lg">
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" component="h1">Models</Typography>
                <Button variant="contained" startIcon={<AddIcon />} onClick={() => navigate('/create-model')}>
                    New Model
                </Button>
            </Box>

            {error && <ErrorMessage message={error} />}

            <Typography variant="h5" component="h2" gutterBottom>Your Models</Typography>
            {myModels.length > 0 ? (
                <ModelList models={myModels} />
            ) : (
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                    <Typography color="text.secondary">You haven't created any models yet.</Typography>
                </Paper>
            )}

            <Divider sx={{ my: 4 }} />

            <Typography variant="h5" component="h2" gutterBottom>Public Models</Typography>
            {publicModels.length > 0 ? (
                <ModelList models={publicModels} />
            ) : (
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                    <Typography color="text.secondary">No public models are available.</Typography>
                </Paper>
            )}
        </Container>
    );
};

export default ModelsPage;  