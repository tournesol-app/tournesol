import { useState, useEffect } from 'react';
import { useLocation, Location } from 'react-router';

const buildSearchParams = (location: Location) =>
  Object.fromEntries(new URLSearchParams(location.search));

export const useSearchParams = () => {
  const location = useLocation();
  const [searchParamsObject, setSearchParams] = useState(
    buildSearchParams(location)
  );

  useEffect(() => {
    setSearchParams(buildSearchParams(location));
  }, [location]);

  return searchParamsObject;
};
