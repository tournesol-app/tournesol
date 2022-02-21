import React from 'react';
import { Typography } from '@mui/material';

interface Props {
  title: string;
  children: React.ReactNode;
}

const TitledSection = ({ title, children }: Props) => {
  return (
    <>
      <Typography
        variant="h6"
        sx={{
          borderBottom: '1px solid #E7E5DB',
          marginBottom: '0.3em',
        }}
      >
        {title}
      </Typography>
      {children}
    </>
  );
};

export default TitledSection;
