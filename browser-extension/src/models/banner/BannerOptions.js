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

// TODO: these values are placeholder values that should be updated.
export const defaultBannerOptions = new BannerOptions(
  '2023-04-01T00:00:00Z',
  '2023-05-20T00:00:00Z',
  'https://docs.google.com/forms/d/e/1FAIpQLSd4_8nF0kVnHj3GvTlEAFw-PHAGOAGc1j1NKZbXr8Ga_nIY9w/viewform?usp=pp_url&entry.939413650=',
  'https://docs.google.com/forms/d/e/1FAIpQLSfEXZLlkLA6ngx8LV-VVpIxV9AZ9MgN-H_U0aTOnVhrXv1XLQ/viewform?usp=pp_url&entry.1924714025=',
  'browser_extension_study_2023'
);
