import React from 'react';

import Box from '@material-ui/core/Box';
import Grid from '@material-ui/core/Grid';

import ContentHeader from '../../../components/ContentHeader';
import SettingsMenu from '../../../features/settings/SettingsMenu';
import ProfileForm from '../../../features/settings/profile/ProfileForm';
import Section from 'src/components/Section';

function ProfilePage() {
  return (
    <>
      <ContentHeader title="Settings > Profile" />
      <Box m={4}>
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
            <Section title="Profile" xs={12}>
              <ProfileForm />
            </Section>
          </Grid>
        </Grid>
      </Box>
    </>
  );
}

export default ProfilePage;
