import { useCallback, useState } from 'react';

import Plausible, { EventOptions, PlausibleOptions } from 'plausible-tracker';

/**
 * A hook that returns a web analytics client, and several tracking functions.
 *
 * We currently use plausible-tracker, a Plausible Analytics client.
 *
 * See: https://github.com/plausible/plausible-tracker
 */
export const useWebAnalytics = () => {
  const [client] = useState(
    process.env.REACT_APP_WEBSITE_ANALYTICS_URL
      ? Plausible({ apiHost: process.env.REACT_APP_WEBSITE_ANALYTICS_URL })
      : null
  );

  // Do nothing not tracking API has been configured.
  const enableAutoPageviews = useCallback(() => {
    if (client) {
      return client.enableAutoPageviews();
    }
  }, [client]);

  // Do nothing not tracking API has been configured.
  const trackEvent = useCallback(
    (
      eventName: string,
      options?: EventOptions,
      eventData?: PlausibleOptions
    ) => {
      if (client) {
        client.trackEvent(eventName, options, eventData);
      }
    },
    [client]
  );

  return {
    client: client,
    enableAutoPageviews: enableAutoPageviews,
    trackEvent: trackEvent,
  };
};
