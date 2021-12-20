import React from 'react';
import { ChoicesFilterSection } from 'src/components';

const languagesChoice = {
  en: 'English',
  fr: 'French',
  de: 'German',
};

interface Props {
  value: string;
  onChange: (value: string) => void;
}

function LanguagesFilter(props: Props) {
  return (
    <ChoicesFilterSection
      title="Languages"
      choices={languagesChoice}
      {...props}
    ></ChoicesFilterSection>
  );
}

export default LanguagesFilter;
