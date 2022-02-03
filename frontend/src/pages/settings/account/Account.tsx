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
  // sectionBreakP can be changed independently of breakP
  const breakP = { xs: 12, sm: 12, md: 9, lg: 9, xl: 10 };
  const sectionBreakP = breakP;
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
              {...sectionBreakP}
            >
              <EmailAddressForm />
            </SettingsSection>
            <SettingsSection
              title={t('settings.changePassword')}
              {...sectionBreakP}
            >
              <PasswordForm />
            </SettingsSection>
            <Box marginTop={8} />
            <SettingsSection
              title={t('settings.exportAllData')}
              {...sectionBreakP}
            >
              <ExportAllDataForm />
            </SettingsSection>
            <SettingsSection
              title={
                <Typography variant="h4" className={classes.titleDanger}>
                  {t('settings.deleteAccount')}
                </Typography>
              }
              {...sectionBreakP}
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
