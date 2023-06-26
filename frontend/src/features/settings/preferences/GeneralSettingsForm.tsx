import React from 'react';
import { useTranslation } from 'react-i18next';

import { Grid, Typography } from '@mui/material';
import NotificationsEmailResearch from './fields/NotificationsEmailResearch';
import NotificationsEmailNewFeatures from './fields/NotificationsEmailNewFeatures';

interface GeneralSettingsFormProps {
  notificationsEmailResearch: boolean;
  setNotificationsEmailResearch: (target: boolean) => void;
}

/**
 * Display a form allowing the logged users to update their general preferences
 */
const GeneralSettingsForm = ({
  notificationsEmailResearch,
  setNotificationsEmailResearch,
}: GeneralSettingsFormProps) => {
  const { t } = useTranslation();

  return (
    <>
      <Grid
        container
        spacing={4}
        mb={4}
        direction="column"
        alignItems="stretch"
      >
        <Grid item>
          <Typography id="notifications" variant="h6">
            {t('generalUserSettings.notifications')}
          </Typography>
        </Grid>
        <Grid item>
          <NotificationsEmailResearch
            value={notificationsEmailResearch}
            onChange={setNotificationsEmailResearch}
          />
        </Grid>
        <Grid item>
          <NotificationsEmailNewFeatures
            value={notificationsEmailResearch}
            onChange={setNotificationsEmailResearch}
          />
        </Grid>
      </Grid>
    </>
  );
};

export default GeneralSettingsForm;
