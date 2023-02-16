import { Box } from '@mui/material';
import * as React from 'react';
import { EventList } from './EventList';

const EventPage: React.FC = () => (
    <Box
        sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
        }}
    >
        <EventList />
    </Box>
);

export default EventPage;
