import { useState, useEffect } from 'react';

import {
  VideoService,
  VideoSerializerWithCriteria as Video,
} from 'src/services/openapi';

const _inMemoryCache: { [videoId: string]: Promise<Video> } = {};

export const useVideoMetadata = (videoId: string) => {
  const [video, setVideo] = useState({ video_id: '' } as Video);
  useEffect(() => {
    // Fetches the video metadata if they have not been fetched or `videoId` has changed
    const process = async () => setVideo(await getVideoInformation(videoId));
    if (video.video_id != videoId) process();
  }, [video.video_id, videoId]); // Only re-runs if `videoId` changes
  return video;
};

export const getVideoInformation = async (videoId: string): Promise<Video> => {
  // TODO: replace this custom method with the automatically generated `VideoService.videoRetrieve``
  // VideoService.videoRetrieve is currently not used because the URL is incorrect
  if (_inMemoryCache[videoId] == undefined) {
    const promise = VideoService.videoRetrieve({ videoId }).catch((err) => {
      console.log(err);
      const defaultVideo: Video = {
        name: 'Missing Information',
        uid: '',
        publication_date: '',
        uploader: '',
        views: 0,
        video_id: videoId,
        description: '',
        language: null,
        tournesol_score: null,
        rating_n_ratings: 0,
        rating_n_contributors: 0,
        criteria_scores: [],
        duration: null,
      };
      return defaultVideo;
    });
    _inMemoryCache[videoId] = promise;
  }
  return _inMemoryCache[videoId];
};
