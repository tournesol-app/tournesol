import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { IconButton, InputAdornment, TextField } from '@mui/material';
import { Clear } from '@mui/icons-material';

import { TitledSection } from 'src/components';

const TYPING_DELAY = 400;

interface DurationFilterProps {
  value: string;
  onChangeCallback: (value: string) => void;
}

/**
 * Display a `TextField` of type number, calling a callback when the input
 * value changes.
 *
 * The `TYPING_DELAY` ensures the user has the time to type several digit
 * before triggering the callback.
 */
function DurationFilter({ value, onChangeCallback }: DurationFilterProps) {
  const { t } = useTranslation();

  const [duration, setDuration] = useState<string>(value);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value: string = event.target.value;
    setDuration(value);
  };

  const clearMaxDuration = () => {
    setDuration('');
    onChangeCallback('');
  };

  useEffect(() => {
    const timeOutId = setTimeout(
      () => onChangeCallback(duration),
      TYPING_DELAY
    );
    return () => clearTimeout(timeOutId);
  }, [duration, onChangeCallback]);

  return (
    <TitledSection title={t('filter.duration.title')}>
      <TextField
        margin="dense"
        fullWidth
        size="small"
        color="secondary"
        variant="outlined"
        type="number"
        name="duration_lte"
        label={t('filter.duration.max.label')}
        value={duration}
        onChange={handleChange}
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                aria-label={t('filter.duration.max.clearAriaLabel')}
                edge="end"
                onClick={clearMaxDuration}
              >
                <Clear />
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
    </TitledSection>
  );
}

export default DurationFilter;
