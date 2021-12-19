import React from 'react';
import clsx from 'clsx';
import { Box, CircularProgress, makeStyles } from '@material-ui/core';

const useStyles = makeStyles(() => ({
  loadingContent: {
    opacity: '30%',
    filter: 'grayscale(100%) blur(2px)',
    pointerEvents: 'none',
  },
}));

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
  const classes = useStyles();

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
      <Box className={clsx({ [classes.loadingContent]: isLoading })}>
        {children}
      </Box>
    </>
  );
};

export default LoaderWrapper;
