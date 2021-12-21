import React from 'react';

import { Box, Grid, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

import ContentHeader from 'src/components/ContentHeader';
import PasswordForm from 'src/features/settings/account/PasswordForm';
import DeleteAccountForm from 'src/features/settings/account/DeleteAccountForm';
import EmailAddressForm from 'src/features/settings/account/EmailAddressForm';
import ExportAllDataForm from 'src/features/settings/account/ExportAllDataForm';
import SettingsMenu from 'src/features/settings/SettingsMenu';
import { SettingsSection } from 'src/components';

const useStyles = makeStyles((theme) => ({
  titleDanger: { color: theme.palette.error.main },
}));

export const AccountPage = () => {
  const classes = useStyles();
  return (
    <>
      <ContentHeader title="Settings > Account" />
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
            spacing={3}
          >
            <SettingsSection title="Change email address" xs={12}>
              <EmailAddressForm />
            </SettingsSection>
            <SettingsSection title="Change password" xs={12} md={6}>
              <PasswordForm />
            </SettingsSection>
            <Box marginTop={8} />
            <SettingsSection title="Export all data" xs={12}>
              <ExportAllDataForm />
            </SettingsSection>
            <SettingsSection
              title={
                <Typography variant="h4" className={classes.titleDanger}>
                  Delete account
                </Typography>
              }
              md={6}
            >
              <DeleteAccountForm />
            </SettingsSection>
          </Grid>
        </Grid>
      </Box>
    </>
  );
};

export default AccountPage;
