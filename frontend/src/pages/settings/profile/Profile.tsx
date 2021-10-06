import React from 'react';

import Box from '@material-ui/core/Box';
import Grid from '@material-ui/core/Grid';

import ContentHeader from '../../../components/ContentHeader';
import SettingsMenu from '../../../features/settings/SettingsMenu';

function ProfilePage() {
  return (
    <>
      <ContentHeader title="Settings > Profile" />
      <Box m={4}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={12} md={2}>
            <SettingsMenu />
          </Grid>
        </Grid>
      </Box>
    </>
  );
}

export default ProfilePage;
