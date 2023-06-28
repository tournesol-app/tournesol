import React from 'react';
import { useTranslation } from 'react-i18next';

import Grid from '@mui/material/Grid';

import { ContentBox, ContentHeader, SettingsSection } from 'src/components';
import SettingsMenu from 'src/features/settings/SettingsMenu';
import ProfileForm from 'src/features/settings/profile/ProfileForm';
import {
  mainSectionBreakpoints,
  mainSectionGridSpacing,
  settingsMenuBreakpoints,
  subSectionBreakpoints,
} from 'src/pages/settings/layout';

function ProfilePage() {
  const { t } = useTranslation();

  return (
    <>
      <ContentHeader title={`${t('settings.title')} > ${t('profile')}`} />
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
            spacing={mainSectionGridSpacing}
            {...mainSectionBreakpoints}
          >
            <SettingsSection title={t('profile')} {...subSectionBreakpoints}>
              <ProfileForm />
            </SettingsSection>
          </Grid>
        </Grid>
      </ContentBox>
    </>
  );
}

export default ProfilePage;
