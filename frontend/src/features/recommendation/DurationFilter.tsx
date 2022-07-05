import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { IconButton, InputAdornment, TextField, Slider } from '@mui/material';
import { Clear } from '@mui/icons-material';
import { styled } from '@mui/material/styles';
//import backgroundImage from "/logos/Tournesol_minilogo.png";

import { TitledSection } from 'src/components';

// in milliseconds
const TYPING_DELAY = 300;

interface DurationFilterProps {
  valueMax: string;
  valueMin: string;
  onChangeCallback: (filter: { param: string; value: string }) => void;
}

const TournesolSlider = styled(Slider)(() => ({
  '& .MuiSlider-thumb': {
    backgroundImage: `url("https://github.com/tournesol-app/tournesol/blob/main/frontend/public/logos/Tournesol_Logo.png")`,
  },
}));

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
  const breaks = [0, 100, 200, 300, 400, 500, 600];
  const labels = [0, 2, 5, 10, 20, 60, 120];

  const handleChange = (event: Event, newValue: number | number[]) => {
    const [minVal, maxVal] = Array.isArray(newValue)
      ? newValue
      : [newValue, newValue];
    setMinDuration(Math.round(calculateValue(minVal)).toString());
    setMaxDuration(Math.round(calculateValue(maxVal)).toString());
  };

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

  function valueLabelFormat(value: number) {
    let seconds = Math.round(value * 60);
    if (seconds < 60) {
      return `${seconds}s`;
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60);
      seconds = Math.round(seconds - minutes * 60);
      return seconds < 10
        ? `${minutes}m0${seconds}s`
        : `${minutes}m${seconds}s`;
    } else if (value < 120) {
      const hours = Math.floor(value / 60);
      const minutes = Math.round(value - hours * 60);
      return minutes < 10 ? `${hours}h0${minutes}m` : `${hours}h${minutes}m`;
    }
    return `>2h`;
  }

  function calculateValue(value: number) {
    for (let i = 0; i < breaks.length; i++) {
      const min = breaks[i - 1];
      const max = breaks[i];
      if (value < max) {
        const pc = (value - min) / (max - min);
        const res = labels[i - 1] + pc * (labels[i] - labels[i - 1]);
        return res;
      }
    }
    return 120;
  }

  function correspondingValue(value: number) {
    for (let i = 0; i < labels.length; i++) {
      const min = labels[i - 1];
      const max = labels[i];
      if (value < max) {
        const pc = (value - min) / (max - min);
        const res = breaks[i - 1] + pc * (breaks[i] - breaks[i - 1]);
        return res;
      }
    }
    return 600;
  }

  const marks = [
    { value: 0, label: '0s' },
    { value: 100, label: '2m' },
    { value: 200, label: '5m' },
    { value: 300, label: '10m' },
    { value: 400, label: '20m' },
    { value: 500, label: '1h' },
    { value: 600, label: '>2h' },
  ];

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
      <TournesolSlider
        min={Math.min(...breaks)}
        max={Math.max(...breaks)}
        getAriaLabel={() => 'Duration range'}
        onChange={handleChange}
        valueLabelDisplay="auto"
        getAriaValueText={valueLabelFormat}
        valueLabelFormat={valueLabelFormat}
        defaultValue={[
          correspondingValue(parseInt(minDuration)),
          correspondingValue(parseInt(maxDuration)),
        ]}
        marks={marks}
        scale={calculateValue}
      />
    </TitledSection>
  );
}

export default DurationFilter;
