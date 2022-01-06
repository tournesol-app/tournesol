import React from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Grid, Typography } from '@mui/material';
import makeStyles from '@mui/styles/makeStyles';

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
  const { t } = useTranslation();
  const classes = useStyles();
  return (
    <>
      <ContentHeader
        title={`${t('settings.title')} > ${t('settings.account')}`}
      />
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
            <SettingsSection title={t('settings.changeEmailAddress')} xs={12}>
              <EmailAddressForm />
            </SettingsSection>
            <SettingsSection
              title={t('settings.changePassword')}
              xs={12}
              md={6}
            >
              <PasswordForm />
            </SettingsSection>
            <Box marginTop={8} />
            <SettingsSection title={t('settings.exportAllData')} xs={12}>
              <ExportAllDataForm />
            </SettingsSection>
            <SettingsSection
              title={
                <Typography variant="h4" className={classes.titleDanger}>
                  {t('settings.deleteAccount')}
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
