import React from 'react';
import { Box, SxProps } from '@mui/material';
import { criteriaToEmoji } from 'src/utils/constants';

const CriteriaIcon = ({
  criteriaName,
  width = '18px',
  sx = {},
}: {
  criteriaName: string;
  width?: string;
  sx?: SxProps;
}) => {
  const emoji =
    criteriaName in criteriaToEmoji ? criteriaToEmoji[criteriaName] : undefined;
  const imagePath =
    criteriaName === 'largely_recommended'
      ? '/svg/LogoSmall.svg'
      : `/svg/${criteriaName}.svg`;
  return (
    <Box
      sx={{
        '& img': {
          display: 'block',
        },
        ...sx,
      }}
    >
      {emoji ? emoji : <img src={imagePath} width={width} />}
    </Box>
  );
};

export default CriteriaIcon;
