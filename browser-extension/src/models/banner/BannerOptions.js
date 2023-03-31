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
  '2020-01-01T00:00:00Z',
  '2024-01-01T00:00:00Z',
  'https://docs.google.com/forms/d/e/1FAIpQLScQzlEKBSA3MqxI0kaPazbyIUnZ4PjFcrR8EFiikG1quyAoiw/viewform?usp=pp_url&entry.939413650=',
  'https://docs.google.com/forms/d/e/1FAIpQLSf9PXr-f8o9QqDR-Pi63xRZx4y4nOumNDdwi_jvUWc6LxZRAw/viewform?usp=pp_url&entry.1924714025=',
  'browser_extension_study_2023'
);
