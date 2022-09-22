import React from 'react';
import { Box, Container } from '@mui/material';

interface Props {
  maxWidth?: false | 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  children: React.ReactNode;
  noMinPaddingX?: boolean;
}

/**
 * A generic top-level container allowing to have the same layout on all
 * pages.
 *
 * Use it in combination with <ContentHeader> to display the body of the
 * pages.
 */
const ContentBox = ({
  children,
  maxWidth = false,
  noMinPaddingX = false,
}: Props) => {
  if (!children) {
    return null;
  }
  return (
    <Box
      px={[noMinPaddingX ? 0 : 2, 2, 3]}
      py={2}
      // Push the global footer away, to avoid displaying it in the middle
      // of the screen.
      minHeight="555px"
    >
      <Container maxWidth={maxWidth} disableGutters>
        {children}
      </Container>
    </Box>
  );
};

export default ContentBox;
