import React from 'react';
import { Button, Paper, Typography } from '@mui/material';
import makeStyles from '@mui/styles/makeStyles';
import { useTranslation, Trans } from 'react-i18next';

interface PaginationProps {
  limit: number;
  offset: number;
  count: number;
  onOffsetChange: (n: number) => void;
  itemType?: string;
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
  itemType,
}: PaginationProps) => {
  const { t } = useTranslation();
  const classes = useStyles();

  const firstShowing = offset + 1;
  const lastShowing = Math.min(count, offset + limit);
  const itemTypeText = itemType ?? t('pagination.videos');

  return (
    <Paper square variant="outlined" className={classes.paginationContainer}>
      <Button
        disabled={offset <= 0}
        variant="contained"
        color="primary"
        size="small"
        id="id_rate_later_prev"
        onClick={() => {
          onOffsetChange(Math.max(offset - limit, 0));
        }}
      >
        {'< '}
        <Trans t={t} i18nKey="pagination.previousButton">
          Previous {{ limit }}
        </Trans>
      </Button>
      <Typography variant="body2" mx={2}>
        <Trans t={t} i18nKey="pagination.showingCounts">
          Showing {{ itemTypeText }} {{ firstShowing }} to {{ lastShowing }} of{' '}
          {{ total: count }}
        </Trans>
      </Typography>
      <Button
        disabled={offset + limit >= count}
        variant="contained"
        color="primary"
        size="small"
        id="id_rate_later_next"
        onClick={() => {
          onOffsetChange(Math.min(count, offset + limit));
        }}
      >
        <Trans t={t} i18nKey="pagination.nextButton">
          Next {{ limit }}
        </Trans>
        {' >'}
      </Button>
    </Paper>
  );
};

export default Pagination;
