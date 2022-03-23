import React, { useMemo, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import {
  availableRecommendationsLanguages,
  getLanguageName,
} from 'src/utils/recommendationsLanguages';
import { TitledSection } from 'src/components';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

function LanguageFilter({ value, onChange }: Props) {
  const { t, i18n } = useTranslation();

  const getOptionLabel = useCallback(
    (option) => getLanguageName(t, option),
    [t]
  );

  const handleChange = useCallback(
    (event: React.SyntheticEvent<Element, Event>, newValue: string[]) => {
      onChange(newValue.join(','));
    },
    [onChange]
  );

  const arrayValue = useMemo(
    () => (value === '' ? [] : value.split(',')),
    [value]
  );

  const sortedLanguages = useMemo(() => {
    const compare = new Intl.Collator(i18n.resolvedLanguage).compare;
    return availableRecommendationsLanguages.sort((a, b) =>
      compare(getOptionLabel(a), getOptionLabel(b))
    );
  }, [i18n.resolvedLanguage, getOptionLabel]);

  const placeholder = useMemo(
    () => (arrayValue.length === 0 ? t('filter.allLanguages') : undefined),
    [arrayValue.length, t]
  );

  return (
    <TitledSection title={t('filter.language')}>
      <Autocomplete
        multiple
        options={sortedLanguages}
        getOptionLabel={getOptionLabel}
        value={arrayValue}
        onChange={handleChange}
        renderInput={(params) => (
          <TextField
            {...params}
            variant="outlined"
            color="secondary"
            size="small"
            placeholder={placeholder}
          />
        )}
        filterSelectedOptions
        limitTags={3}
        disableClearable
        data-testid="autocomplete"
        sx={{
          '& .MuiAutocomplete-inputRoot': {
            minHeight: '50px',
          },
          '& .MuiAutocomplete-endAdornment': {
            top: 'calc(100% - 39px)',
          },
        }}
      />
    </TitledSection>
  );
}

export default LanguageFilter;
