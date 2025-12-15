import React from 'react';

import { FavoriteBorder } from '@mui/icons-material';
import { Box, Button, Grid } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import AccountInfo from './AccountInfo';
import Logo from './Logo';
import Search from './Search';

const TopBarDesktop = () => {
  const { t } = useTranslation();
  const { options } = useCurrentPoll();

  return (
    <>
      <Logo />
      <Grid item xs>
        {options?.withSearchBar && <Search />}
      </Grid>
      <Box display="flex" flex={0.5} justifyContent="flex-end">
        <Button
          variant="text"
          startIcon={<FavoriteBorder />}
          color="inherit"
          sx={{
            borderColor: 'rgba(0, 0, 0, 0.23)',
            textTransform: 'initial',
            fontWeight: 'bold',
            borderWidth: '2px',
            color: (t) => t.palette.neutral.dark,
          }}
          component={Link}
          to="/about/donate"
        >
          {t('topbar.donate')}
        </Button>
      </Box>
      <AccountInfo />
    </>
  );
};

export default TopBarDesktop;
