import React from 'react';

import type { PaginatedVideoList } from 'src/services/openapi';
import VideoList from '../videos/VideoList';
import SearchFilter from './Searchfilter';

function VideoRecommendationCard(props: {
  date: string;
  language: string;
  videos: PaginatedVideoList;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <div className="main">
      <SearchFilter
        language={props.language}
        date={props.date}
        onChange={props.onChange}
      />
      <VideoList videos={props.videos} />
    </div>
  );
}

export default VideoRecommendationCard;
