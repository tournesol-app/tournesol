export const getWikiBaseUrl = () => {
  if (location.hostname === 'localhost') {
    return 'https://wiki.staging.tournesol.app';
  }
  return `https://wiki.${location.host}`;
};

export const twitterTournesolAppUrl = 'https://twitter.com/TournesolApp';
export const twitterTournesolBotEnUrl = 'https://twitter.com/tournesolbot';
export const twitterTournesolBotFrUrl = 'https://twitter.com/tournesolbotfr';

export const discordTournesolInviteUrl =
  'https://discord.com/invite/TvsFB8RNBV';

export const githubTournesolAppUrl =
  'https://github.com/tournesol-app/tournesol';
