import React from 'react';
import { useTranslation } from 'react-i18next';

import Grid2 from '@mui/material/Grid2';

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
        <Grid2 container spacing={4}>
          <Grid2 size={settingsMenuBreakpoints}>
            <SettingsMenu />
          </Grid2>
          <Grid2
            container
            direction="column"
            spacing={mainSectionGridSpacing}
            size={mainSectionBreakpoints}
            sx={{
              alignItems: 'stretch',
            }}
          >
            <SettingsSection title={t('profile')} {...subSectionBreakpoints}>
              <ProfileForm />
            </SettingsSection>
          </Grid2>
        </Grid2>
      </ContentBox>
    </>
  );
}

export default ProfilePage;
