import React from 'react';
import { useTranslation } from 'react-i18next';

import Grid from '@mui/material/Grid';

import { ContentBox, ContentHeader, SettingsSection } from 'src/components';
import SettingsMenu from 'src/features/settings/SettingsMenu';
import ProfileForm from 'src/features/settings/profile/ProfileForm';

import { mainSectionBp, settingsMenuBp } from '../layout';

function ProfilePage() {
  const { t } = useTranslation();

  // subSectionBreakP can be changed independently of mainSectionBp
  const subSectionBreakP = mainSectionBp;
  return (
    <>
      <ContentHeader title={`${t('settings.title')} > ${t('profile')}`} />
      <ContentBox maxWidth="xl">
        <Grid container spacing={4}>
          <Grid item {...settingsMenuBp}>
            <SettingsMenu />
          </Grid>
          <Grid
            container
            item
            direction="column"
            alignItems="stretch"
            {...mainSectionBp}
          >
            <SettingsSection title={t('profile')} {...subSectionBreakP}>
              <ProfileForm />
            </SettingsSection>
          </Grid>
        </Grid>
      </ContentBox>
    </>
  );
}

export default ProfilePage;
