import React, { useState, useEffect } from 'react';
import { PaginatedVideoList } from 'src/services/openapi';

import { getRecommendedVideos } from './RecommendationApi';
import VideoRecommendationCard from './VideoRecommendationCard';

function VideoRecommendationFromFilters() {
  const prov: PaginatedVideoList = { count: 0, results: [] };
  const [date, setDate] = React.useState('Any');
  const [language, setLanguage] = React.useState('English');
  const [videos, setVideos] = useState(prov);
  const dayInMillisecondes = 1000 * 60 * 60 * 24;
  const conversionTime = new Map();
  conversionTime.set('Any', 1);
  conversionTime.set('Today', dayInMillisecondes);
  conversionTime.set('Week', dayInMillisecondes * 7);
  conversionTime.set('Month', dayInMillisecondes * 7 * 31);
  conversionTime.set('Year', dayInMillisecondes * 365);
  const dateConversion = () => {
    const dateNow = Date.now();
    if (date != 'Any') {
      const limitPublicationDateMilliseconds =
        dateNow - conversionTime.get(date);
      return new Date(limitPublicationDateMilliseconds).toString();
    } else {
      return '';
    }
  };

  useEffect(() => {
    getRecommendedVideos(
      language,
      dateConversion(),
      (videos: PaginatedVideoList) => {
        setVideos(videos);
      }
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [language, date]);

  return (
    <VideoRecommendationCard
      language={language}
      date={date}
      videos={videos}
      onChange={(event) => {
        if (conversionTime.get(event.target.name)) {
          setDate(event.target.name);
        } else {
          setLanguage(event.target.name);
        }
      }}
    />
  );
}

export default VideoRecommendationFromFilters;
