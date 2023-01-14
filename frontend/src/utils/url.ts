export const getWikiBaseUrl = () => {
  if (location.hostname === 'localhost') {
    return 'https://wiki.staging.tournesol.app';
  }
  return `https://wiki.${location.host}`;
};

/**
 * Mailing list
 */
export const tournesolTalksMailingListUrl =
  'https://framalistes.org/sympa/subscribe/tournesoltalks';

/**
 * Social links
 */

// Discord
export const discordTournesolInviteUrl =
  'https://discord.com/invite/TvsFB8RNBV';

// Twitter
export const twitterTournesolUrl = 'https://twitter.com/TournesolApp';
export const twitterTournesolBotEnUrl = 'https://twitter.com/tournesolbot';
export const twitterTournesolBotFrUrl = 'https://twitter.com/tournesolbotfr';

// Twitch
export const twitchTournesolUrl = 'https://twitch.tv/tournesolapp';

// GitHub
export const githubTournesolUrl = 'https://github.com/tournesol-app/tournesol';

// LinkedIn
export const linkedInTournesolUrl =
  'https://www.linkedin.com/company/tournesol-app';

// YouTube
export const youtubePlaylistEnUrl =
  'https://youtube.com/playlist?list=PLXX93NlSmUpayYeaNvKaeftX_QwEei3fU';
export const youtubePlaylistBotFrUrl =
  'https://youtube.com/playlist?list=PLXX93NlSmUpZkR9NaBXMaPlPalESb5tDv';

/**
 * Support
 */

// PayPal
export const paypalTournesolUrl =
  'https://www.paypal.com/paypalme/tournesolapp';

// uTip
export const utipTournesolUrl = 'https://utip.io/tournesol';

/**
 * Research
 */

// Papers
export const whitePaperUrl = 'https://arxiv.org/abs/2107.07334';
