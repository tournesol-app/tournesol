import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { IconButton, InputAdornment, TextField } from '@mui/material';
import { Clear } from '@mui/icons-material';

import { TitledSection } from 'src/components';

const TYPING_DELAY = 400;

interface DurationFilterProps {
  valueMax: string;
  valueMin: string;
  onChangeMaxCallback: (value: string) => void;
  onChangeMinCallback: (value: string) => void;
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
  onChangeMaxCallback,
  onChangeMinCallback,
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
    onChangeMaxCallback('');
  };

  const clearMinDuration = () => {
    setMinDuration('');
    onChangeMinCallback('');
  };

  useEffect(() => {
    const timeOutId = setTimeout(
      () => onChangeMaxCallback(maxDuration),
      TYPING_DELAY
    );
    return () => clearTimeout(timeOutId);
  }, [maxDuration, onChangeMaxCallback]);

  useEffect(() => {
    const timeOutId = setTimeout(
      () => onChangeMinCallback(minDuration),
      TYPING_DELAY
    );
    return () => clearTimeout(timeOutId);
  }, [minDuration, onChangeMinCallback]);

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
    </TitledSection>
  );
}

export default DurationFilter;
