import React from 'react';

import { LanguageField } from 'src/features/recommendation/LanguageFilter';

interface ItemsLanguagesProps {
  label: string;
  helpText: string;
  value: string[];
  onChange: (target: string[]) => void;
}

const ItemsLanguages = ({
  label,
  helpText,
  value,
  onChange,
}: ItemsLanguagesProps) => {
  return (
    <LanguageField
      label={label}
      helperText={helpText}
      value={value.join(',')}
      onChange={(values) => {
        if (!values) {
          onChange([]);
        } else {
          onChange(values.split(','));
        }
      }}
    />
  );
};

export default ItemsLanguages;
