import { useState, useEffect } from 'react';
import { idFromUid } from '../utils/video';

const useIsAvailable = (uid: string) => {
  const [entityIsChecking, setEntityIsChecking] = useState(true);
  const [entityIsAvailable, setEntityIsAvailable] = useState(false);

  useEffect(() => {
    if (uid.indexOf('yt:') === -1) {
      setEntityIsChecking(false);
      setEntityIsAvailable(true);
    } else {
      const img = new Image();
      img.src = `https://i.ytimg.com/vi/${idFromUid(uid)}/mqdefault.jpg`;
      img.onload = function () {
        setEntityIsAvailable(img.width !== 120);
        setEntityIsChecking(false);
      };
    }
  }, [uid]);

  return { entityIsChecking, entityIsAvailable };
};

export default useIsAvailable;
