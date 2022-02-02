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
  const breakP = { xs: 12, sm: 12, md: 9, lg: 9, xl: 10 };
  return (
    <>
      <ContentHeader
        title={`${t('settings.title')} > ${t('settings.account')}`}
      />
      <Box m={4}>
        <Grid container spacing={4}>
          <Grid item xs={12} sm={12} md={3} lg={3} xl={2}>
            <SettingsMenu />
          </Grid>
          <Grid
            container
            item
            direction="column"
            alignItems="stretch"
            spacing={3}
            {...breakP}
          >
            <SettingsSection
              title={t('settings.changeEmailAddress')}
              {...breakP}
            >
              <EmailAddressForm />
            </SettingsSection>
            <SettingsSection title={t('settings.changePassword')} {...breakP}>
              <PasswordForm />
            </SettingsSection>
            <Box marginTop={8} />
            <SettingsSection title={t('settings.exportAllData')} {...breakP}>
              <ExportAllDataForm />
            </SettingsSection>
            <SettingsSection
              title={
                <Typography variant="h4" className={classes.titleDanger}>
                  {t('settings.deleteAccount')}
                </Typography>
              }
              {...breakP}
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
