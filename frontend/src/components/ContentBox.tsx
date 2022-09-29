import React from 'react';
import { Box, Container } from '@mui/material';

import { contentHeaderHeight } from 'src/components/ContentHeader';
import { topBarHeight } from 'src/features/frame/components/topbar/TopBar';

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

  // 224px represents the current height of the <Footer>. If more items are
  // added in it, its height may increase.
  const innerHeight =
    window.innerHeight - topBarHeight - contentHeaderHeight - 224;

  return (
    <Box
      px={[noMinPaddingX ? 0 : 2, 2, 3]}
      py={2}
      // Push the global footer away, to avoid displaying it in the middle
      // of the screen.
      minHeight={`${innerHeight}px`}
    >
      <Container maxWidth={maxWidth} disableGutters>
        {children}
      </Container>
    </Box>
  );
};

export default ContentBox;
