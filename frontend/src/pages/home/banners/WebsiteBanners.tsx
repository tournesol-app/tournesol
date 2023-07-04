import React, { useEffect, useState } from 'react';

import { useNotifications } from 'src/hooks';

import { BackofficeService, Banner } from 'src/services/openapi';
import WebsiteBannerSingle from './WebsiteBannerSingle';

const WebsiteBanners = () => {
  const { contactAdministrator } = useNotifications();

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
      <WebsiteBannerSingle banners={banners} />
    </>
  );
};

export default WebsiteBanners;
