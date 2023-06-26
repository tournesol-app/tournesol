import React from 'react';
import ContentBox from './ContentBox';
import { Box, Paper, Typography } from '@mui/material';

interface LegalDocumentProps {
  children: React.ReactNode;
  mainTitle: string;
}

export const LegalDocument = ({ children, mainTitle }: LegalDocumentProps) => {
  return (
    <ContentBox maxWidth="md">
      <Typography variant="h3" textAlign="center" mt={2} mb={4}>
        {mainTitle}
      </Typography>
      <Box display="flex" flexDirection="column" gap={4}>
        {children}
      </Box>
    </ContentBox>
  );
};

export const LegalPaper = ({ children }: { children: React.ReactNode }) => {
  return <Paper sx={{ p: 2 }}>{children}</Paper>;
};
