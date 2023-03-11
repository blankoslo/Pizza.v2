import React from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Card, IconButton, Typography } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { ApiGroup } from '../../../api/GroupService';

interface Props {
    group: ApiGroup;
    deleteGroupButton: (id: string) => void;
}

const GroupEntry: React.FC<Props> = ({ group, deleteGroupButton }) => {
    const { t } = useTranslation();

    return (
        <Card
            sx={{
                display: 'flex',
                flexDirection: 'row',
                position: 'relative',
                marginBottom: '20px',
                padding: 3,
            }}
        >
            <Box
                sx={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                }}
            >
                <Typography variant="h5" component="span">
                    {`${group.name} (${group.members.length} ${t('groups.list.entry.numberOf')})`}
                </Typography>
            </Box>
            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                }}
            >
                <IconButton
                    sx={{
                        height: 'fit-content',
                    }}
                    size="large"
                    onClick={() => deleteGroupButton(group.id)}
                >
                    <DeleteIcon fontSize="large" />
                </IconButton>
            </Box>
        </Card>
    );
};

export { GroupEntry };
