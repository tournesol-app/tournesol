import React from 'react';

import { useLocation } from 'react-router-dom';
import { Box, FormControlLabel, Checkbox, Typography } from '@material-ui/core';
import { CheckCircle, CheckCircleOutline } from '@material-ui/icons';
import { FilterSection } from 'src/components/filter/FilterSection';

function DateFilter({
  setFilter,
}: {
  setFilter: (k: string, v: string) => void;
}) {
  const Location = useLocation();
  const searchParams = new URLSearchParams(Location.search);

  const dateChoices = ['Today', 'Week', 'Month', 'Year'];
  const date = searchParams.get('date') || 'Any';

  const handleDateChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFilter('date', event.target.name);
  };

  return (
    <FilterSection title="Upload date">
      <Box display="flex" flexDirection="column">
        {dateChoices.map((label) => (
          <FormControlLabel
            control={
              <Checkbox
                icon={<CheckCircleOutline />}
                checkedIcon={<CheckCircle />}
                checked={date == label}
                onChange={handleDateChange}
                name={label}
                size="small"
              />
            }
            label={<Typography variant="body2">{label}</Typography>}
            key={label}
          />
        ))}
      </Box>
    </FilterSection>
  );
}

export default DateFilter;
