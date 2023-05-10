import React, { useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';

import {
  Button,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
  TextField,
  Typography,
} from '@mui/material';

import {
  DEFAULT_RATE_LATER_AUTO_REMOVAL,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';
import {
  replaceSettings,
  selectSettings,
} from 'src/features/settings/userSettingsSlice';
import { useNotifications } from 'src/hooks';
import {
  ApiError,
  BlankEnum,
  ComparisonUi_weeklyCollectiveGoalDisplayEnum,
  TournesolUserSettings,
  UsersService,
} from 'src/services/openapi';

/**
 * Display a generic user settings form that can be used by any poll.
 */
const VideosPollUserSettingsForm = () => {
  const pollName = YOUTUBE_POLL_NAME;

  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { showSuccessAlert, showErrorAlert } = useNotifications();

  const [disabled, setDisabled] = useState(false);
  const [apiErrors, setApiErrors] = useState<ApiError | null>(null);

  // List of user's settings.
  const userSettings = useSelector(selectSettings).settings;

  // Comparison (page)
  const [compUiWeeklyColGoalDisplay, setCompUiWeeklyColGoalDisplay] = useState<
    ComparisonUi_weeklyCollectiveGoalDisplayEnum | BlankEnum
  >(
    userSettings?.[pollName]?.comparison_ui__weekly_collective_goal_display ??
      ComparisonUi_weeklyCollectiveGoalDisplayEnum.ALWAYS
  );

  // Rate-later settings
  const [rateLaterAutoRemoval, setRateLaterAutoRemoval] = useState(
    userSettings?.[pollName]?.rate_later__auto_remove ??
      DEFAULT_RATE_LATER_AUTO_REMOVAL
  );

  const changeCompUiDisplayWeeklyColGoal = (event: SelectChangeEvent) => {
    setCompUiWeeklyColGoalDisplay(
      event.target.value as
        | ComparisonUi_weeklyCollectiveGoalDisplayEnum
        | BlankEnum
    );
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setDisabled(true);

    const response: void | TournesolUserSettings =
      await UsersService.usersMeSettingsPartialUpdate({
        requestBody: {
          [pollName]: {
            comparison_ui__weekly_collective_goal_display:
              compUiWeeklyColGoalDisplay,
            rate_later__auto_remove: rateLaterAutoRemoval,
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
            {t('pollUserSettingsForm.comparisonPage')}
          </Typography>
        </Grid>
        {/*
            Comparison UI: weekly collective goal display
        */}
        <Grid item>
          <FormControl fullWidth>
            <InputLabel
              id="label__comparison_ui__weekly_collective_goal_display"
              color="secondary"
            >
              {t('pollUserSettingsForm.displayTheTheWeeklyCollectiveGoal')}
            </InputLabel>
            <Select
              size="small"
              color="secondary"
              id="comparison_ui__weekly_collective_goal_display"
              labelId="label__comparison_ui__weekly_collective_goal_display"
              value={compUiWeeklyColGoalDisplay}
              label={t(
                'pollUserSettingsForm.displayTheTheWeeklyCollectiveGoal'
              )}
              onChange={changeCompUiDisplayWeeklyColGoal}
              inputProps={{
                'data-testid': `${pollName}_weekly_collective_goal_display`,
              }}
            >
              {[
                {
                  label: t('pollUserSettingsForm.always'),
                  value: ComparisonUi_weeklyCollectiveGoalDisplayEnum.ALWAYS,
                },
                {
                  label: t('pollUserSettingsForm.websiteOnly'),
                  value:
                    ComparisonUi_weeklyCollectiveGoalDisplayEnum.WEBSITE_ONLY,
                },
                {
                  label: t('pollUserSettingsForm.embeddedOnly'),
                  value:
                    ComparisonUi_weeklyCollectiveGoalDisplayEnum.EMBEDDED_ONLY,
                },
                {
                  label: t('pollUserSettingsForm.never'),
                  value: ComparisonUi_weeklyCollectiveGoalDisplayEnum.NEVER,
                },
              ].map((item) => (
                <MenuItem key={item.value} value={item.value}>
                  {item.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item>
          <Typography variant="h6">
            {t('pollUserSettingsForm.rateLater')}
          </Typography>
        </Grid>
        {/*
            Rate-later list: auto removal threshold
        */}
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
                  count={rateLaterAutoRemoval}
                >
                  Entities will be removed from your rate-later list after
                  {{ rateLaterAutoRemoval }} comparisons.
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
            value={rateLaterAutoRemoval}
            onChange={(event) =>
              setRateLaterAutoRemoval(Number(event.target.value))
            }
            inputProps={{
              min: 1,
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

export default VideosPollUserSettingsForm;
