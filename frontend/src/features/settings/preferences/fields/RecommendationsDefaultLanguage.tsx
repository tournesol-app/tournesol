import React from 'react';

import LanguageFilter from 'src/features/recommendation/LanguageFilter';

interface RecommendationsDefaultLanguageProps {
  value: string[];
  onChange: (target: string[]) => void;
}

const RecommendationsDefaultLanguage = ({
  value,
  onChange,
}: RecommendationsDefaultLanguageProps) => {
  return (
    <LanguageFilter
      value={value.join(',')}
      onChange={(target) => {
        onChange(target.split(','));
      }}
    />
  );
};

export default RecommendationsDefaultLanguage;
