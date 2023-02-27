import React from 'react';

import Grid from '@mui/material/Grid';

import AccountInfo from './AccountInfo';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import Search from './Search';
import Logo from './Logo';

const LargeScreenTopBar = () => {
  const { options } = useCurrentPoll();

  return (
    <>
      <Logo />
      <Grid item md={4}>
        {options?.withSearchBar && <Search />}
      </Grid>
      <AccountInfo />
    </>
  );
};

export default LargeScreenTopBar;
