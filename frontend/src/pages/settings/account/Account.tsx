import React from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Grid2, Typography, useTheme } from '@mui/material';

import { ContentBox, ContentHeader, SettingsSection } from 'src/components';
import PasswordForm from 'src/features/settings/account/PasswordForm';
import DeleteAccountForm from 'src/features/settings/account/DeleteAccountForm';
import EmailAddressForm from 'src/features/settings/account/EmailAddressForm';
import ExportAllDataForm from 'src/features/settings/account/ExportAllDataForm';
import SettingsMenu from 'src/features/settings/SettingsMenu';
import {
  mainSectionBreakpoints,
  mainSectionGridSpacing,
  settingsMenuBreakpoints,
  subSectionBreakpoints,
} from 'src/pages/settings/layout';

export const AccountPage = () => {
  const { t } = useTranslation();
  const theme = useTheme();

  return (
    <>
      <ContentHeader
        title={`${t('settings.title')} > ${t('settings.account')}`}
      />
      <ContentBox maxWidth="xl">
        <Grid2 container spacing={4}>
          <Grid2 size={settingsMenuBreakpoints}>
            <SettingsMenu />
          </Grid2>
          <Grid2
            container
            direction="column"
            spacing={mainSectionGridSpacing}
            size={mainSectionBreakpoints}
            sx={{
              alignItems: 'stretch',
            }}
          >
            <SettingsSection
              title={t('settings.changeEmailAddress')}
              {...subSectionBreakpoints}
            >
              <EmailAddressForm />
            </SettingsSection>
            <SettingsSection
              title={t('settings.changePassword')}
              {...subSectionBreakpoints}
            >
              <PasswordForm />
            </SettingsSection>
            <SettingsSection
              title={t('settings.exportAllData')}
              {...subSectionBreakpoints}
            >
              <ExportAllDataForm />
            </SettingsSection>
            <Box
              sx={{
                mt: 8,
              }}
            ></Box>
            <SettingsSection
              title={
                <Typography
                  variant="h4"
                  sx={{ color: theme.palette.error.main }}
                >
                  {t('settings.deleteAccount')}
                </Typography>
              }
              {...subSectionBreakpoints}
            >
              <DeleteAccountForm />
            </SettingsSection>
          </Grid2>
        </Grid2>
      </ContentBox>
    </>
  );
};

export default AccountPage;
