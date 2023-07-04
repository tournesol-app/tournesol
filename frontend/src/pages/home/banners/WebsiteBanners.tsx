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

  const sortBanners = (a: Banner, b: Banner) => {
    if (a.priority !== undefined && b.priority !== undefined) {
      return b.priority - a.priority;
    }

    return 0;
  };

  useEffect(() => {
    async function getBanners() {
      const bannersList = await BackofficeService.backofficeBannersList({
        limit: 100,
      }).catch(() => {
        contactAdministrator('error');
      });

      if (bannersList?.results !== undefined) {
        bannersList.results.sort(sortBanners);
        setBanners(bannersList.results);
      }
    }

    getBanners();
  }, [contactAdministrator]);

  return (
    <>
      {banners[0] !== undefined && (
        <Box py={3} bgcolor="#1282B2">
          <Grid
            container
            width="100%"
            flexDirection="column"
            alignItems="center"
          >
            <Grid item xl={9} width="100%" spacing={2} direction="column">
              <Paper sx={{ p: 2 }} square={mediaBelowXl}>
                <Stack
                  // Using != direction per breakpoint requires to define != spacing
                  // per breakpoint.
                  spacing={{ xs: 2, sm: 2 }}
                  direction={{ sm: 'column', md: 'row' }}
                  alignItems="center"
                  justifyContent="space-between"
                >
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Campaign fontSize="large" sx={{ color: '#1282B2' }} />
                    <Typography paragraph mb={0}>
                      {banners[0].text}
                    </Typography>
                  </Stack>
                  <Box display="flex" justifyContent="flex-end">
                    {banners[0]?.action_link && (
                      <Button
                        to={banners[0].action_link}
                        color="primary"
                        variant="contained"
                        component={Link}
                      >
                        {banners[0].action_label}
                      </Button>
                    )}
                  </Box>
                </Stack>
              </Paper>
            </Grid>
          </Grid>
        </Box>
      )}
    </>
  );
};

export default WebsiteBanners;
