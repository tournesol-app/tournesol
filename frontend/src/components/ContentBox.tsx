import React from 'react';
import { Box, Container } from '@mui/material';

interface Props {
  maxWidth?: false | 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  children: React.ReactNode;
  noMinPaddingX?: boolean;
}

const ContentBox = ({
  children,
  maxWidth = false,
  noMinPaddingX = false,
}: Props) => {
  if (!children) {
    return null;
  }
  return (
    <Box px={[noMinPaddingX ? 0 : 2, 2, 3]} py={2}>
      <Container maxWidth={maxWidth} disableGutters>
        {children}
      </Container>
    </Box>
  );
};

export default ContentBox;
