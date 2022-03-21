import React from 'react';

interface Props {
  length: number;
  messages: string;
}

const ComparisonSeries = ({ length, messages }: Props) => {
  return <>{messages}</>;
};

export default ComparisonSeries;
