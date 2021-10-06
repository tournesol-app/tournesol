import React, { useState } from 'react';

import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';

import { useSnackbar } from 'notistack';

import { useAppSelector } from '../../../app/hooks';
import { changePassword } from '../../account/accountAPI';
import { selectLogin } from '../../login/loginSlice';
import { contactAdministrator } from '../../../utils/notifications';

const PasswordForm = () => {
  // TODO (1) use await instead of .then followed by .catch
  // TODO (2) make the form unfocused after a success
  const token = useAppSelector(selectLogin);
  const access_token = token.access_token ? token.access_token : '';

  const [oldPassword, setOldPassword] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');

  const { enqueueSnackbar } = useSnackbar();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    changePassword(access_token, oldPassword, password, passwordConfirm)
      .then((value: Record<string, string>) => {
        enqueueSnackbar(value['detail'], { variant: 'success' });
        setOldPassword('');
        setPassword('');
        setPasswordConfirm('');
      })
      .catch((reason: { body: { [k: string]: string[] } }) => {
        if (reason && 'body' in reason) {
          const newErrorMessages = Object.values(reason['body']).flat();
          newErrorMessages.map((msg) =>
            enqueueSnackbar(msg, { variant: 'error' })
          );
        } else {
          contactAdministrator(
            enqueueSnackbar,
            'Sorry, an error has occurred, cannot update password.'
          );
        }
      });
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
            onChange={(event) => setPasswordConfirm(event.target.value)}
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
