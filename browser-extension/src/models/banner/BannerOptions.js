export class BannerOptions {
  constructor(
    TS_BANNER_DATE_START,
    TS_BANNER_DATE_END,
    TS_BANNER_ACTION_FR_URL,
    TS_BANNER_ACTION_EN_URL,
    TS_BANNER_PROOF_KW
  ) {
    this.TS_BANNER_DATE_START = new Date(TS_BANNER_DATE_START);
    this.TS_BANNER_DATE_END = new Date(TS_BANNER_DATE_END);
    this.TS_BANNER_ACTION_FR_URL = TS_BANNER_ACTION_FR_URL;
    this.TS_BANNER_ACTION_EN_URL = TS_BANNER_ACTION_EN_URL;
    this.TS_BANNER_PROOF_KW = TS_BANNER_PROOF_KW;
  }
}

export const defaultBannerOptions = new BannerOptions(
  '2023-09-07T00:00:00Z',
  '2023-10-01T00:00:00Z',
  'https://tournesol.app/about/donate?utm_source=extension',
  'https://tournesol.app/about/donate?utm_source=extension',
  '2023_2024_funding_campaing'
);
