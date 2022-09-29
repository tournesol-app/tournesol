import React from 'react';
import { useTranslation } from 'react-i18next';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';

import { ContentHeader, SettingsSection } from 'src/components';
import SettingsMenu from '../../../features/settings/SettingsMenu';
import ProfileForm from '../../../features/settings/profile/ProfileForm';
import { topBarHeight } from 'src/features/frame/components/topbar/TopBar';
import { contentHeaderHeight } from 'src/components/ContentHeader';

function ProfilePage() {
  const { t } = useTranslation();

  // Push the global footer away, to avoid displaying it in the middle
  // of the screen.
  // TODO: try to use the custom <ContentBox> instead of <Box> to remove
  // this logic.
  const minHeight =
    window.innerHeight - topBarHeight - contentHeaderHeight - 224 - 32;

  return (
    <>
      <ContentHeader title={`${t('settings.title')} > ${t('profile')}`} />
      <Box m={4} minHeight={minHeight}>
        <Grid container spacing={4}>
          <Grid item xs={12} sm={12} md={3}>
            <SettingsMenu />
          </Grid>
          <Grid
            container
            item
            direction="column"
            alignItems="stretch"
            xs={12}
            sm={12}
            md={9}
          >
            <SettingsSection title={t('profile')} xs={12}>
              <ProfileForm />
            </SettingsSection>
          </Grid>
        </Grid>
      </Box>
    </>
  );
}

export default ProfilePage;
