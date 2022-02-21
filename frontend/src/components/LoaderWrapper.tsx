import React from 'react';
import { Box, CircularProgress } from '@mui/material';

interface LoaderProps {
  isLoading: boolean;
  children: React.ReactNode;
}

/**
 * Wraps content that should be represented as loading when
 * `isLoading`is True. The content will then be displayed as greyed-out,
 * and a circular loader will be visibled in an overlay.
 */
const LoaderWrapper = ({ isLoading, children }: LoaderProps) => {
  return (
    <>
      {isLoading && (
        <Box position="relative">
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
        sx={{
          ...(isLoading && {
            opacity: '30%',
            filter: 'grayscale(100%) blur(2px)',
            pointerEvents: 'none',
          }),
        }}
      >
        {children}
      </Box>
    </>
  );
};

export default LoaderWrapper;
