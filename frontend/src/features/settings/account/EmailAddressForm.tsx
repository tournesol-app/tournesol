import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';

import {
  CircularProgress,
  Box,
  Typography,
  Theme,
  Grid,
  Button,
} from '@mui/material';
import { useTheme } from '@mui/styles';

import { FormTextField } from 'src/components';
import { AccountsService, ApiError, UserProfile } from 'src/services/openapi';
import { Lens as LensIcon, HelpOutline as HelpIcon } from '@mui/icons-material';
import { useNotifications } from 'src/hooks';

const TrustStatus = ({ isTrusted }: { isTrusted: boolean }) => {
  const { t } = useTranslation();
  const theme = useTheme<Theme>();
  const statusColor = isTrusted
    ? theme.palette.success.dark
    : theme.palette.warning.dark;

  return (
    <Box
      display="flex"
      flexDirection="row"
      flexWrap="wrap"
      alignItems="center"
      justifyContent="space-between"
    >
      <Typography
        component="div"
        sx={{ display: 'flex', alignItems: 'center' }}
      >
        {t('settings.emailStatus')}
        {': '}
        <LensIcon sx={{ fontSize: 16, color: statusColor, margin: '0 4px' }} />
        <Box color={statusColor} fontWeight="bold">
          {isTrusted
            ? t('settings.emailTrusted')
            : t('settings.emailNonTrusted')}
        </Box>
      </Typography>

      <Box display="inline-flex">
        <Button
          component={RouterLink}
          to="/about/trusted_domains"
          size="small"
          sx={{ fontSize: 13, color: '#777' }}
          startIcon={<HelpIcon />}
        >
          {t('settings.learnMoreAboutTrustedDomains')}
        </Button>
      </Box>
    </Box>
  );
};

const EmailAddressForm = () => {
  const { t } = useTranslation();
  const { showErrorAlert } = useNotifications();
  const [profileData, setProfileData] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSuccess, setIsSuccess] = useState(false);
  const [apiError, setApiError] = useState<ApiError | null>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);

    try {
      await AccountsService.accountsRegisterEmailCreate({
        requestBody: {
          email: new FormData(event.currentTarget).get('email') as string,
        },
      });
      setIsSuccess(true);
    } catch (err) {
      setApiError(err as ApiError);
      if (err?.status !== 400) {
        showErrorAlert(err?.message || 'Server error');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const profile = await AccountsService.accountsProfileRetrieve();
        setProfileData(profile);
        setIsLoading(false);
      } catch (err) {
        showErrorAlert(err?.message || 'Server error');
      }
    };
    loadProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const formError = apiError?.status === 400 ? apiError.body : null;

  const getContent = () => {
    if (isSuccess) {
      return (
        <Typography>
          ✅ {t('settings.verificationEmailSentNewEmail')}
        </Typography>
      );
    }
    return (
      <Grid container spacing={2} direction="column" alignItems="stretch">
        {isLoading && <CircularProgress />}
        {/* "display" is used here to keep the form state during loading. */}
        <Grid item sx={{ display: isLoading ? 'none' : undefined }}>
          {profileData && (
            <Box
              marginBottom={2}
              display="flex"
              flexDirection="column"
              gap="8px"
            >
              <Typography>
                {t('settings.currentEmailAddressIs')}{' '}
                <strong style={{ whiteSpace: 'nowrap' }}>
                  <code>{profileData.email}</code>
                </strong>
              </Typography>
              <TrustStatus isTrusted={profileData.is_trusted} />
            </Box>
          )}
          <form onSubmit={handleSubmit}>
            <FormTextField
              required
              fullWidth
              label={t('settings.newEmailAddress')}
              name="email"
              type="email"
              formError={formError}
              style={{ marginBottom: 16 }}
            />
            <Button
              type="submit"
              color="secondary"
              fullWidth
              variant="contained"
            >
              {t('settings.sendVerificationEmail')}
            </Button>
          </form>
        </Grid>
      </Grid>
    );
  };

  return <Box minHeight="180px">{getContent()}</Box>;
};

export default EmailAddressForm;
