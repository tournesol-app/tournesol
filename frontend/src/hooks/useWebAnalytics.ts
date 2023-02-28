import { useState } from 'react';

import Plausible from 'plausible-tracker';

/**
 * A hook that returns a web analytics client.
 *
 * We currently use plausible-tracker, a Plausible Analytics client.
 *
 * See: https://github.com/plausible/plausible-tracker
 */
export const useWebAnalytics = () => {
  const [client] = useState(
    Plausible({ apiHost: process.env.REACT_APP_WEBSITE_ANALYTICS_URL })
  );

  return {
    client: client,
    enableAutoPageviews: client.enableAutoPageviews,
    trackEvent: client.trackEvent,
  };
};
