import React from 'react';

import { Grid, IconButton, Typography } from '@mui/material';

import { useAppSelector, useAppDispatch } from 'src/app/hooks';
import { InternalLink } from 'src/components';
import { useCurrentPoll } from 'src/hooks';

import { openDrawer, closeDrawer, selectFrame } from '../../drawerOpenSlice';

const Logo = () => {
  const { baseUrl: pollHome } = useCurrentPoll();
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
          px: '6px',
          py: '6px',
          border: '1px solid rgba(0, 0, 0, 0.12)',
          backgroundColor: 'rgba(0, 0, 0, 0.04)',
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
        <InternalLink to={pollHome || '/'} color="text.primary">
          Tournesol
        </InternalLink>
      </Typography>
    </Grid>
  );
};

export default Logo;
