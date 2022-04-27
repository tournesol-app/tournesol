import React from 'react';
import { Box, SxProps } from '@mui/material';
import { criteriaIcon } from 'src/utils/criteria';

const CriteriaIcon = ({
  criteriaName,
  width = '18px',
  sx = {},
}: {
  criteriaName: string;
  width?: string;
  sx?: SxProps;
}) => {
  const { emoji, imagePath } = criteriaIcon(criteriaName);
  return (
    <Box
      sx={{
        ...sx,
      }}
    >
      {emoji ? emoji : <img src={imagePath} width={width} />}
    </Box>
  );
};

export default CriteriaIcon;
