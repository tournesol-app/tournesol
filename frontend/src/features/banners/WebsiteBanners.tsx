import React, { useEffect, useState } from 'react';

import { BackofficeService, Banner } from 'src/services/openapi';

import WebsiteBanner from './WebsiteBanner';
import { useTranslation } from 'react-i18next';

const sortBannersByPriority = (a: Banner, b: Banner) => {
  if (a.priority !== undefined && b.priority !== undefined) {
    return b.priority - a.priority;
  }

  return 0;
};

const WebsiteBanners = () => {
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

  if (banners.length <= 0) {
    return <></>;
  }

  return <WebsiteBanner banner={banners[0]} />;
};

export default WebsiteBanners;
