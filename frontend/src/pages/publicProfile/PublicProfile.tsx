import React from 'react';
import { useTranslation } from 'react-i18next';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import { ContentHeader, SettingsSection } from 'src/components';
import PublicProfileForm from 'src/features/profile/PublicProfileForm';
/*
this is only a display page
*/
function PublicProfile() {
  const { t } = useTranslation();
  return (
    <>
      <ContentHeader title={`${t('Profile')}`} />
      <Box m={4}>
        <Grid container spacing={4}>
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
              <PublicProfileForm />
            </SettingsSection>
          </Grid>
        </Grid>
      </Box>
    </>
  );
}

export default PublicProfile;
