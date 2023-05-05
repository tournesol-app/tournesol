import { useState, useEffect } from 'react';
import { UID_YT_NAMESPACE } from 'src/utils/constants';
import { idFromUid } from 'src/utils/video';

export enum ENTITY_AVAILABILITY {
  UNKNOWN = 'unknown',
  AVAILABLE = 'available',
  UNAVAILABLE = 'unavailable',
}

export const useEntityAvailable = (uid: string) => {
  const [availability, setAvailability] = useState<ENTITY_AVAILABILITY>(
    ENTITY_AVAILABILITY.UNKNOWN
  );

  useEffect(() => {
    if (uid.startsWith(UID_YT_NAMESPACE)) {
      const img = new Image();
      img.src = `https://i.ytimg.com/vi/${idFromUid(uid)}/mqdefault.jpg`;
      img.onload = function () {
        if (img.width !== 120) {
          setAvailability(ENTITY_AVAILABILITY.AVAILABLE);
        } else {
          setAvailability(ENTITY_AVAILABILITY.UNAVAILABLE);
        }
      };
    } else {
      setAvailability(ENTITY_AVAILABILITY.AVAILABLE);
    }
  }, [uid]);

  return { availability };
};
