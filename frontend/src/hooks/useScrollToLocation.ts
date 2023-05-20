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
        element.scrollIntoView({ behavior: 'smooth' });
        scrolledRef.current = true;
      }
    }
  }, []);
};
