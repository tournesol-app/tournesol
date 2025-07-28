import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Grid2 } from '@mui/material';

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
    <Grid2
      container
      spacing={4}
      direction="column"
      sx={{
        alignItems: 'stretch',
      }}
    >
      <Grid2>
        <SettingsHeading
          id="notifications"
          text={t('generalUserSettingsForm.emailNotifications')}
        />
      </Grid2>
      <Grid2>
        <Alert severity="info">
          <AlertTitle>
            <strong>
              {t('generalUserSettingsForm.joinTheResearchStudies')}
            </strong>
          </AlertTitle>
          {t('generalUserSettingsForm.joinTheResearchStudiesDesc')}
        </Alert>
      </Grid2>
      <Grid2>
        <NotificationsLang
          value={notificationsLang}
          onChange={setNotificationsLang}
        />
      </Grid2>
      <Grid2
        container
        spacing={1}
        direction="column"
        sx={{
          alignItems: 'stretch',
        }}
      >
        <Grid2>
          <NotificationsEmailResearch
            value={notificationsEmailResearch}
            onChange={setNotificationsEmailResearch}
          />
        </Grid2>
        <Grid2>
          <NotificationsEmailNewFeatures
            value={notificationsEmailNewFeatures}
            onChange={setNotificationsEmailNewFeatures}
          />
        </Grid2>
      </Grid2>
    </Grid2>
  );
};

export default GeneralUserSettingsForm;
