import React from 'react';
import { Box, BoxProps, SxProps, Tooltip } from '@mui/material';

interface Props extends BoxProps {
  score: number;
  unsafe?: boolean;
  tooltip?: React.ReactNode;
  sx?: SxProps;
}

const TournesolScore = ({
  score,
  tooltip = '',
  unsafe = false,
  sx = {},
}: Props) => {
  return (
    <Tooltip title={tooltip} placement="right">
      <Box
        data-testid="video-card-overall-score"
        sx={[
          {
            display: 'inline-flex',
            alignItems: 'center',
            alignSelf: 'baseline',
          },
          ...(Array.isArray(sx) ? sx : [sx]),
          unsafe && {
            filter: 'grayscale(100%)',
            opacity: 0.6,
          },
        ]}
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
