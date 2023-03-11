import React from 'react';
import { Box } from '@mui/material';
import { GroupList } from './GroupList';

const GroupsPage: React.FC = () => {
    return (
        <Box
            sx={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
            }}
        >
            <GroupList />
        </Box>
    );
};

export default GroupsPage;
