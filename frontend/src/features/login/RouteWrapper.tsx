import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

import { useAppSelector } from 'src/app/hooks';
import { isLoggedIn, selectLogin } from 'src/features/login';

/**
 * A wrapper around the element rendered by the React Router <Route> component.
 *
 * Should be used to trigger code when the route changes.
 */
const RouteWrapper = ({
  children,
  auth = false,
}: {
  children: React.ReactNode;
  auth?: boolean;
}) => {
  const login = useAppSelector(selectLogin);
  const location = useLocation();

  if (auth && !isLoggedIn(login)) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default RouteWrapper;
