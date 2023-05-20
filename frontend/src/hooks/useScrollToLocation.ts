import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

export const useScrollToLocation = () => {
  const scrolledRef = useRef(false);
  const { hash } = useLocation();

  useEffect(() => {
    if (hash && !scrolledRef.current) {
      const id = hash.replace('#', '');
      const element = document.getElementById(id);

      if (element) {
        // Give more time to the React tree to be rendered, to increase the
        // chance of scrolling all the way down to the target.
        // Insecure Bayesian Web Development.
        setTimeout(() => {
          element.scrollIntoView({ behavior: 'smooth' });
          scrolledRef.current = true;
        }, 600);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
};
