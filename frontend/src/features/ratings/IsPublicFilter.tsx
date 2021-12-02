import React from 'react';
import { ChoicesFilterSection } from 'src/components';

const isPublicChoices = {
  true: 'Public',
  false: 'Private',
};

interface Props {
  value: string;
  onChange: (value: string) => void;
}

function IsPublicFilter(props: Props) {
  return (
    <ChoicesFilterSection
      title="Filter by visibility"
      choices={isPublicChoices}
      {...props}
    ></ChoicesFilterSection>
  );
}

export default IsPublicFilter;
