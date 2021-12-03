import React from 'react';
import ChoicesFilterSection from 'src/components/filter/ChoicesFilterSection';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

const dateChoices = {
  Today: 'Today',
  Week: 'This week',
  Month: 'This month',
  Year: 'This year',
};

function DateFilter(props: Props) {
  return (
    <ChoicesFilterSection
      title="Upload date"
      choices={dateChoices}
      {...props}
    />
  );
}

export default DateFilter;
