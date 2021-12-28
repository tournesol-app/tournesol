import React from 'react';
import { ChoicesFilterSection } from 'src/components';

export const languageChoices = {
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
      multipleChoice={true}
      choices={languageChoices}
      {...props}
    ></ChoicesFilterSection>
  );
}

export default LanguageFilter;
