import React from 'react';

import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton';
import { Menu } from '@mui/icons-material';

import { openDrawer, closeDrawer, selectFrame } from '../../drawerOpenSlice';
import { useAppSelector, useAppDispatch } from '../../../../app/hooks';
import PollSelector from './PollSelector';
import { polls } from 'src/utils/constants';

const Logo = () => {
  const drawerOpen = useAppSelector(selectFrame);
  const dispatch = useAppDispatch();

  return (
    <Grid
      item
      md={4}
      xs={'auto'}
      marginRight="auto"
      sx={{
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
      }}
    >
      <IconButton
        onClick={() => dispatch(drawerOpen ? closeDrawer() : openDrawer())}
        size="large"
      >
        <Menu />
      </IconButton>
      <PollSelector polls={polls} />
    </Grid>
  );
};

export default Logo;
