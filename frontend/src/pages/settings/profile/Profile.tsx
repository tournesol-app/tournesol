import React from 'react';
import { useTranslation } from 'react-i18next';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';

import { ContentHeader, SettingsSection } from 'src/components';
import SettingsMenu from '../../../features/settings/SettingsMenu';
import ProfileForm from '../../../features/settings/profile/ProfileForm';

function ProfilePage() {
  const { t } = useTranslation();
  return (
    <>
      <ContentHeader title={`${t('settings.title')} > ${t('profile')}`} />
      <Box
        m={4}
        // Push the global footer away, to avoid displaying it in the middle
        // of the screen.
        // TODO: try to use the custom <ContentBox> instead of <Box>
        minHeight="523px"
      >
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
