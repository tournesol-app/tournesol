import React from 'react';

import { FormControlLabel, Switch } from '@mui/material';

interface BooleanFieldProps {
  scope: string;
  name: string;
  label: string;
  value: boolean;
  onChange: (target: boolean) => void;
}

const BooleanField = ({
  scope,
  name,
  label,
  value,
  onChange,
}: BooleanFieldProps) => {
  return (
    <FormControlLabel
      control={
        <Switch
          name={`${scope}_${name}`}
          checked={value}
          onChange={(event) => onChange(event.target.checked)}
          size="medium"
          color="secondary"
          inputProps={
            {
              'data-testid': `${scope}_${name}`,
            } as React.InputHTMLAttributes<HTMLInputElement>
          }
        />
      }
      label={label}
    />
  );
};

export default BooleanField;
