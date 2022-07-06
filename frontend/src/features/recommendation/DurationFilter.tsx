import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Slider } from '@mui/material';

import { TitledSection } from 'src/components';

const TYPING_DELAY = 30; // in milliseconds
const INFINITE_DURATION = 100000; //approximately 2 months long

interface DurationFilterProps {
  valueMax: string;
  valueMin: string;
  onChangeCallback: (filter: { param: string; value: string }) => void;
}

function DurationFilter({
  valueMax,
  valueMin,
  onChangeCallback,
}: DurationFilterProps) {
  const { t } = useTranslation();

  const [maxDuration, setMaxDuration] = useState<string>(valueMax);
  const [minDuration, setMinDuration] = useState<string>(valueMin);
  const breaks = [0, 100, 200, 300, 400, 500, 600, 700];
  const labels = [0, 2, 5, 10, 20, 60, 120, 480];

  const handleChange = (event: Event, newValue: number | number[]) => {
    let [minVal, maxVal] = Array.isArray(newValue)
      ? newValue
      : [newValue, newValue];
    minVal = Math.round(calculateValue(minVal));
    maxVal = Math.round(calculateValue(maxVal));
    setMinDuration(minVal.toString());
    setMaxDuration(maxVal.toString());
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
    } else if (value < Math.max(...labels)) {
      const hours = Math.floor(value / 60);
      const minutes = Math.round(value - hours * 60);
      return minutes < 10 ? `${hours}h0${minutes}m` : `${hours}h${minutes}m`;
    }
    return `>8h`;
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
    return INFINITE_DURATION;
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
    return Math.max(...breaks);
  }

  const marks = [
    { value: 0, label: '0s' },
    { value: 100, label: '2m' },
    { value: 200, label: '5m' },
    { value: 300, label: '10m' },
    { value: 400, label: '20m' },
    { value: 500, label: '1h' },
    { value: 600, label: '2h' },
    { value: 700, label: '>8h' },
  ];

  return (
    <TitledSection title={t('filter.duration.title')}>
      <Slider
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
        value={[
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
