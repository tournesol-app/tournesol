import React, { useState } from 'react';

import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';

import { useSnackbar } from 'notistack';

import {
  contactAdministrator,
  showErrorAlert,
  showSuccessAlert,
} from 'src/utils/notifications';
import { AccountsService } from 'src/services/openapi';

const PasswordForm = () => {
  const { enqueueSnackbar } = useSnackbar();

  const [oldPassword, setOldPassword] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');

  const passwordConfirmMatches =
    password !== '' && password === passwordConfirm;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    const response: void | Record<string, string> =
      await AccountsService.accountsChangePasswordCreate(
        {
          old_password: oldPassword,
          password,
          password_confirm: passwordConfirm,
        }
        // handle errors and unknown errors
      ).catch((reason: { body: { [k: string]: string[] } }) => {
        if (reason && 'body' in reason) {
          const newErrorMessages = Object.values(reason['body']).flat();
          newErrorMessages.map((msg) => showErrorAlert(enqueueSnackbar, msg));
        } else {
          contactAdministrator(
            enqueueSnackbar,
            'error',
            'Sorry, an error has occurred, cannot update password.'
          );
        }
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
          <Button type="submit" color="secondary" fullWidth variant="contained">
            Update password
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};

export default PasswordForm;
