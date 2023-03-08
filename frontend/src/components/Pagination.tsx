import React from 'react';
import {
  Typography,
  Button,
  Paper,
  Pagination as PaginationComponent,
  Box,
  useMediaQuery,
  useTheme,
} from '@mui/material';

import { useTranslation, Trans } from 'react-i18next';
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
  const { t } = useTranslation();
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'), {
    noSsr: true,
  });
  const [currentPage, setCurrentPage] = React.useState(
    (offset + limit) / limit
  );
  const [pageSearch, setPageSearch] = React.useState('');
  const totalPages = Math.floor(count / limit) + (count % limit === 0 ? 0 : 1);

  const handleChangePage = (
    _event: React.ChangeEvent<unknown>,
    page: number
  ) => {
    scrollToTop();
    setCurrentPage(page);
    onOffsetChange(Math.max(0, (page - 1) * limit));
  };
  const handlePageSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPageSearch(event.target.value);
  };
  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && /^\d+$/.test(pageSearch)) {
      const page = parseInt(pageSearch, 10);
      if (page > 0 && page <= totalPages) {
        scrollToTop();
        onOffsetChange(Math.max(page * limit - limit, 0));
        setCurrentPage(page);
      }
    }
  };

  const previousPageStep = (step: number) => {
    if (currentPage > 1) {
      scrollToTop();
      const page = Math.max(1, currentPage - step);
      setCurrentPage(page);
      onOffsetChange(Math.max(page * limit - limit, 0));
    }
  };

  const nextPageStep = (step: number) => {
    if (currentPage < Math.ceil(count / limit)) {
      scrollToTop();
      const page = Math.min(totalPages, currentPage + step);
      setCurrentPage(page);
      onOffsetChange(page * limit - limit);
    }
  };

  return (
    <Paper
      square
      variant="outlined"
      sx={{
        padding: '10px',
        display: 'flex',
        alignItems: 'center',
        flexDirection: 'row',
        justifyContent: 'center',
        flexWrap: 'wrap',
      }}
    >
      {isSmallScreen && (
        <PaginationComponent
          count={totalPages}
          page={currentPage}
          onChange={handleChangePage}
          hidePrevButton
          hideNextButton
          sx={{
            flexBasis: {
              xs: '100%',
              sm: 'auto',
            },
            display: 'flex',
            justifyContent: 'center',
            '& ul': {
              justifyContent: 'center',
            },
          }}
        />
      )}
      <Box
        sx={{
          width: '100%',
          display: 'flex',
          justifyContent: isSmallScreen ? 'space-around' : 'center',
          alignItems: 'center',
          marginTop: isSmallScreen ? '8px' : '0px',
          '& button': {
            whiteSpace: 'nowrap',
          },
        }}
      >
        <Button
          variant="contained"
          color="primary"
          size="small"
          id="id_rate_later_100_prev"
          sx={{ marginRight: !isSmallScreen ? '8px' : '0px' }}
          onClick={() => previousPageStep(100)}
        >
          {'< '}
          {isSmallScreen ? (
            '-100'
          ) : (
            <Trans t={t} i18nKey="pagination.previousButton">
              Previous {{ limit: 100 }}
            </Trans>
          )}
        </Button>
        <Button
          variant="contained"
          color="primary"
          size="small"
          id="id_rate_later_10_prev"
          onClick={() => previousPageStep(10)}
        >
          {'< '}
          {isSmallScreen ? (
            '-10'
          ) : (
            <Trans t={t} i18nKey="pagination.previousButton">
              Previous {{ limit: 10 }}
            </Trans>
          )}
        </Button>
        {!isSmallScreen && (
          <PaginationComponent
            count={totalPages}
            page={currentPage}
            siblingCount={3}
            boundaryCount={2}
            onChange={handleChangePage}
            hidePrevButton
            hideNextButton
            sx={{
              '& .MuiPagination-ul': {
                flexWrap: 'nowrap',
              },
            }}
          />
        )}
        <Button
          variant="contained"
          color="primary"
          size="small"
          id="id_rate_later_10_next"
          sx={{ marginRight: !isSmallScreen ? '8px' : '0px' }}
          onClick={() => nextPageStep(10)}
        >
          {isSmallScreen ? (
            '+10'
          ) : (
            <Trans t={t} i18nKey="pagination.nextButton">
              Next {{ limit: 10 }}
            </Trans>
          )}
          {' >'}
        </Button>
        <Button
          variant="contained"
          color="primary"
          size="small"
          id="id_rate_later_100_next"
          onClick={() => nextPageStep(100)}
        >
          {isSmallScreen ? (
            '+100'
          ) : (
            <Trans t={t} i18nKey="pagination.nextButton">
              Next {{ limit: 100 }}
            </Trans>
          )}
          {' >'}
        </Button>
        {!isSmallScreen && (
          <Box display="flex" alignItems="center" style={{ height: '100%' }}>
            <Typography variant="body2" mx={2} style={{ whiteSpace: 'nowrap' }}>
              <Trans t={t} i18nKey="pagination.page">
                Page :
              </Trans>
            </Typography>
            <input
              type="text"
              id="searchPageInput"
              size={3}
              onChange={handlePageSearch}
              onKeyDown={handleKeyDown}
            ></input>
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default Pagination;
