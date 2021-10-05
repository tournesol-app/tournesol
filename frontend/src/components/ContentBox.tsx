import React from 'react';
import { Box, Container } from '@material-ui/core';

interface Props {
  maxWidth?: false | 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  children: React.ReactNode;
}

const ContentBox = ({ children, maxWidth }: Props) => {
  if (!children) {
    return null;
  }
  return (
    <Box p={[2, 2, 3]}>
      <Container maxWidth={maxWidth}>{children}</Container>
    </Box>
  );
};

export default ContentBox;
