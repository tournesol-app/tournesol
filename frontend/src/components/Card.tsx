import React from 'react';
import Card from '@mui/material/Card';

interface Props {
  children: React.ReactNode;
  sx?: object;
  [props: string]: unknown;
}

const CustomCard = ({ children, sx, ...props }: Props) => {
  return (
    <Card
      {...props}
      sx={{
        background: '#FFFFFF',
        border: '1px solid #DCD8CB',
        boxShadow:
          '0px 0px 8px rgba(0, 0, 0, 0.02), 0px 2px 4px rgba(0, 0, 0, 0.05)',
        borderRadius: '4px',
        ...(sx || {}),
      }}
    >
      {children}
    </Card>
  );
};

export default CustomCard;
