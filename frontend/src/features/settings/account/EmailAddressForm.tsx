import React, { useState, useEffect } from 'react';

import {
  CircularProgress,
  Box,
  Typography,
  Theme,
  Grid,
  Button,
} from '@material-ui/core';
import { Link as RouterLink } from 'react-router-dom';

import { useSnackbar } from 'notistack';

import { showErrorAlert } from '../../../utils/notifications';
import { FormTextField } from 'src/components';

import { AccountsService, ApiError, UserProfile } from 'src/services/openapi';
import { Lens as LensIcon, HelpOutline as HelpIcon } from '@material-ui/icons';
import { useTheme } from '@material-ui/styles';

const TrustStatus = ({ isTrusted }: { isTrusted: boolean }) => {
  const theme = useTheme<Theme>();

  return (
    <Box display="flex" flexDirection="row" flexWrap="wrap" alignItems="center">
      <Typography>
        <Box display="flex" gridGap="4px" alignItems="center">
          Email status:
          <Box
            display="inline-flex"
            flexDirection="row"
            alignItems="center"
            gridGap="4px"
            color={
              isTrusted
                ? theme.palette.success.main
                : theme.palette.warning.main
            }
            fontWeight="bold"
          >
            <LensIcon style={{ fontSize: 16 }} />
            <Grid item>{isTrusted ? 'Trusted' : 'Non-trusted'}</Grid>
          </Box>
        </Box>
      </Typography>

      <Box display="inline-flex" marginLeft="auto">
        <Button
          component={RouterLink}
          to="/about/trusted_domains"
          size="small"
          style={{ fontSize: 13, color: '#777' }}
          startIcon={<HelpIcon />}
        >
          Learn more about trusted domains
        </Button>
      </Box>
    </Box>
  );
};

export const EmailAddressForm = () => {
  const { enqueueSnackbar } = useSnackbar();
  const [profileData, setProfileData] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSuccess, setIsSuccess] = useState(false);
  const [apiError, setApiError] = useState<ApiError | null>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);

    try {
      await AccountsService.accountsRegisterEmailCreate({
        email: new FormData(event.currentTarget).get('email') as string,
      });
      setIsSuccess(true);
    } catch (err) {
      setApiError(err as ApiError);
      if (err?.status !== 400) {
        showErrorAlert(enqueueSnackbar, err?.message || 'Server error');
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
        showErrorAlert(enqueueSnackbar, err?.message || 'Server error');
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
          ✅ A verification email has been sent to confirm your new email
          address.
        </Typography>
      );
    }
    return (
      <>
        {isLoading && <CircularProgress />}
        {/* "display" is used here to keep the form state during loading. */}
        <div style={{ display: isLoading ? 'none' : undefined }}>
          {profileData && (
            <Box marginBottom={2}>
              <Typography>
                Your current email address is{' '}
                <strong>
                  <code>{profileData.email}</code>
                </strong>
              </Typography>
              <TrustStatus isTrusted={profileData.is_trusted} />
            </Box>
          )}
          <form onSubmit={handleSubmit}>
            <Grid container spacing={2} direction="column" alignItems="stretch">
              <Grid item md={6}>
                <FormTextField
                  required
                  fullWidth
                  label="New email address"
                  name="email"
                  type="email"
                  formError={formError}
                />
              </Grid>
              <Grid item md={6}>
                <Button
                  type="submit"
                  color="secondary"
                  fullWidth
                  variant="contained"
                >
                  Send verification email
                </Button>
              </Grid>
            </Grid>
          </form>
        </div>
      </>
    );
  };

  return <Box minHeight="180px">{getContent()}</Box>;
};
