export const getWikiBaseUrl = () => {
  if (location.hostname === 'localhost') {
    return 'https://wiki.staging.tournesol.app';
  }
  return `https://wiki.${location.host}`;
};
