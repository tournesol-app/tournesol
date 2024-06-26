import React from 'react';
import { Redirect, useLocation } from 'react-router-dom';

const RecommendationsPageRedirect = () => {
  const location = useLocation();
  return <Redirect to={`/search${location.search}`} />;
};

export default RecommendationsPageRedirect;
