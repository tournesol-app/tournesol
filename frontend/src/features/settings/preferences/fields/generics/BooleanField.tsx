import React from 'react';

import { FormControlLabel, Switch } from '@mui/material';

interface BooleanFieldProps {
  scope: string;
  fieldName: string;
  label: string;
  value: boolean;
  onChange: (target: boolean) => void;
}

const BooleanField = ({
  scope,
  fieldName,
  label,
  value,
  onChange,
}: BooleanFieldProps) => {
  return (
    <FormControlLabel
      control={
        <Switch
          name={`${scope}_${fieldName}`}
          checked={value}
          onChange={() => onChange(!value)}
          size="medium"
          color="secondary"
          inputProps={
            {
              'data-testid': `${scope}_${fieldName}`,
            } as React.InputHTMLAttributes<HTMLInputElement>
          }
        />
      }
      label={label}
    />
  );
};

export default BooleanField;
