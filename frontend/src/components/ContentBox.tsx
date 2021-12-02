import React from 'react';
import { Box, Container } from '@material-ui/core';

interface Props {
  maxWidth?: false | 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  children: React.ReactNode;
  noMinPadding?: boolean;
}

const ContentBox = ({
  children,
  maxWidth = false,
  noMinPadding = false,
}: Props) => {
  if (!children) {
    return null;
  }
  return (
    <Box p={[noMinPadding ? 0 : 2, 2, 3]}>
      <Container maxWidth={maxWidth} disableGutters>
        {children}
      </Container>
    </Box>
  );
};

export default ContentBox;
