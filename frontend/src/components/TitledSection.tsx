import React from 'react';
import { Box, IconButton, Typography } from '@mui/material';
import { Save } from '@mui/icons-material';

interface Props {
  title: string;
  children: React.ReactNode;
  canSave?: boolean;
}

const TitledSection = ({ title, children, canSave = false }: Props) => {
  return (
    <>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Typography
          variant="h6"
          sx={{
            borderBottom: '1px solid #E7E5DB',
            marginBottom: '0.3em',
          }}
          style={{ flexGrow: 1, flexShrink: 0 }}
        >
          {title}
        </Typography>
        {canSave ? (
          <IconButton>
            <Save />
          </IconButton>
        ) : null}
      </Box>
      {children}
    </>
  );
};

export default TitledSection;
