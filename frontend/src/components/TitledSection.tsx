import React from 'react';
import { Typography } from '@mui/material';

interface Props {
  title: string;
  children: React.ReactNode;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  titleComponent?: React.ElementType<any>;
}

const TitledSection = ({ title, titleComponent, children }: Props) => {
  return (
    <>
      <Typography
        variant="h6"
        component={titleComponent ?? 'h6'}
        sx={{
          borderBottom: '1px solid #E7E5DB',
          marginBottom: '4px',
        }}
      >
        {title}
      </Typography>
      {children}
    </>
  );
};

export default TitledSection;
