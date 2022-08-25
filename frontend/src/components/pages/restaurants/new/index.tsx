import { Box } from '@mui/material';
import * as React from 'react';
import { RestaurantCreator } from './RestaurantCreator';

const NewRestaurantPage: React.FC = () => (
    <Box
        sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
        }}
    >
        <RestaurantCreator />
    </Box>
);

export default NewRestaurantPage;
