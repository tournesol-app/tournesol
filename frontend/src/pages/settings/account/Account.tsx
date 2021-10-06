import React from 'react';

import Box from '@material-ui/core/Box';
import Divider from '@material-ui/core/Divider';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import ContentHeader from '../../../components/ContentHeader';
import PasswordForm from '../../../features/settings/account/PasswordForm';
import SettingsMenu from '../../../features/settings/SettingsMenu';

function AccountPage() {
  return (
    <>
      <ContentHeader title="Settings > Account" />
      <Box m={4}>
        <Grid container spacing={4}>
          <Grid item xs={12} sm={12} md={2}>
            <SettingsMenu />
          </Grid>
          <Grid
            container
            item
            direction="column"
            alignItems="stretch"
            xs={12}
            sm={12}
            md={10}
          >
            <Grid item>
              <Box marginBottom={2}>
                <Typography variant="h4" color="secondary">
                  Change password
                </Typography>
                <Divider />
              </Box>
            </Grid>
            <Grid item md={4}>
              <PasswordForm />
            </Grid>
          </Grid>
        </Grid>
      </Box>
    </>
  );
}

export default AccountPage;
