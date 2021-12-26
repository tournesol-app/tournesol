import React from 'react';
import { ChoicesFilterSection } from 'src/components';

export const isPublicChoices = {
  true: 'Public',
  false: 'Private',
};

interface FilterProps {
  value: string;
  onChange: (value: string) => void;
}

function IsPublicFilter(props: FilterProps) {
  return (
    <ChoicesFilterSection
      title="Filter by visibility"
      multipleChoice={false}
      choices={isPublicChoices}
      {...props}
    ></ChoicesFilterSection>
  );
}

export default IsPublicFilter;
