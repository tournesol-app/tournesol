import React from 'react';
import { useRefreshToken } from 'src/hooks/useRefreshToken';

/**
 * A wrapper around the element rendered by the React Router <Route> component.
 *
 * Should be used to trigger code when the route changes.
 */
const RouteWrapper = ({ children }: { children: React.ReactNode }) => {
  useRefreshToken();
  return <>{children}</>;
};

export default RouteWrapper;
