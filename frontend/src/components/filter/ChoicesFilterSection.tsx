import React from 'react';

import { Typography, FormControlLabel, Checkbox, Box } from '@material-ui/core';
import { CheckCircle, CheckCircleOutline } from '@material-ui/icons';
import { FilterSection } from 'src/components/filter/FilterSection';

interface Props {
  title: string;
  value: string;
  choices: Record<string, string>;
  onChange: (value: string) => void;
}

const ChoicesFilterSection = ({ title, value, choices, onChange }: Props) => {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      onChange(event.target.name);
    } else {
      onChange('');
    }
  };

  return (
    <FilterSection title={title}>
      <Box display="flex" flexDirection="column">
        {Object.entries(choices).map(([choiceValue, choiceLabel]) => {
          const checked = value === choiceValue;
          return (
            <FormControlLabel
              control={
                <Checkbox
                  icon={<CheckCircleOutline />}
                  checkedIcon={<CheckCircle />}
                  checked={checked}
                  onChange={handleChange}
                  name={choiceValue}
                  size="small"
                />
              }
              label={
                <Typography
                  variant="body2"
                  color={checked ? 'secondary' : 'textPrimary'}
                >
                  {choiceLabel}
                </Typography>
              }
              key={choiceValue}
            />
          );
        })}
      </Box>
    </FilterSection>
  );
};

export default ChoicesFilterSection;
