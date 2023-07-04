import React, { useEffect, useState } from 'react';

import {
  Box,
  Button,
  Grid,
  Paper,
  Stack,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import { Campaign } from '@mui/icons-material';

import { useNotifications } from 'src/hooks';

import { BackofficeService, Banner } from 'src/services/openapi';
import { Link } from 'react-router-dom';

const WebsiteBanners = () => {
  const { contactAdministrator } = useNotifications();

  const theme = useTheme();
  const mediaBelowXl = useMediaQuery(theme.breakpoints.down('xl'));

  const [banners, setBanners] = useState<Array<Banner>>([]);

  // const sortDate = (dateA: string, dateB: string) => {
  //   return  new Date (dateA).getTime() - new Date(dateB).getTime();
  // }

  const sortBanners = (a: Banner, b: Banner) => {
    // if (a.security_advisory && !b.security_advisory) {
    //   return -1;
    // } else if (!a.security_advisory && b.security_advisory) {
    //   return 1;
    // }

    if (a.priority === undefined && b.priority === undefined) {
      return 0;
    } else if (a.priority === undefined) {
      return 1;
    } else if (b.priority === undefined) {
      return -1;
    }

    if (b.priority !== a.priority) {
      return b.priority - a.priority;
    }

    return 0; // remove when uncommenting the other lines

    // return sortDate(b.date_start, a.date_start);
  };

  useEffect(() => {
    async function getBanners() {
      const bannersList = await BackofficeService.backofficeBannersList({
        limit: 100,
      }).catch(() => {
        contactAdministrator('error');
      });

      // TODO : order banners as wished : security -> -priority -> -date_start -> -date_end
      if (bannersList?.results !== undefined) {
        bannersList.results.sort(sortBanners);
        setBanners(bannersList.results);
      }
    }

    getBanners();
  }, [contactAdministrator]);

  return (
    <Box py={3} bgcolor="#1282B2">
      <Grid container width="100%" flexDirection="column" alignItems="center">
        <Grid container item xl={9} width="100%" spacing={2} direction="column">
          {banners.map((banner, idx) => (
            <Grid key={idx} item>
              <Paper sx={{ p: 2 }} square={mediaBelowXl}>
                <Stack
                  // Using != direction per breakpoint requires to define != spacing
                  // per breakpoint.
                  spacing={{ xs: 2, sm: 2 }}
                  direction={{ sm: 'column', md: 'row' }}
                  alignItems="center"
                >
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Campaign fontSize="large" sx={{ color: '#1282B2' }} />
                    <Typography paragraph mb={0}>
                      {banner.text}
                    </Typography>
                    {banner?.action_link && (
                      <Button
                        to={banner.action_link}
                        color="primary"
                        variant="contained"
                        component={Link}
                      >
                        {banner.action_label}
                      </Button>
                    )}
                  </Stack>
                </Stack>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Grid>
    </Box>
  );
};

export default WebsiteBanners;
