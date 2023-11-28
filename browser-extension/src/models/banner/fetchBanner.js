import { Banner } from './Banner.js';

const fetchBanners = async () =>
  new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ message: 'getBanners' }, (result) => {
      if (result === undefined) {
        reject(new Error(chrome.runtime.lastError));
        return;
      }
      const { banners } = result;
      if (banners) resolve(banners.results);
      else reject(new Error('Invalid API response'));
    });
  });

const sortBanners = (a, b) => {
  // This function also exists in frontend/src/features/banners/WebsiteBanners.tsx
  if (a.security_advisory && !b.security_advisory) {
    return -1;
  }
  if (!a.security_advisory && b.security_advisory) {
    return 1;
  }
  if (a.priority !== undefined && b.priority !== undefined) {
    return b.priority - a.priority;
  }

  return 0;
};

export const fetchBanner = async () => {
  try {
    const banners = await fetchBanners();
    if (banners.length === 0) return;

    banners.sort(sortBanners);
    const banner = banners[0];

    return new Banner({
      name: banner.name,
      dateStart: new Date(banner.date_start),
      dateEnd: new Date(banner.date_end),
      title: banner.title,
      text: banner.text,
      actionLabel: banner.action_label,
      actionLink: banner.action_link,
      securityAdvisory: banner.security_advisory,
    });
  } catch (e) {
    console.warn('Error while fetching Tournesol banners', e);
  }
};
