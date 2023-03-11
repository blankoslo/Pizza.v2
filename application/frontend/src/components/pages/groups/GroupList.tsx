import React, { useState } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { useInfiniteGroups } from '../../../hooks/useGroups';
import { groupsDefaultQueryKey, useGroupService } from '../../../api/GroupService';
import { toast } from 'react-toastify';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { DialogDeleteWarning } from './DialogDeleteWarning';
import { DialogNew } from './DialogNew';
import { GroupEntry } from './GroupEntry';
import { useTranslation } from 'react-i18next';
import { Button3D } from '../../Button3D';
import { InfinityList } from '../../InfinityList';

export const GroupList: React.FC = () => {
    const { t } = useTranslation();
    const { deleteGroup } = useGroupService();

    const [showNewModal, setShowNewModal] = useState(false);
    const [deleteId, setDeleteId] = useState<string>();
    const { isLoading, data: _groups, hasNextPage, fetchNextPage } = useInfiniteGroups({ page_size: 10 });
    const hasMore = isLoading ? true : hasNextPage ?? false;
    const groups = _groups?.pages.flatMap((page) => page.data);

    const queryClient = useQueryClient();

    const addMutation = useMutation((id: string) => deleteGroup(id), {
        onSuccess: () => {
            toast.success(t('groups.delete.mutation.onSuccess'));
        },
        onError: () => {
            toast.error(t('groups.delete.mutation.onError'));
        },
        onSettled: () => {
            queryClient.invalidateQueries([groupsDefaultQueryKey]);
        },
    });

    const deleteGroupButton = (id: string) => {
        setDeleteId(id);
    };

    const deleteGroupCallback = () => {
        if (deleteId) {
            addMutation.mutate(deleteId);
            setDeleteId(undefined);
        }
    };

    const deleteGroupCancel = () => {
        setDeleteId(undefined);
    };

    const toggleCreateNewForm = () => {
        setShowNewModal((val) => !val);
    };

    const INFINITY_LIST_ID = 'groupInfinityListContainer';

    return (
        <>
            <DialogDeleteWarning open={!!deleteId} handleClose={deleteGroupCancel} onDelete={deleteGroupCallback} />
            <DialogNew open={showNewModal} handleClose={toggleCreateNewForm} />
            <Paper
                sx={(theme) => ({
                    padding: 1,
                    height: '100%',
                    width: '30vw',
                    minWidth: '600px',
                    backgroundColor: theme.palette.secondary.main,
                    borderRadius: 3,
                    display: 'flex',
                    flexDirection: 'column',
                })}
            >
                <Box
                    sx={{
                        fontSize: '1.2rem',
                        fontWeight: 'bold',
                        margin: '24px 24px 12px 24px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                    }}
                >
                    <Typography variant="h5" component="h2" align="center">
                        {t('groups.list.title')}
                    </Typography>
                    <Button3D text={t('groups.list.newGroupButton')} onClick={toggleCreateNewForm} />
                </Box>
                <Box
                    id={INFINITY_LIST_ID}
                    sx={{
                        overflow: 'auto',
                    }}
                >
                    {groups && (
                        <InfinityList
                            parentId={INFINITY_LIST_ID}
                            fetchData={() => fetchNextPage()}
                            hasMore={hasMore}
                            items={groups.map((group) => (
                                <GroupEntry
                                    key={group.id}
                                    group={group}
                                    deleteGroupButton={deleteGroupButton}
                                />
                            ))}
                        />
                    )}
                    {groups && groups.length == 0 && (
                        <Box sx={{ display: 'flex', justifyContent: 'center' }}>{t('groups.list.noResults')}</Box>
                    )}
                </Box>
            </Paper>
        </>
    );
};
