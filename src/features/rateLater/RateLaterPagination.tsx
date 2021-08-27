import React from 'react';
import { Button, makeStyles, Paper } from '@material-ui/core';

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
  paginationStatusText: {
    margin: '0 20px',
  },
});

const RateLaterPagination = ({
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
      <span className={classes.paginationStatusText}>
        Showing videos {offset + 1} to {Math.min(count, offset + limit)}
      </span>
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

export default RateLaterPagination;
