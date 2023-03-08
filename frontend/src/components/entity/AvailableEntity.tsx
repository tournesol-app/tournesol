import React from 'react';

import LoaderWrapper from 'src/components/LoaderWrapper';
import useIsAvailable from 'src/hooks/useIsAvailable';
import { ActionList } from 'src/utils/types';

/**
 * Return an <EntityCard> with isAvailable=false if the entity doesn't seem to
 * be available online at its original location, return the given children
 * components as-is instead.
 */
const AvailableEntity = ({
  uid,
  children,
  actionsIfUnavailable,
}: {
  uid: string;
  children: React.ReactElement;
  actionsIfUnavailable?: ActionList;
}) => {
  const { entityIsChecking, entityIsAvailable } = useIsAvailable(uid);

  return (
    <LoaderWrapper isLoading={entityIsChecking}>
      {entityIsAvailable ? (
        <>{children}</>
      ) : (
        <>
          {React.cloneElement(children, {
            isAvailable: entityIsAvailable,
            actions: actionsIfUnavailable,
          })}
        </>
      )}
    </LoaderWrapper>
  );
};

export default AvailableEntity;
