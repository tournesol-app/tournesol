import React, { useState } from 'react';

import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';

import { useSnackbar } from 'notistack';

import { AccountsService, ApiError } from 'src/services/openapi';
import { showSuccessAlert } from 'src/utils/notifications';
import { displayErrors } from 'src/utils/api/response';

const PasswordForm = () => {
  const { enqueueSnackbar } = useSnackbar();

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
        displayErrors(
          enqueueSnackbar,
          reason,
          'Sorry, an error has occurred, cannot update password.'
        );
      });

    // handle success and malformed success
    if (response) {
      if ('detail' in response) {
        showSuccessAlert(enqueueSnackbar, response['detail']);
      } else {
        showSuccessAlert(enqueueSnackbar, 'Password changed successfully');
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
            label="Old password"
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
            label="New password"
            name="password"
            color="secondary"
            size="small"
            type="password"
            variant="outlined"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            inputProps={{ 'data-testid': 'password' }}
          />
        </Grid>
        <Grid item>
          <TextField
            required
            fullWidth
            label="Confirm new password"
            name="password_confirm"
            color="secondary"
            size="small"
            type="password"
            variant="outlined"
            value={passwordConfirm}
            helperText={
              passwordConfirm !== '' && !passwordConfirmMatches
                ? 'Passwords do not match'
                : undefined
            }
            error={passwordConfirm !== '' && !passwordConfirmMatches}
            onChange={(event) => setPasswordConfirm(event.target.value)}
            inputProps={{ 'data-testid': 'password_confirm' }}
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
            Update password
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};

export default PasswordForm;
