import React from 'react';
import { Box, SxProps, Tooltip } from '@mui/material';
import { useCurrentPoll } from 'src/hooks';
import { criteriaIcon } from 'src/utils/criteria';

const CriteriaIcon = ({
  criteriaName,
  emojiSize = '16px',
  imgWidth = '18px',
  tooltip,
  sx = {},
}: {
  criteriaName: string;
  emojiSize?: string;
  imgWidth?: string;
  tooltip?: string;
  sx?: SxProps;
}) => {
  const { getCriteriaLabel } = useCurrentPoll();
  const { emoji, imagePath } = criteriaIcon(criteriaName);
  const criteriaLabel = getCriteriaLabel(criteriaName);

  // If `tooltip` is empty, null or undefined, fallback to `criteriaLabel`.
  // If `criteriaLabel` is empty, null or undefined, fallback to `criteriaName`.
  const tooltipTitle = tooltip || criteriaLabel || criteriaName;

  return (
    <Box
      sx={{
        '& img': {
          display: 'block',
        },
        ...sx,
      }}
    >
      <Tooltip title={tooltipTitle}>
        {emoji ? (
          <Box fontSize={emojiSize}>{emoji}</Box>
        ) : (
          <img src={imagePath} width={imgWidth} alt={criteriaLabel} />
        )}
      </Tooltip>
    </Box>
  );
};

export default CriteriaIcon;
