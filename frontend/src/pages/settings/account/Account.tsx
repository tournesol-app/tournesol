import React from 'react';

import { useHistory } from 'react-router-dom';
import { Box, Divider, Grid, Typography, Button } from '@material-ui/core';

import ContentHeader from '../../../components/ContentHeader';
import PasswordForm from '../../../features/settings/account/PasswordForm';
import SettingsMenu from '../../../features/settings/SettingsMenu';
import { deleteAccountAPI } from 'src/features/account/accountAPI';

function AccountPage() {
  const history = useHistory();
  const deleteAccount = async () => {
    await deleteAccountAPI();
    history.push('/');
  };

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
            <Grid item>
              <Box marginBottom={2} marginTop={2}>
                <Typography variant="h4" color="secondary">
                  Delete account
                </Typography>
                <Divider />
              </Box>
            </Grid>
            <Grid item md={4}>
              <Button
                onClick={deleteAccount}
                color="secondary"
                fullWidth
                variant="contained"
              >
                Delete your account
              </Button>
            </Grid>
          </Grid>
        </Grid>
      </Box>
    </>
  );
}

export default AccountPage;
