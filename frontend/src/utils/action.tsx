import React from 'react';

import { IconButton, makeStyles } from '@material-ui/core';
import { Compare as CompareIcon } from '@material-ui/icons';

const useStyles = makeStyles(() => ({
  card: {
    alignItems: 'center',
    verticalAlign: 'middle',
  },
}));

export const CompareNowAction = ({ videoId }: { videoId: string }) => {
  const classes = useStyles();

  return (
    <IconButton
      className={classes.card}
      size="medium"
      color="secondary"
      href={`/comparison/?videoA=${videoId}`}
    >
      <CompareIcon />
    </IconButton>
  );
};
