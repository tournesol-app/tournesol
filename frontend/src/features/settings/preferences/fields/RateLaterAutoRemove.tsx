import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { TextField, Typography } from '@mui/material';

import { ApiError } from 'src/services/openapi';

interface RateLaterAutoRemoveProps {
  apiErrors: ApiError | null;
  value: number;
  onChange: (number: number) => void;
  pollName: string;
}

const RateLaterAutoRemoveField = ({
  apiErrors,
  value,
  onChange,
  pollName,
}: RateLaterAutoRemoveProps) => {
  const { t } = useTranslation();

  return (
    <TextField
      required
      fullWidth
      label={t('pollUserSettingsForm.autoRemove')}
      helperText={
        <>
          <Trans
            t={t}
            i18nKey="pollUserSettingsForm.autoRemoveHelpText"
            count={value}
          >
            Entities will be removed from your rate-later list after
            {{ value }} comparisons.
          </Trans>
          {apiErrors &&
            apiErrors.body[pollName]?.rate_later__auto_remove &&
            apiErrors.body[pollName].rate_later__auto_remove.map(
              (error: string, idx: number) => (
                <Typography
                  key={`${pollName}_rate_later__auto_remove_error_${idx}`}
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
      name={`${pollName}_rate_later__auto_remove`}
      color="secondary"
      size="small"
      type="number"
      variant="outlined"
      value={value}
      onChange={(event) => onChange(Number(event.target.value))}
      inputProps={{
        min: 1,
        'data-testid': `${pollName}_rate_later__auto_remove`,
      }}
    />
  );
};

export default RateLaterAutoRemoveField;
