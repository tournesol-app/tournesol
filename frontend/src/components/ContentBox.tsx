import React from 'react';
import { Box, Container, SxProps } from '@mui/material';

import { topBarHeight } from 'src/features/frame/components/topbar/TopBar';

interface Props {
  maxWidth?: false | 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  children: React.ReactNode;
  noMinPaddingX?: boolean;
  sx?: SxProps;
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
  sx,
}: Props) => {
  if (!children) {
    return null;
  }

  return (
    <Box
      sx={{
        px: [noMinPaddingX ? 0 : 2, 2, 3],
        py: 2,
        // Push the global footer away, to avoid displaying it in the middle
        // of the screen.
        minHeight: `calc(100vh - ${topBarHeight}px)`,
        ...sx,
      }}
    >
      <Container maxWidth={maxWidth} disableGutters>
        {children}
      </Container>
    </Box>
  );
};

export default ContentBox;
