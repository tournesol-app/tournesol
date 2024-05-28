import React from 'react';

import { Grid, IconButton, Typography } from '@mui/material';

import { openDrawer, closeDrawer, selectFrame } from '../../drawerOpenSlice';
import { useAppSelector, useAppDispatch } from '../../../../app/hooks';

const Logo = () => {
  const drawerOpen = useAppSelector(selectFrame);
  const dispatch = useAppDispatch();

  return (
    <Grid
      item
      xs
      display="flex"
      flexDirection="row"
      alignItems="center"
      columnGap={1}
    >
      <IconButton
        onClick={() => dispatch(drawerOpen ? closeDrawer() : openDrawer())}
        size="large"
        sx={{
          p: 0,
          pl: 1,
        }}
      >
        <img src="/svg/LogoSmall.svg" alt="Tournesol logo" />
      </IconButton>
      <Typography
        variant="h1"
        fontFamily="Poppins-Bold"
        fontSize="1.5em"
        fontWeight="bold"
        lineHeight={1}
        display={{ xs: 'none', md: 'initial' }}
      >
        Tournesol
      </Typography>
    </Grid>
  );
};

export default Logo;
