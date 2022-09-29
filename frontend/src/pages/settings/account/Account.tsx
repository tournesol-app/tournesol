import React from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Grid, Typography, useTheme } from '@mui/material';

import { ContentBox, ContentHeader, SettingsSection } from 'src/components';
import PasswordForm from 'src/features/settings/account/PasswordForm';
import DeleteAccountForm from 'src/features/settings/account/DeleteAccountForm';
import EmailAddressForm from 'src/features/settings/account/EmailAddressForm';
import ExportAllDataForm from 'src/features/settings/account/ExportAllDataForm';
import SettingsMenu from 'src/features/settings/SettingsMenu';

import { mainSectionBp, settingsMenuBp } from '../layout';

export const AccountPage = () => {
  const { t } = useTranslation();
  const theme = useTheme();

  // subSectionBreakP can be changed independently of mainSectionBp
  const subSectionBreakP = mainSectionBp;
  return (
    <>
      <ContentHeader
        title={`${t('settings.title')} > ${t('settings.account')}`}
      />
      <ContentBox maxWidth="xl">
        <Grid container spacing={4}>
          <Grid item {...settingsMenuBp}>
            <SettingsMenu />
          </Grid>
          <Grid
            container
            item
            direction="column"
            alignItems="stretch"
            spacing={3}
            {...mainSectionBp}
          >
            <SettingsSection
              title={t('settings.changeEmailAddress')}
              {...subSectionBreakP}
            >
              <EmailAddressForm />
            </SettingsSection>
            <SettingsSection
              title={t('settings.changePassword')}
              {...subSectionBreakP}
            >
              <PasswordForm />
            </SettingsSection>
            <Box marginTop={8} />
            <SettingsSection
              title={t('settings.exportAllData')}
              {...subSectionBreakP}
            >
              <ExportAllDataForm />
            </SettingsSection>
            <SettingsSection
              title={
                <Typography
                  variant="h4"
                  sx={{ color: theme.palette.error.main }}
                >
                  {t('settings.deleteAccount')}
                </Typography>
              }
              {...subSectionBreakP}
            >
              <DeleteAccountForm />
            </SettingsSection>
          </Grid>
        </Grid>
      </ContentBox>
    </>
  );
};

export default AccountPage;
