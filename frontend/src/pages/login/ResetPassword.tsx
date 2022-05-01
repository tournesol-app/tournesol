import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router';
import { Grid, Button } from '@mui/material';
import {
  AccountsService,
  ResetPassword as ResetPasswordData,
} from 'src/services/openapi';
import { ContentHeader, ContentBox, FormTextField } from 'src/components';
import { useLoginState, useNotifications, useSearchParams } from 'src/hooks';
import useLastPoll from 'src/hooks/useLastPoll';

function ResetPassword() {
  useLastPoll();
  const { t } = useTranslation();
  const history = useHistory();
  const searchParams = useSearchParams();
  const { showErrorAlert, showSuccessAlert } = useNotifications();
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
      await AccountsService.accountsResetPasswordCreate({
        requestBody: resetPasswordData,
      });
      logout();
      showSuccessAlert(t('reset.passwordModifiedSuccessfully'));
      history.replace('/login');
    } catch (err) {
      if (err?.status !== 400) {
        showErrorAlert(err?.message || 'Server error');
      } else if (err.body?.detail) {
        showErrorAlert(err.body.detail);
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
      <ContentHeader title={t('reset.resetYourPassword')} />
      <ContentBox maxWidth="xs">
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3} direction="column" alignItems="stretch">
            <Grid item xs={12}>
              <FormTextField
                type="password"
                name="password"
                label={t('reset.newPassword')}
                onChange={(e) => setPassword(e.target.value)}
                formError={formError}
              />
            </Grid>
            <Grid item xs={12}>
              <FormTextField
                type="password"
                name="confirm_password"
                label={t('reset.confirmNewPassword')}
                error={confirmPassword !== '' && !confirmPasswordIsValid}
                helperText={
                  confirmPassword !== '' && !confirmPasswordIsValid
                    ? t('reset.passwordsDoNotMatch')
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
                {t('reset.resetPasswordButton')}
              </Button>
            </Grid>
          </Grid>
        </form>
      </ContentBox>
    </>
  );
}

export default ResetPassword;
