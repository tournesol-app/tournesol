import React from 'react';

import LoaderWrapper from 'src/components/LoaderWrapper';
import { useEntityAvailable } from 'src/hooks';
import { ENTITY_AVAILABILITY } from 'src/hooks/useEntityAvailable';
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
  const { availability } = useEntityAvailable(uid);

  return (
    <LoaderWrapper isLoading={availability === ENTITY_AVAILABILITY.UNKNOWN}>
      {availability === ENTITY_AVAILABILITY.AVAILABLE ? (
        <>{children}</>
      ) : (
        <>
          {React.cloneElement(children, {
            isAvailable: false,
            actions: actionsIfUnavailable,
          })}
        </>
      )}
    </LoaderWrapper>
  );
};

export default AvailableEntity;
