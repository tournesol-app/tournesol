import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';

import { AccountsService, ApiError } from 'src/services/openapi';
import { useNotifications } from 'src/hooks';

const PasswordForm = () => {
  const { t } = useTranslation();
  const { displayErrorsFrom, showSuccessAlert } = useNotifications();
  const [oldPassword, setOldPassword] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [disabled, setDisabled] = useState(false);

  const passwordConfirmMatches =
    password !== '' && password === passwordConfirm;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setDisabled(true);

    const response: void | Record<string, string> =
      await AccountsService.accountsChangePasswordCreate({
        requestBody: {
          old_password: oldPassword,
          password,
          password_confirm: passwordConfirm,
        },
      }).catch((reason: ApiError) => {
        displayErrorsFrom(
          reason,
          t('settings.errorOccurredDuringPasswordUpdate')
        );
      });

    // handle success and malformed success
    if (response) {
      if ('detail' in response) {
        showSuccessAlert(response['detail']);
      } else {
        showSuccessAlert(t('settings.passwordChangedSuccessfully'));
      }

      setOldPassword('');
      setPassword('');
      setPasswordConfirm('');
      (document.activeElement as HTMLElement).blur();
    }
    setDisabled(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <Grid container spacing={2} direction="column" alignItems="stretch">
        <Grid item>
          <TextField
            required
            fullWidth
            label={t('settings.oldPassword')}
            name="old_password"
            color="secondary"
            size="small"
            type="password"
            variant="outlined"
            value={oldPassword}
            onChange={(event) => setOldPassword(event.target.value)}
            inputProps={{ 'data-testid': 'old_password' }}
          />
        </Grid>
        <Grid item>
          <TextField
            required
            fullWidth
            label={t('settings.newPassword')}
            name="password"
            color="secondary"
            size="small"
            type="password"
            variant="outlined"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            inputProps={{ 'data-testid': 'password' }}
            autoComplete="new-password"
          />
        </Grid>
        <Grid item>
          <TextField
            required
            fullWidth
            label={t('settings.confirmNewPassword')}
            name="password_confirm"
            color="secondary"
            size="small"
            type="password"
            variant="outlined"
            value={passwordConfirm}
            helperText={
              passwordConfirm !== '' && !passwordConfirmMatches
                ? t('settings.passwordsDoNotMatch')
                : undefined
            }
            error={passwordConfirm !== '' && !passwordConfirmMatches}
            onChange={(event) => setPasswordConfirm(event.target.value)}
            inputProps={{ 'data-testid': 'password_confirm' }}
            autoComplete="new-password"
          />
        </Grid>
        <Grid item>
          <Button
            fullWidth
            type="submit"
            color="secondary"
            variant="contained"
            disabled={disabled}
          >
            {t('settings.updatePassword')}
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};

export default PasswordForm;
