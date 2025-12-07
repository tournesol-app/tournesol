import { useEffect } from 'react';

export const useScrollToLocation = () => {
  useEffect(() => {
    const scrollToHash = () => {
      const hash = window.location.hash;
      if (hash) {
        const id = hash.replace('#', '');
        const element = document.getElementById(id);

        if (element) {
          // Give more time to the React tree to be rendered, to increase the
          // chance of scrolling all the way down to the target.
          // Insecure Bayesian Web Development.
          setTimeout(() => {
            element.scrollIntoView({ behavior: 'smooth' });
          }, 600);
        }
      }
    };

    scrollToHash();
    window.addEventListener('hashchange', scrollToHash);
    return () => {
      window.removeEventListener('hashchange', scrollToHash);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
};
