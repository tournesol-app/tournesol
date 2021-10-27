import React from 'react';

import Box from '@material-ui/core/Box';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';

import ContentHeader from '../../../components/ContentHeader';
import SettingsMenu from '../../../features/settings/SettingsMenu';
import ProfileForm from '../../../features/settings/profile/ProfileForm';

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
            <Grid item>
              <Box marginBottom={2}>
                <Typography variant="h4" color="secondary">
                  Profile
                </Typography>
                <Divider />
              </Box>
            </Grid>
            <Grid item md={6}>
              <ProfileForm />
            </Grid>
          </Grid>
        </Grid>
      </Box>
    </>
  );
}

export default ProfilePage;
