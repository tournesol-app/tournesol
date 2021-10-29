import { useLocation } from 'react-router';

export const useSearchParams = () => {
  const location = useLocation();
  return Object.fromEntries(new URLSearchParams(location.search));
};
