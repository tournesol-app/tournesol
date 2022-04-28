import React from 'react';
import { Box, SxProps } from '@mui/material';
import { useCurrentPoll } from 'src/hooks';
import { criteriaIcon } from 'src/utils/criteria';

const CriteriaIcon = ({
  criteriaName,
  width = '18px',
  imgTitle,
  sx = {},
}: {
  criteriaName: string;
  width?: string;
  imgTitle?: string;
  sx?: SxProps;
}) => {
  const { getCriteriaLabel } = useCurrentPoll();
  const { emoji, imagePath } = criteriaIcon(criteriaName);
  return (
    <Box
      sx={{
        '& img': {
          display: 'block',
        },
        ...sx,
      }}
    >
      {emoji ? (
        emoji
      ) : (
        <img
          src={imagePath}
          width={width}
          alt={getCriteriaLabel(criteriaName)}
          title={imgTitle ? imgTitle : criteriaName}
        />
      )}
    </Box>
  );
};

export default CriteriaIcon;
