import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from 'notistack';

import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';

import { useLoginState } from 'src/hooks';
import { displayErrors } from 'src/utils/api/response';
import {
  contactAdministrator,
  showSuccessAlert,
} from 'src/utils/notifications';
import { AccountsService, ApiError } from 'src/services/openapi';

const ProfileForm = () => {
  const { t } = useTranslation();
  const { updateUsername } = useLoginState();
  const { enqueueSnackbar } = useSnackbar();

  const [username, setUsername] = useState('');
  const [disabled, setDisabled] = useState(false);

  useEffect(() => {
    async function retrieveProfile() {
      const response = await AccountsService.accountsProfileRetrieve().catch(
        () => {
          contactAdministrator(
            enqueueSnackbar,
            'error',
            t('settings.errorOccurredWhenRetrievingProfile')
          );
        }
      );
      if (response) {
        setUsername(response['username']);
        updateUsername(response['username']);
      }
    }

    retrieveProfile();
  }, [t, updateUsername, enqueueSnackbar]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setDisabled(true);

    const response = await AccountsService.accountsProfilePartialUpdate({
      requestBody: {
        username,
      },
    }).catch((reason: ApiError) => {
      displayErrors(
        enqueueSnackbar,
        reason,
        t('settings.errorOccurredWhenUpdatingProfile')
      );
    });

    // handle success and malformed success
    if (response) {
      if ('detail' in response) {
        showSuccessAlert(enqueueSnackbar, response['detail']);
      } else {
        showSuccessAlert(
          enqueueSnackbar,
          t('settings.profileChangedSuccessfully')
        );
      }

      updateUsername(username);
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
            label={t('username')}
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
            {t('settings.captionUsernameWillAppearInPublicDatabase')}
          </Typography>
        </Grid>
        <Grid item>
          <Button
            fullWidth
            type="submit"
            color="secondary"
            variant="contained"
            disabled={disabled}
          >
            {t('settings.updateProfile')}
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};

export default ProfileForm;
