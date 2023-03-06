import React, { useState, useEffect } from 'react';

import LoaderWrapper from 'src/components/LoaderWrapper';
import { TypeEnum } from 'src/services/openapi';
import { ActionList } from 'src/utils/types';
import { idFromUid } from 'src/utils/video';

/**
 * Return an <EntityCard> with isAvailable=false if the entity doesn't seem to
 * be available online at its original location, return the given children
 * components as-is instead.
 */
const AvailableEntity = ({
  uid,
  type,
  children,
  actionsIfUnavailable,
}: {
  uid: string;
  type: string;
  children: React.ReactElement;
  actionsIfUnavailable?: ActionList;
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAvailable, setIsAvailable] = useState(false);

  /**
   * Check if the entity is available.
   *
   * The behaviour "is available" could be factorized in a custom hook.
   */
  useEffect(() => {
    if (type !== TypeEnum.VIDEO) {
      setIsLoading(false);
      setIsAvailable(true);
    } else {
      const img = new Image();
      img.src = `https://i.ytimg.com/vi/${idFromUid(uid)}/mqdefault.jpg`;
      img.onload = function () {
        setIsLoading(false);
        setIsAvailable(img.width !== 120);
      };
    }
  }, [uid, type]);

  return (
    <LoaderWrapper isLoading={isLoading}>
      {isAvailable ? (
        <>{children}</>
      ) : (
        <>
          {React.cloneElement(children, {
            isAvailable: isAvailable,
            actions: actionsIfUnavailable,
          })}
        </>
      )}
    </LoaderWrapper>
  );
};

export default AvailableEntity;
