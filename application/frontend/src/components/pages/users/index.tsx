import { Box } from '@mui/material';
import * as React from 'react';
import { UserList } from './UserList';

const UsersPage: React.FC = () => (
    <Box
        sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
        }}
    >
        <UserList />
    </Box>
);

export default UsersPage;
