import { useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';

export const useRestorePreviousTitle = () => {
  const history = useHistory();
  const [previousTitle] = useState(document.title);

  useEffect(() => {
    return () => {
      if (history.action === 'POP') {
        document.title = previousTitle;
      } else {
        document.title = 'Tournesol';
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
};
