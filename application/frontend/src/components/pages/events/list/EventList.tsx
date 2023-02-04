import React from 'react';
import { Box } from '@mui/material';
import { NewEventsContainer } from './NewEventsContainer';
import { OldEventsContainer } from './OldEventsContainer';
import { EventsContainer } from './EventsContainer';

const EventList: React.FC = () => (
    <Box
        sx={{
            height: '100%',
            display: 'flex',
            gap: 1,
            flexWrap: 'wrap',
        }}
    >
        <EventsContainer title="events.list.futureEvents.title">
            <NewEventsContainer />
        </EventsContainer>
        <EventsContainer title="events.list.pastEvents.title">
            <OldEventsContainer />
        </EventsContainer>
    </Box>
);

export { EventList };
