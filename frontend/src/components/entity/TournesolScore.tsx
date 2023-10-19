import React from 'react';
import { Box, BoxProps, Tooltip } from '@mui/material';

interface Props extends BoxProps {
  score: number;
  unsafe?: boolean;
  tooltip?: React.ReactNode;
}

const TournesolScore = ({
  score,
  tooltip = '',
  unsafe = false,
  ...extra
}: Props) => {
  return (
    <Tooltip title={tooltip} placement="right">
      <Box
        display="inline-flex"
        alignItems="center"
        alignSelf="baseline"
        {...(unsafe && {
          sx: {
            filter: 'grayscale(100%)',
            opacity: 0.6,
          },
        })}
        {...extra}
      >
        <img
          alt="sunflower icon"
          src="/svg/tournesol.svg"
          style={{ height: '1em' }}
        />
        <strong>{score.toFixed(0)}</strong>
      </Box>
    </Tooltip>
  );
};

export default TournesolScore;
