import React from 'react';
import { useTranslation } from 'react-i18next';

import { Grid, Typography } from '@mui/material';

import NotificationsEmailResearch from './fields/NotificationsEmailResearch';
import NotificationsEmailNewFeatures from './fields/NotificationsEmailNewFeatures';

interface GeneralSettingsFormProps {
  notificationsEmailResearch: boolean;
  setNotificationsEmailResearch: (target: boolean) => void;
  notificationsEmailNewFeatures: boolean;
  setNotificationsEmailNewFeatures: (target: boolean) => void;
}

/**
 * Display a form allowing the logged users to update their general
 * preferences.
 */
const GeneralUserSettingsForm = ({
  notificationsEmailResearch,
  setNotificationsEmailResearch,
  notificationsEmailNewFeatures,
  setNotificationsEmailNewFeatures,
}: GeneralSettingsFormProps) => {
  const { t } = useTranslation();

  return (
    <Grid container spacing={2} mb={2} direction="column" alignItems="stretch">
      <Grid item>
        <Typography id="notifications" variant="h6">
          {t('generalUserSettingsForm.emailNotifications')}
        </Typography>
      </Grid>
      <Grid item container spacing={1} direction="column" alignItems="stretch">
        <Grid item>
          <NotificationsEmailResearch
            value={notificationsEmailResearch}
            onChange={setNotificationsEmailResearch}
          />
        </Grid>
        <Grid item>
          <NotificationsEmailNewFeatures
            value={notificationsEmailNewFeatures}
            onChange={setNotificationsEmailNewFeatures}
          />
        </Grid>
      </Grid>
    </Grid>
  );
};

export default GeneralUserSettingsForm;
