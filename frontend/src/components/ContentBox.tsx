import React from 'react';
import { Box, Container, useMediaQuery, useTheme } from '@mui/material';

import {
  topBarHeight,
  topBarHeightSm,
} from 'src/features/frame/components/topbar/TopBar';

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
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));
  const contentHeight = isSmallScreen ? topBarHeightSm : topBarHeight;

  if (!children) {
    return null;
  }

  return (
    <Box
      px={[noMinPaddingX ? 0 : 2, 2, 3]}
      py={2}
      // Push the global footer away, to avoid displaying it in the middle
      // of the screen.
      minHeight={`calc(100vh - ${contentHeight}px)`}
    >
      <Container maxWidth={maxWidth} disableGutters>
        {children}
      </Container>
    </Box>
  );
};

export default ContentBox;
