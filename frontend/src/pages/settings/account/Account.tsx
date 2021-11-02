import React from 'react';

import { Box, Divider, Grid, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

import ContentHeader from '../../../components/ContentHeader';
import PasswordForm from '../../../features/settings/account/PasswordForm';
import DeleteAccountForm from '../../../features/settings/account/DeleteAccountForm';
import SettingsMenu from '../../../features/settings/SettingsMenu';

const useStyles = makeStyles((theme) => ({
  titleDanger: { color: theme.palette.error.main },
}));

function AccountPage() {
  const classes = useStyles();

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
                <Typography variant="h4" className={classes.titleDanger}>
                  Delete account
                </Typography>
                <Divider />
              </Box>
              <Grid item md={4}>
                <DeleteAccountForm />
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </Box>
    </>
  );
}

export default AccountPage;
