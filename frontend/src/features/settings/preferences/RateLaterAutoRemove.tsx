import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Grid, TextField, Typography } from '@mui/material';

import { ApiError } from 'src/services/openapi';

interface RateLaterAutoRemoveProps {
  apiErrors: ApiError | null;
  rateLaterAutoRemoval: number;
  setRateLaterAutoRemoval: (number: number) => void;
  pollName: string;
}

const RateLaterAutoRemove = ({
  apiErrors,
  rateLaterAutoRemoval,
  setRateLaterAutoRemoval,
  pollName,
}: RateLaterAutoRemoveProps) => {
  const { t } = useTranslation();

  return (
    <>
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
    </>
  );
};

export default RateLaterAutoRemove;
