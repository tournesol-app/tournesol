import React from 'react';
import { useTranslation } from 'react-i18next';

import { Grid } from '@mui/material';

import { ContentBox, ContentHeader, SettingsSection } from 'src/components';
import UserSettingsForm from 'src/features/settings/preferences/videos/UserSettingsForm';
import SettingsMenu from 'src/features/settings/SettingsMenu';
import {
  mainSectionBreakpoints,
  settingsMenuBreakpoints,
} from 'src/pages/settings/layout';

function PreferencePage() {
  const { t } = useTranslation();

  // subSectionBreakP can be changed independently of mainSectionBp
  const subSectionBreakpoints = mainSectionBreakpoints;
  return (
    <>
      <ContentHeader
        title={`${t('settings.title')} > ${t('preferences.preferences')}`}
      />
      <ContentBox maxWidth="xl">
        <Grid container spacing={4}>
          <Grid item {...settingsMenuBreakpoints}>
            <SettingsMenu />
          </Grid>
          <Grid
            container
            item
            direction="column"
            alignItems="stretch"
            {...mainSectionBreakpoints}
          >
            <SettingsSection
              title={t('preferences.preferencesOfThePoll')}
              {...subSectionBreakpoints}
            >
              <UserSettingsForm />
            </SettingsSection>
          </Grid>
        </Grid>
      </ContentBox>
    </>
  );
}

export default PreferencePage;
