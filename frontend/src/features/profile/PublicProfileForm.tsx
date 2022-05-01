import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useParams } from 'react-router-dom';
import {
  AccountsService,
  ApiError,
  UserProfile,
  UsersService,
} from 'src/services/openapi';
import { Lens as LensIcon, HelpOutline as HelpIcon } from '@mui/icons-material';
import { useTheme } from '@mui/styles';
import { useNotifications } from 'src/hooks';
import {
  CircularProgress,
  Box,
  Typography,
  Theme,
  Grid,
  Button,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

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

const PublicProfileForm = () => {
  const { username_url } = useParams<{ username_url: string }>();
  const { t } = useTranslation();
  const { contactAdministrator } = useNotifications();
  const { showErrorAlert } = useNotifications();
  const [profileData, setProfileData] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSuccess, setIsSuccess] = useState(false);
  const [apiError, setApiError] = useState<ApiError | null>(null);

  const [username, setUsername] = useState(username_url);
  const [diplomas, setDiplomas] = useState<null | undefined | string>();
  const [competencies, setCompetencies] = useState<null | undefined | string>();
  const [lastname, setLastName] = useState<null | undefined | string>();
  const [firstname, setFirstName] = useState<null | undefined | string>();

  useEffect(() => {
    //this do for logged user
    // async function retrieveProfile() {
    //   const response = await AccountsService.accountsProfileRetrieve().catch(
    //     () => {
    //       contactAdministrator(
    //         'error',
    //         t('settings.errorOccurredWhenRetrievingProfile')
    //       );
    //     }
    //   );
    //   if (response) {
    //     setUsername(response['username']);
    //     setDiplomas(response['diplomas']);
    //     setCompetencies(response['competencies']);
    //     setLastName(response['last_name']);
    //   }
    // }

    // retrieveProfile();

    //try for user by username
    // async function retrieveProfile() {

    //   const response = await UsersService.userRetrieve1({username}).catch()(
    //     () => {
    //       contactAdministrator(
    //         'error',
    //         t('settings.errorOccurredWhenRetrievingProfile')
    //       );
    //     }
    //   );
    //   if (response) {
    //     setUsername(response['username']);
    //     setDiplomas(response['diplomas']);
    //     setCompetencies(response['competencies']);
    //     setLastName(response['last_name']);
    //   }
    // }

    // retrieveProfile();

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
  }, [t, contactAdministrator]);

  return (
    <Grid container spacing={2} direction="column" alignItems="stretch">
      <Grid item>
        <Typography>
          {t('Username: ')}{' '}
          <strong style={{ whiteSpace: 'nowrap' }}>
            <code>{username}</code>
          </strong>
        </Typography>

        <Typography>
          {t(lastname != null || firstname != null ? 'Name: ' : '')}{' '}
          <strong style={{ whiteSpace: 'nowrap' }}>
            <code>{lastname}</code>
            <code>{firstname}</code>
          </strong>
        </Typography>
        <Typography>
          {t(diplomas != null ? 'Declared diplomas: ' : '')}{' '}
          <strong style={{ whiteSpace: 'nowrap' }}>
            <code>{diplomas}</code>
          </strong>
        </Typography>
        <Typography>
          {t(competencies != null ? 'Declared competencies: ' : '')}{' '}
          <strong style={{ whiteSpace: 'nowrap' }}>
            <code>{competencies}</code>
          </strong>
        </Typography>
      </Grid>
      {isLoading && <CircularProgress />}
      {/* "display" is used here to keep the form state during loading. */}
      <Grid item sx={{ display: isLoading ? 'none' : undefined }}>
        {profileData && (
          <Box marginBottom={2} display="flex" flexDirection="column" gap="8px">
            <Typography>
              {t('Email Address: ')}{' '}
              <strong style={{ whiteSpace: 'nowrap' }}>
                <code>{profileData.email}</code>
              </strong>
            </Typography>
            <TrustStatus isTrusted={profileData.is_trusted} />
          </Box>
        )}
      </Grid>
    </Grid>
  );
};

export default PublicProfileForm;
