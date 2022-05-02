import React from 'react';
import { Box, SxProps, Tooltip } from '@mui/material';
import { useCurrentPoll } from 'src/hooks';
import { criteriaIcon } from 'src/utils/criteria';

const CriteriaIcon = ({
  criteriaName,
  emojiSize = '16px',
  imgWidth = '18px',
  imgTitle,
  sx = {},
}: {
  criteriaName: string;
  emojiSize?: string;
  imgWidth?: string;
  imgTitle?: string;
  sx?: SxProps;
}) => {
  const { getCriteriaLabel } = useCurrentPoll();
  const { emoji, imagePath } = criteriaIcon(criteriaName);
  const criteriaLabel = getCriteriaLabel(criteriaName);

  return (
    <Box
      sx={{
        '& img': {
          display: 'block',
        },
        ...sx,
      }}
    >
      <Tooltip title={imgTitle ? imgTitle : criteriaLabel}>
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
