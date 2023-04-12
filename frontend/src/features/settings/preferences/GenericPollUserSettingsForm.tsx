import React, { useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';

import { Button, Grid, TextField, Typography } from '@mui/material';

import { YOUTUBE_POLL_NAME } from 'src/utils/constants';
import {
  replaceSettings,
  selectSettings,
} from 'src/features/settings/userSettingsSlice';
import { useNotifications } from 'src/hooks';
import {
  ApiError,
  TournesolUserSettings,
  UsersService,
} from 'src/services/openapi';

interface Props {
  // Allowed polls. Using literal allows us to use the form settings[pollName]
  // with TypeScript.
  pollName: typeof YOUTUBE_POLL_NAME;
}

/**
 * Display a generic user settings form that can be used by any poll.
 */
const GenericPollUserSettingsForm = ({ pollName }: Props) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { showSuccessAlert, showErrorAlert } = useNotifications();

  const [disabled, setDisabled] = useState(false);
  const [apiErrors, setApiErrors] = useState<ApiError | null>(null);

  // List of user's settings.
  const userSettings = useSelector(selectSettings).settings;
  const [rateLaterAutoRemove, setRateLaterAutoRemove] = useState(
    userSettings ? userSettings[pollName]?.rate_later__auto_remove ?? 4 : 4
  );

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setDisabled(true);

    const response: void | TournesolUserSettings =
      await UsersService.usersMeSettingsPartialUpdate({
        requestBody: {
          [pollName]: {
            rate_later__auto_remove: rateLaterAutoRemove,
          },
        },
      }).catch((reason: ApiError) => {
        showErrorAlert(
          t('pollUserSettingsForm.errorOccurredDuringPreferencesUpdate')
        );

        setApiErrors(reason);
      });

    if (response) {
      showSuccessAlert(
        t('pollUserSettingsForm.preferencesUpdatedSuccessfully')
      );
      setApiErrors(null);
      dispatch(replaceSettings(response));
      (document.activeElement as HTMLElement).blur();
    }
    setDisabled(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <Grid container spacing={4} direction="column" alignItems="stretch">
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
              <>
                <Trans
                  t={t}
                  i18nKey="pollUserSettingsForm.autoRemoveHelpText"
                  count={rateLaterAutoRemove}
                >
                  Entities will be removed from your rate-later list after
                  {{ rateLaterAutoRemove }} comparisons.
                </Trans>
                {apiErrors &&
                  apiErrors.body[pollName]?.rate_later__auto_remove &&
                  apiErrors.body[pollName].rate_later__auto_remove.map(
                    (error: string, idx: number) => (
                      <Typography
                        key={`rate_later__auto_remove_error_${idx}`}
                        color="red"
                        display="block"
                        variant="caption"
                      >
                        {error}
                      </Typography>
                    )
                  )}
              </>
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
            inputProps={{
              'data-testid': `${pollName}_rate_later__auto_remove`,
            }}
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

export default GenericPollUserSettingsForm;
