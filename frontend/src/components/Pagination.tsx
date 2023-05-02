import React from 'react';
import { useTranslation, Trans } from 'react-i18next';

import {
  Button,
  Paper,
  Pagination as PaginationComponent,
  Box,
  useMediaQuery,
  useTheme,
  Typography,
} from '@mui/material';

import { scrollToTop } from 'src/utils/ui';

interface PaginationProps {
  limit: number;
  offset: number;
  count: number;
  onOffsetChange: (n: number) => void;
}

const Pagination = ({
  offset,
  limit,
  onOffsetChange,
  count,
}: PaginationProps) => {
  const theme = useTheme();
  const { t } = useTranslation();

  const lessThanSm = useMediaQuery(theme.breakpoints.down('sm'), {
    noSsr: true,
  });
  const lessThanLg = useMediaQuery(theme.breakpoints.down('lg'), {
    noSsr: true,
  });

  const currentPage = (offset + limit) / limit;
  const totalPages = Math.floor(count / limit) + (count % limit === 0 ? 0 : 1);

  const firstElementIdx = count === 0 ? 0 : offset + 1;
  const lastElementIdx =
    currentPage === totalPages ? count : currentPage * limit;

  const handleChangePage = (
    _event: React.ChangeEvent<unknown>,
    page: number
  ) => {
    scrollToTop();
    onOffsetChange(Math.max(0, (page - 1) * limit));
  };

  const previousPageStep = (step: number) => {
    if (currentPage > 1) {
      scrollToTop();
      const page = Math.max(1, currentPage - step);
      onOffsetChange(Math.max(page * limit - limit, 0));
    }
  };

  const nextPageStep = (step: number) => {
    if (currentPage < Math.ceil(count / limit)) {
      scrollToTop();
      const page = Math.min(totalPages, currentPage + step);
      onOffsetChange(page * limit - limit);
    }
  };

  return (
    <Paper
      square
      variant="outlined"
      sx={{
        padding: 2,
        gap: 1,
        display: 'flex',
        alignItems: 'center',
        flexDirection: 'row',
        justifyContent: 'center',
        flexWrap: 'wrap',
      }}
    >
      <Box width="100%" display="flex" justifyContent="center">
        <Typography variant="body2">
          <Trans t={t} i18nKey="pagination.showingCounts" count={count}>
            Showing {{ firstElementIdx }} - {{ lastElementIdx }} of {{ count }}
          </Trans>
        </Typography>
      </Box>
      {/* Do not display the navigation when the number of elements is low. */}
      {count > limit && (
        <>
          <PaginationComponent
            count={totalPages}
            page={currentPage}
            siblingCount={lessThanLg ? 1 : 3}
            boundaryCount={lessThanLg ? 1 : 2}
            onChange={handleChangePage}
            hidePrevButton
            hideNextButton
            sx={{
              mt: 1,
            }}
          />
          <Box
            width="100%"
            display="flex"
            justifyContent="center"
            alignItems="center"
            flexWrap="wrap"
            gap={1}
          >
            <Button
              id="pagination_1_prev"
              size="small"
              variant="contained"
              disabled={currentPage <= 1}
              onClick={() => previousPageStep(1)}
            >
              {'< -1'}
            </Button>
            <Button
              id="pagination_10_prev"
              size="small"
              variant="outlined"
              disabled={currentPage <= 1}
              sx={{
                color: theme.palette.text.primary,
                borderColor: theme.palette.text.primary,
              }}
              onClick={() => previousPageStep(10)}
            >
              {'< -10'}
            </Button>
            {totalPages > 100 && !lessThanSm && (
              <>
                <Button
                  id="pagination_100_prev"
                  size="small"
                  variant="outlined"
                  disabled={currentPage <= 1}
                  sx={{
                    color: theme.palette.text.primary,
                    borderColor: theme.palette.text.primary,
                  }}
                  onClick={() => previousPageStep(100)}
                >
                  {'< -100'}
                </Button>
                <Button
                  id="pagination_100_next"
                  size="small"
                  variant="outlined"
                  disabled={currentPage >= totalPages}
                  sx={{
                    color: theme.palette.text.primary,
                    borderColor: theme.palette.text.primary,
                  }}
                  onClick={() => nextPageStep(100)}
                >
                  {'+100 >'}
                </Button>
              </>
            )}
            <Button
              id="pagination_10_next"
              size="small"
              variant="outlined"
              disabled={currentPage >= totalPages}
              sx={{
                color: theme.palette.text.primary,
                borderColor: theme.palette.text.primary,
              }}
              onClick={() => nextPageStep(10)}
            >
              {'+10 >'}
            </Button>
            <Button
              id="pagination_1_next"
              size="small"
              variant="contained"
              disabled={currentPage >= totalPages}
              onClick={() => nextPageStep(1)}
            >
              {'+1 >'}
            </Button>
          </Box>
        </>
      )}
    </Paper>
  );
};

export default Pagination;
