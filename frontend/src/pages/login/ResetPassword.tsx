import React, { useState } from 'react';
import { useHistory } from 'react-router';
import { useSnackbar } from 'notistack';
import { Grid, Button } from '@material-ui/core';
import {
  AccountsService,
  ResetPassword as ResetPasswordData,
} from 'src/services/openapi';
import { ContentHeader, ContentBox, FormTextField } from 'src/components';
import { useLoginState, useSearchParams } from 'src/hooks';
import { showErrorAlert } from 'src/utils/notifications';

function ResetPassword() {
  const history = useHistory();
  const searchParams = useSearchParams();
  const { enqueueSnackbar } = useSnackbar();
  const [formError, setFormError] = useState<Record<string, string[]>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const { logout } = useLoginState();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    const { user_id, timestamp, signature } = searchParams;
    const resetPasswordData: ResetPasswordData = {
      user_id,
      password,
      timestamp: Number(timestamp),
      signature,
    };

    try {
      await AccountsService.accountsResetPasswordCreate(resetPasswordData);
      logout();
      enqueueSnackbar(
        'Your password has been modified successfully. You can now log in to Tournesol.',
        { variant: 'success' }
      );
      history.replace('/login');
    } catch (err) {
      if (err?.status !== 400) {
        showErrorAlert(enqueueSnackbar, err?.message || 'Server error');
      } else if (err.body?.detail) {
        showErrorAlert(enqueueSnackbar, err.body.detail);
      } else {
        setFormError(err.body || {});
      }
    } finally {
      setIsLoading(false);
    }
  };

  const confirmPasswordIsValid =
    confirmPassword !== '' && password === confirmPassword;

  return (
    <>
      <ContentHeader title="Reset your password" />
      <ContentBox maxWidth="xs">
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3} direction="column" alignItems="stretch">
            <Grid item xs={12}>
              <FormTextField
                type="password"
                name="password"
                label="New password"
                onChange={(e) => setPassword(e.target.value)}
                formError={formError}
              />
            </Grid>
            <Grid item xs={12}>
              <FormTextField
                type="password"
                name="confirm_password"
                label="Confirm your new password"
                error={confirmPassword !== '' && !confirmPasswordIsValid}
                helperText={
                  confirmPassword !== '' && !confirmPasswordIsValid
                    ? 'Passwords do not match'
                    : undefined
                }
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                type="submit"
                color="secondary"
                fullWidth
                variant="contained"
                disabled={isLoading || !confirmPasswordIsValid}
              >
                Reset password
              </Button>
            </Grid>
          </Grid>
        </form>
      </ContentBox>
    </>
  );
}

export default ResetPassword;
