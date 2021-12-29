import React from 'react';
import { Redirect } from 'react-router-dom';

import { useAppSelector } from 'src/app/hooks';
import { selectLogin } from './loginSlice';
import { isLoggedIn } from './loginUtils';
import RedirectState from './RedirectState';
import PublicRoute from './PublicRoute';

interface Props {
  children?: React.ReactNode;
  [propName: string]: unknown;
}

const PrivateRoute = ({ children, ...rest }: Props) => {
  const login = useAppSelector(selectLogin);
  return (
    <PublicRoute
      {...rest}
      render={({ location }: { location: string }) =>
        isLoggedIn(login) ? (
          children
        ) : (
          <Redirect
            to={{
              pathname: '/login',
              state: { from: location } as RedirectState,
            }}
          />
        )
      }
    />
  );
};

export default PrivateRoute;
