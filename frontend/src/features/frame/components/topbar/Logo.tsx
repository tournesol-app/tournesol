import React from 'react';

import {
  Box,
  Grid,
  IconButton,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import { Menu } from '@mui/icons-material';

import { useAppSelector, useAppDispatch } from 'src/app/hooks';
import { InternalLink } from 'src/components';
import { useCurrentPoll } from 'src/hooks';

import { openDrawer, closeDrawer, selectFrame } from '../../drawerOpenSlice';

const Logo = () => {
  const { baseUrl: pollHome } = useCurrentPoll();
  const drawerOpen = useAppSelector(selectFrame);
  const dispatch = useAppDispatch();

  const theme = useTheme();
  const mediumScreen = useMediaQuery(theme.breakpoints.up('md'));

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
      >
        <Menu />
      </IconButton>
      <Typography
        variant="h1"
        fontFamily="Poppins-Bold"
        fontSize="1.5em"
        fontWeight="bold"
        lineHeight={1}
      >
        <Box
          display="flex"
          alignItems="center"
          justifyContent="center"
          columnGap={1}
        >
          <InternalLink to={pollHome || '/'}>
            <img src="/svg/LogoSmall.svg" alt="Tournesol logo" />
          </InternalLink>
          {mediumScreen && (
            <InternalLink to={pollHome || '/'} color="text.primary">
              Tournesol
            </InternalLink>
          )}
        </Box>
      </Typography>
    </Grid>
  );
};

export default Logo;
