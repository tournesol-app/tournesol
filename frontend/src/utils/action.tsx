import React from 'react';

import { IconButton } from '@material-ui/core';
import { Compare as CompareIcon } from '@material-ui/icons';

export const CompareNowAction = ({ videoId }: { videoId: string }) => {
  return (
    <IconButton
      size="medium"
      color="secondary"
      href={`/comparison/?videoA=${videoId}`}
    >
      <CompareIcon />
    </IconButton>
  );
};
