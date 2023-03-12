import React, {useState} from 'react';
import { Box, Typography } from '@mui/material';
import { NewEventsContainer } from './NewEventsContainer';
import { OldEventsContainer } from './OldEventsContainer';
import { EventsContainer } from './EventsContainer';
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import {Button3D} from "../../Button3D";
import DialogNewEvent from "./DialogNewEvent";
import {useTranslation} from "react-i18next";

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

const TabPanel: React.FC<TabPanelProps> = (props) => {
    const { children, value, index, ...other } = props;

    return (
        <Box
            role="tabpanel"
            hidden={value !== index}
            id={`simple-tabpanel-${index}`}
            aria-labelledby={`simple-tab-${index}`}
            sx={{
                display: 'contents',
            }}
            {...other}
        >
            {value === index && (
                <Box sx={(theme) => ({ p: 1, display: 'flex', flexDirection: 'column', overflow: 'auto' })}>
                    {children}
                </Box>
            )}
        </Box>
    );
};

const EventList: React.FC = () => {
    const [value, setValue] = React.useState(0);

    const handleChange = (event: React.SyntheticEvent, newValue: number) => {
        setValue(newValue);
    };

    const { t } = useTranslation();

    const [showNewModal, setShowNewModal] = useState(false);

    const toggleCreateNewForm = () => {
        setShowNewModal((val) => !val);
    };

    return (
        <Box
            sx={{
                width: '30vw',
                minWidth: '600px',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'normal',
            }}
        >
            <Tabs
                value={value}
                onChange={handleChange}
                textColor="primary"
                indicatorColor="primary"
                aria-label="Event tabs"
                sx={(theme) => ({ width: '100%', backgroundColor: theme.palette.secondary.main })}
            >
                <Tab value={0} label={t('events.list.futureEvents.title')} sx={{ flex: 1, fontWeight: 700 }} />
                <Tab value={1} label={t('events.list.pastEvents.title')} sx={{ flex: 1, fontWeight: 700 }} />
            </Tabs>
            <TabPanel value={value} index={0}>
                <Box sx={{ marginBottom: 1 }}>
                    <DialogNewEvent open={showNewModal} handleClose={toggleCreateNewForm} />
                    <Button3D text={t('events.list.newEventButton')} onClick={toggleCreateNewForm} />
                </Box>
                <NewEventsContainer />
            </TabPanel>
            <TabPanel value={value} index={1}>
                <OldEventsContainer />
            </TabPanel>
        </Box>
    );
}

export { EventList };
