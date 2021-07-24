import React from 'react';
import { useAppSelector } from '../../app/hooks';
import { selectLogin } from './loginSlice';
import { hasValidToken } from './tokenValidity';
import { Route, Redirect } from 'react-router-dom';

export const PrivateRoute = ({ children, ...rest }: any) => {
  const login = useAppSelector(selectLogin);
  return (
    <Route
      {...rest}
      render={({ location }: any) =>
        hasValidToken(login) ? (
          children
        ) : (
          <Redirect
            to={{
              pathname: "/login",
              state: { from: location }
            }}
          />
        )
      }
    />
  );
}
