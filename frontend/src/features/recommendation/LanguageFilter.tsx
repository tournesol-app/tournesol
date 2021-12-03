import React from 'react';
import ChoicesFilterSection from 'src/components/filter/ChoicesFilterSection';

const languageChoices = {
  en: 'English',
  fr: 'French',
  de: 'German',
};

interface Props {
  value: string;
  onChange: (value: string) => void;
}

function LanguageFilter(props: Props) {
  return (
    <ChoicesFilterSection
      title="Language"
      choices={languageChoices}
      {...props}
    ></ChoicesFilterSection>
  );
}

export default LanguageFilter;
