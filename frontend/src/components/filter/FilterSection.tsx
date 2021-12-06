import React from 'react';
import { Typography } from '@material-ui/core';

interface Props {
  title: string;
  children: React.ReactNode;
}

const FilterSection = ({ title, children }: Props) => {
  return (
    <>
      <Typography
        variant="h6"
        style={{ borderBottom: '1px solid #E7E5DB', marginBottom: '0.3em' }}
      >
        {title}
      </Typography>
      {children}
    </>
  );
};

export default FilterSection;
