import React, { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import { Trans, useTranslation } from 'react-i18next';

import { Button, Grid, TextField, Typography } from '@mui/material';

import { replaceSettings } from 'src/features/settings/userSettingsSlice';
import { useNotifications } from 'src/hooks';
import {
  ApiError,
  TournesolUserSettings,
  UsersService,
} from 'src/services/openapi';

const RATE_LATER_AUTO_REMOVE_DEFAULT = 4;

const UserSettingsForm = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();

  const { contactAdministrator, displayErrorsFrom, showSuccessAlert } =
    useNotifications();

  const [disabled, setDisabled] = useState(false);
  const [rateLaterAutoRemove, setRateLaterAutoRemove] = useState(0);

  /**
   * Retrieve the up-to-date user's preferences from the API and refresh the
   * Redux store.
   */
  useEffect(() => {
    async function retrieveProfile() {
      const response = await UsersService.usersMeSettingsRetrieve().catch(
        () => {
          contactAdministrator(
            'error',
            t('pollUserSettingsForm.errorOccurredWhileRetrievingPreferences')
          );
        }
      );

      if (response) {
        setRateLaterAutoRemove(
          response?.videos?.rate_later__auto_remove ??
            RATE_LATER_AUTO_REMOVE_DEFAULT
        );
        dispatch(replaceSettings(response));
      }
    }

    retrieveProfile();
  }, [t, dispatch, contactAdministrator]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setDisabled(true);

    const response: void | TournesolUserSettings =
      await UsersService.usersMeSettingsPartialUpdate({
        requestBody: {
          videos: {
            rate_later__auto_remove: rateLaterAutoRemove,
          },
        },
      }).catch((reason: ApiError) => {
        // TODO: display the errors next to their related fields
        displayErrorsFrom(
          reason,
          t('pollUserSettingsForm.errorOccurredDuringPreferencesUpdate')
        );
      });

    if (response) {
      showSuccessAlert(
        t('pollUserSettingsForm.preferencesUpdatedSuccessfully')
      );
      dispatch(replaceSettings(response));
      (document.activeElement as HTMLElement).blur();
    }
    setDisabled(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <Grid container spacing={2} direction="column" alignItems="stretch">
        <Grid item>
          <Typography variant="h6">
            {t('pollUserSettingsForm.rateLater')}
          </Typography>
        </Grid>
        <Grid item>
          <TextField
            required
            fullWidth
            label={t('pollUserSettingsForm.autoRemove')}
            helperText={
              <Trans
                t={t}
                i18nKey="pollUserSettingsForm.autoRemoveHelpText"
                count={rateLaterAutoRemove}
              >
                Entities will be removed from your rate-later list after
                {{ rateLaterAutoRemove }} comparisons.
              </Trans>
            }
            name="rate_later__auto_remove"
            color="secondary"
            size="small"
            type="number"
            variant="outlined"
            value={rateLaterAutoRemove}
            onChange={(event) =>
              setRateLaterAutoRemove(Number(event.target.value))
            }
            inputProps={{ 'data-testid': 'rate_later__auto_remove' }}
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
            {t('pollUserSettingsForm.updatePreferences')}
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};

export default UserSettingsForm;
