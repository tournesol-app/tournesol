import React from 'react';
import { useTranslation } from 'react-i18next';

import { IconButton, InputAdornment, TextField } from '@mui/material';
import { Clear } from '@mui/icons-material';

import { TitledSection } from 'src/components';

interface Props {
  value: number;
  onChangeCallback: (value: string) => void;
}

function DurationFilter(props: Props) {
  const { t } = useTranslation();

  const [duration, setDuration] = React.useState<string>('');

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value: string = event.target.value;
    setDuration(value);
    props.onChangeCallback(value);
  };

  const clearMaxDuration = () => {
    setDuration('');
    props.onChangeCallback('');
  };

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
