import Plausible, { EventOptions, PlausibleOptions } from 'plausible-tracker';

/**
 * A map of all custom events tracked by the web analytics server.
 *
 * The values represent the events' names as they are configured in the web
 * analytics server's settings.
 */
export const TRACKED_EVENTS = {
  signup: 'signup',
  tutorial: 'tutorial',
  tutorialSkipped: 'tutorial skipped',
  accountDeleted: 'account deleted',
};

const doNotTrack = new URLSearchParams(location.search).get('dnt') === '1';
const analyticsClient =
  import.meta.env.REACT_APP_WEBSITE_ANALYTICS_URL && !doNotTrack
    ? Plausible({ apiHost: import.meta.env.REACT_APP_WEBSITE_ANALYTICS_URL })
    : null;

if (analyticsClient) {
  analyticsClient.enableAutoPageviews();
}

export const trackEvent = (
  eventName: string,
  options?: EventOptions,
  eventData?: PlausibleOptions
) => {
  // Do nothing when no tracking API has been configured.
  if (analyticsClient) {
    analyticsClient.trackEvent(eventName, options, eventData);
  }
};
