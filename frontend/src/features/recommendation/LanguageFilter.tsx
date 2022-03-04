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
  const { t } = useTranslation();

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

  return (
    <TitledSection title={t('filter.language')}>
      <Autocomplete
        multiple
        options={availableRecommendationsLanguages}
        getOptionLabel={getOptionLabel}
        renderInput={(params) => <TextField {...params} variant="standard" />}
        value={arrayValue}
        onChange={handleChange}
        data-testid="autocomplete"
      />
    </TitledSection>
  );
}

export default LanguageFilter;
