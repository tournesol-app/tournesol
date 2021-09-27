export const handleWikiUrl = (host: string) => {
  if (host == 'localhost:3000') {
    return 'https://wiki.staging.tournesol.app';
  }
  return `https://wiki.${host}`;
};
