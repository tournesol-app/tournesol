import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Grid } from '@mui/material';

import { Notifications_langEnum } from 'src/services/openapi';

import NotificationsEmailResearch from './fields/NotificationsEmailResearch';
import NotificationsEmailNewFeatures from './fields/NotificationsEmailNewFeatures';
import NotificationsLang from './fields/NotificationsLang';
import SettingsHeading from './SettingsHeading';

interface GeneralSettingsFormProps {
  notificationsLang: Notifications_langEnum;
  setNotificationsLang: (lang: Notifications_langEnum) => void;
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
  notificationsLang,
  setNotificationsLang,
  notificationsEmailResearch,
  setNotificationsEmailResearch,
  notificationsEmailNewFeatures,
  setNotificationsEmailNewFeatures,
}: GeneralSettingsFormProps) => {
  const { t } = useTranslation();

  return (
    <Grid container spacing={4} direction="column" alignItems="stretch">
      <Grid item>
        <SettingsHeading
          id="notifications"
          text={t('generalUserSettingsForm.emailNotifications')}
        />
      </Grid>
      <Grid item>
        <Alert severity="info">
          <AlertTitle>
            <strong>
              {t('generalUserSettingsForm.joinTheResearchStudies')}
            </strong>
          </AlertTitle>
          {t('generalUserSettingsForm.joinTheResearchStudiesDesc')}
        </Alert>
      </Grid>
      <Grid item>
        <NotificationsLang
          value={notificationsLang}
          onChange={setNotificationsLang}
        />
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
