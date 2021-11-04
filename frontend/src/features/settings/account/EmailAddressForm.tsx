import React, { useState, useEffect } from 'react';

import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import { CircularProgress, Box, Typography } from '@material-ui/core';

import { useSnackbar } from 'notistack';

import { showErrorAlert } from '../../../utils/notifications';
import { FormTextField } from 'src/components';

import { AccountsService, ApiError } from 'src/services/openapi';

export const EmailAddressForm = () => {
  const { enqueueSnackbar } = useSnackbar();
  const [currentEmail, setCurrentEmail] = useState<string | null>(null);
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
        setCurrentEmail(profile.email);
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
    if (isLoading) {
      return <CircularProgress />;
    }
    return (
      <>
        {currentEmail && (
          <Box marginBottom={2}>
            <Typography>
              Your current email address is{' '}
              <strong>
                <code>{currentEmail}</code>
              </strong>
            </Typography>
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
      </>
    );
  };

  return <Box minHeight="150px">{getContent()}</Box>;
};
