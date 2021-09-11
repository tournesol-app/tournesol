import React from 'react';
import { Box, makeStyles, Typography } from '@material-ui/core';

const useStyles = makeStyles({
  contentHeader: {
    background: '#f9f3dc',
    borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
  },
});

const ContentHeader = ({ title }: { title: string }) => {
  const classes = useStyles();

  return (
    <Box px={4} py={2} color="text.secondary" className={classes.contentHeader}>
      <Typography variant="h4">{title}</Typography>
    </Box>
  );
};

export default ContentHeader;
