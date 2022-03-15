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
    const compare = new Intl.Collator(i18n.language).compare;
    return availableRecommendationsLanguages.sort((a, b) =>
      compare(getOptionLabel(a), getOptionLabel(b))
    );
  }, [i18n.language, getOptionLabel]);

  return (
    <TitledSection title={t('filter.language')}>
      <Autocomplete
        multiple
        options={sortedLanguages}
        getOptionLabel={getOptionLabel}
        value={arrayValue}
        onChange={handleChange}
        renderInput={(params) => (
          <TextField {...params} variant="outlined" color="secondary" />
        )}
        filterSelectedOptions
        limitTags={3}
        disableClearable
        data-testid="autocomplete"
      />
    </TitledSection>
  );
}

export default LanguageFilter;
