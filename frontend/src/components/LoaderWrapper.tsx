import React from 'react';
import { Box, CircularProgress, SxProps } from '@mui/material';

interface LoaderProps {
  isLoading: boolean;
  children: React.ReactNode;
  circularProgress?: boolean;
  sx?: SxProps;
}

/**
 * Wraps content that should be represented as loading when
 * `isLoading`is True. The content will then be displayed as greyed-out,
 * and a circular loader will be visibled in an overlay.
 */
const LoaderWrapper = ({
  isLoading,
  children,
  circularProgress = true,
  sx = {},
}: LoaderProps) => {
  return (
    <>
      {isLoading && circularProgress && (
        <Box position="relative" width="100%">
          <Box
            position="absolute"
            display="flex"
            width="100%"
            minHeight="100px"
            alignItems="center"
            justifyContent="center"
          >
            <CircularProgress size={50} />
          </Box>
        </Box>
      )}
      <Box
        sx={[
          ...(Array.isArray(sx) ? sx : [sx]),
          isLoading && {
            opacity: '30%',
            filter: 'grayscale(100%) blur(2px)',
            pointerEvents: 'none',
          },
        ]}
      >
        {children}
      </Box>
    </>
  );
};

export default LoaderWrapper;
