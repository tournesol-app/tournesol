import React from 'react';

import { useLocation } from 'react-router-dom';
import { Typography, FormControlLabel, Checkbox, Box } from '@material-ui/core';
import { CheckCircle, CheckCircleOutline } from '@material-ui/icons';
import { FilterSection } from 'src/components/filter/FilterSection';

function LanguageFilter({
  setFilter,
}: {
  setFilter: (k: string, v: string) => void;
}) {
  const Location = useLocation();
  const searchParams = new URLSearchParams(Location.search);
  const language = searchParams.get('language') || '';

  const languageChoices = {
    en: 'English',
    fr: 'French',
    de: 'German',
  };

  const handleLanguageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFilter('language', event.target.name);
  };

  return (
    <FilterSection title="Language">
      <Box display="flex" flexDirection="column">
        {Object.entries(languageChoices).map(
          ([language_key, language_value]) => (
            <FormControlLabel
              control={
                <Checkbox
                  icon={<CheckCircleOutline />}
                  checkedIcon={<CheckCircle />}
                  checked={language == language_key}
                  onChange={handleLanguageChange}
                  name={language_key}
                  size="small"
                />
              }
              label={<Typography variant="body2">{language_value}</Typography>}
              key={language_key}
            />
          )
        )}
      </Box>
    </FilterSection>
  );
}

export default LanguageFilter;
