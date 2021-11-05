import React, { useEffect, useState } from 'react';
import { useSnackbar } from 'notistack';

import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';

import {
  contactAdministrator,
  showErrorAlert,
  showSuccessAlert,
} from '../../../utils/notifications';
import { AccountsService } from '../../../services/openapi';

const ProfileForm = () => {
  const [username, setUsername] = useState('');

  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    async function retrieveProfile() {
      const response = await AccountsService.accountsProfileRetrieve();
      setUsername(response['username']);
    }

    retrieveProfile();
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    const response = await AccountsService.accountsProfilePartialUpdate({
      username,
      // handle errors and unknown errors
    }).catch((reason: { body: { [k: string]: string[] } }) => {
      if (reason && 'body' in reason) {
        const newErrorMessages = Object.values(reason['body']).flat();
        newErrorMessages.map((msg) => showErrorAlert(enqueueSnackbar, msg));
      } else {
        contactAdministrator(
          enqueueSnackbar,
          'error',
          'Sorry, an error has occurred, cannot update the profile.'
        );
      }
    });

    // handle success and malformed success
    if (response) {
      if ('detail' in response) {
        showSuccessAlert(enqueueSnackbar, response['detail']);
      } else {
        showSuccessAlert(enqueueSnackbar, 'Profile changed successfully');
      }

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
            label="User name"
            name="username"
            color="secondary"
            size="small"
            type="text"
            variant="outlined"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            inputProps={{ 'data-testid': 'username' }}
          />
          <Typography variant="caption">
            Your user name will appear in the Tournesol&apos;s public database
            if you choose to make any of your data on Tournesol public. You can
            change it at any time.
          </Typography>
        </Grid>
        <Grid item>
          <Button type="submit" color="secondary" fullWidth variant="contained">
            Update profile
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};

export default ProfileForm;
