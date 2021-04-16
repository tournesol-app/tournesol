import React from 'react';

import Button from '@material-ui/core/Button';
import VideoCard from './VideoCard';

import { GET_ALL_VIDEOS } from '../api';

export default () => {
  const [videos, setVideos] = React.useState(null);
  const [loaded, setLoaded] = React.useState(false);
  const [page, setPage] = React.useState(1);
  const [totalPages, setTotalPages] = React.useState(0);

  const videosPerPage = 20;

  const setVideoList = (v) => {
    setVideos(v);
    setLoaded(true);

    setTotalPages(Math.ceil(v.length / videosPerPage));
    setPage(1);
  };

  if (videos === null) {
    GET_ALL_VIDEOS((r) => {
      setVideoList(r);
    });
  }

  return (
    <>
      {!loaded && <p>Loading...</p>}
      {loaded && (
        <div>
          <div>
            Total pages: {totalPages}, current page: {page}
            &nbsp;
            <Button
              variant="contained"
              color="primary"
              onClick={() => {
                setPage(Math.max(1, page - 1));
              }}
            >
              &lArr;
            </Button>
            &nbsp;
            <Button
              variant="contained"
              color="primary"
              onClick={() => {
                setPage(Math.min(totalPages, page + 1));
              }}
            >
              &rArr;
            </Button>
          </div>
          <div>
            {videos
              .slice((page - 1) * videosPerPage, page * videosPerPage)
              .map((v) => (
                <VideoCard video={v} showPlayer_={false} showChart_={false} />
              ))}
          </div>
        </div>
      )}
    </>
  );
};
