import React from 'react';
import { ChoicesFilterSection } from 'src/components';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

export const dateChoices = {
  Today: 'Today',
  Week: 'This week',
  Month: 'This month',
  Year: 'This year',
};

function DateFilter(props: Props) {
  return (
    <ChoicesFilterSection
      title="Upload date"
      multipleChoice={false}
      choices={dateChoices}
      {...props}
    />
  );
}

export default DateFilter;
