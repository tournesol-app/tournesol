import React from 'react';

import Box from '@material-ui/core/Box';
import Grid from '@material-ui/core/Grid';

import ContentHeader from '../../../components/ContentHeader';
import SettingsMenu from '../../../features/settings/SettingsMenu';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import BuildIcon from '@material-ui/icons/Build';

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
              <Typography paragraph>
                <BuildIcon color="primary" />
                &nbsp;&nbsp;Page under construction...&nbsp;&nbsp;
                <BuildIcon color="primary" />
              </Typography>
            </Grid>
          </Grid>
        </Grid>
      </Box>
    </>
  );
}

export default ProfilePage;
