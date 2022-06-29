import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { IconButton, InputAdornment, TextField } from '@mui/material';
import { Clear } from '@mui/icons-material';

import { TitledSection } from 'src/components';

// in milliseconds
const TYPING_DELAY = 300;

interface DurationFilterProps {
  valueMax: string;
  valueMin: string;
  onChangeCallback: (filter: { param: string; value: string }) => void;
}

/**
 * Display two `TextField` of type number, calling different callbacks when
 * on of their input values change.
 *
 * The `TYPING_DELAY` ensures the user has the time to type several digit
 * before triggering the callback.
 */
function DurationFilter({
  valueMax,
  valueMin,
  onChangeCallback,
}: DurationFilterProps) {
  const { t } = useTranslation();

  const [maxDuration, setMaxDuration] = useState<string>(valueMax);
  const [minDuration, setMinDuration] = useState<string>(valueMin);

  const handleChangeMax = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value: string = event.target.value;
    setMaxDuration(value);
  };

  const handleChangeMin = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value: string = event.target.value;
    setMinDuration(value);
  };

  const clearMaxDuration = () => {
    setMaxDuration('');
    onChangeCallback({ param: 'duration_lte', value: '' });
  };

  const clearMinDuration = () => {
    setMinDuration('');
    onChangeCallback({ param: 'duration_gte', value: '' });
  };

  useEffect(() => {
    const timeOutId = setTimeout(
      () => onChangeCallback({ param: 'duration_lte', value: maxDuration }),
      TYPING_DELAY
    );

    return () => clearTimeout(timeOutId);
  }, [maxDuration, onChangeCallback]);

  useEffect(() => {
    const timeOutId = setTimeout(
      () => onChangeCallback({ param: 'duration_gte', value: minDuration }),
      TYPING_DELAY
    );

    return () => clearTimeout(timeOutId);
  }, [minDuration, onChangeCallback]);

  return (
    <TitledSection title={t('filter.duration.title')}>
      <TextField
        margin="dense"
        fullWidth
        size="small"
        color="secondary"
        variant="outlined"
        type="number"
        name="duration_gte"
        label={t('filter.duration.min.label')}
        value={minDuration}
        onChange={handleChangeMin}
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                aria-label={t('filter.duration.min.clearAriaLabel')}
                edge="end"
                onClick={clearMinDuration}
              >
                <Clear />
              </IconButton>
            </InputAdornment>
          ),
        }}
        data-testid="filter-duration-gte"
      />
      <TextField
        margin="dense"
        fullWidth
        size="small"
        color="secondary"
        variant="outlined"
        type="number"
        name="duration_lte"
        label={t('filter.duration.max.label')}
        value={maxDuration}
        onChange={handleChangeMax}
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
        data-testid="filter-duration-lte"
      />
    </TitledSection>
  );
}

export default DurationFilter;
