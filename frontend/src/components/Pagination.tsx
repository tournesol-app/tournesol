import React from 'react';
import { Button, Paper, Typography } from '@mui/material';

import makeStyles from '@mui/styles/makeStyles';

interface PaginationProps {
  limit: number;
  offset: number;
  count: number;
  onOffsetChange: (n: number) => void;
}

const useStyles = makeStyles({
  paginationContainer: {
    padding: '10px',
    display: 'flex',
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center',
  },
});

const Pagination = ({
  offset,
  limit,
  onOffsetChange,
  count,
}: PaginationProps) => {
  const classes = useStyles();

  return (
    <Paper square variant="outlined" className={classes.paginationContainer}>
      <Button
        disabled={offset <= 0}
        variant="contained"
        color="primary"
        id="id_rate_later_prev"
        onClick={() => {
          onOffsetChange(Math.max(offset - limit, 0));
        }}
      >
        Previous {limit}
      </Button>
      <Typography variant="body2" mx={2}>
        Showing videos {offset + 1} to {Math.min(count, offset + limit)}
        {count && ` of ${count}`}
      </Typography>
      <Button
        disabled={offset + limit >= count}
        variant="contained"
        color="primary"
        id="id_rate_later_next"
        onClick={() => {
          onOffsetChange(Math.min(count, offset + limit));
        }}
      >
        Next {limit}
      </Button>
    </Paper>
  );
};

export default Pagination;
