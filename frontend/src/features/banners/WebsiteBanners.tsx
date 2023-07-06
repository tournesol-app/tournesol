import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, useTheme } from '@mui/material';

import { BackofficeService, Banner } from 'src/services/openapi';

import WebsiteBanner from './WebsiteBanner';

const sortBannersByPriority = (a: Banner, b: Banner) => {
  if (a.priority !== undefined && b.priority !== undefined) {
    return b.priority - a.priority;
  }

  return 0;
};

/**
 * Display the banners returned by the API.
 *
 * Today, only the banner with the highest priority is displayed.
 */
const WebsiteBanners = () => {
  const theme = useTheme();
  const { i18n } = useTranslation();

  const [banners, setBanners] = useState<Array<Banner>>([]);

  useEffect(() => {
    async function getBanners() {
      const bannersList = await BackofficeService.backofficeBannersList(
        {}
      ).catch(() => {
        console.warn('Failed to retrieve the banners from the API.');
      });

      if (bannersList?.results && bannersList.results.length > 0) {
        bannersList.results.sort(sortBannersByPriority);
        setBanners(bannersList.results);
      }
    }

    getBanners();
  }, [i18n.resolvedLanguage]);

  if (
    banners.length <= 0 ||
    banners[0].title === '' ||
    banners[0].text === ''
  ) {
    return <></>;
  }

  return (
    <Box pt={3} bgcolor={theme.palette.background.emphatic}>
      <WebsiteBanner banner={banners[0]} />
    </Box>
  );
};

export default WebsiteBanners;