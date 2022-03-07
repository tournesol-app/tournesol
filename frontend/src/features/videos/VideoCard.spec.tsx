import React from 'react';
import { MemoryRouter as Router } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';

import { VideoObject } from 'src/utils/types';
import { theme } from 'src/theme';
import VideoCard from './VideoCard';

const renderVideoCard = (video: VideoObject) =>
  render(
    <Router>
      <ThemeProvider theme={theme}>
        <VideoCard video={video} />
      </ThemeProvider>
    </Router>
  );

describe('VideoCard content', () => {
  it('shows video metadata without criterias', () => {
    const video: VideoObject = {
      uid: 'yt:xSqqXN0D4fY',
      name: 'Video title',
      description: 'Video description',
      views: 154988,
      uploader: 'Channel name',
      rating_n_contributors: 4,
      rating_n_ratings: 9,
      tournesol_score: 0.0,
      duration: 120,
      publication_date: '2021-03-21',
      language: 'fr',
      video_id: 'xSqqXN0D4fY',
    };
    renderVideoCard(video);

    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      'Video title'
    );
    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      '154,988 views'
    );
    expect(screen.getByTestId('video-card-ratings')).toHaveTextContent(
      '9 comparisons by 4 contributors'
    );
    expect(
      screen.queryByTestId('video-card-overall-score')
    ).toBeInTheDocument();
  });

  it('shows video card with single criteria', () => {
    const video: VideoObject = {
      uid: 'yt:xSqqXN0D4fY',
      name: 'Video title',
      description: 'Video description',
      views: 154988,
      uploader: 'Channel name',
      rating_n_contributors: 4,
      rating_n_ratings: 9,
      tournesol_score: 4,
      criteria_scores: [
        {
          criteria: 'largely_recommended',
          score: 0.4,
        },
      ],
      duration: 4200,
      video_id: 'xSqqXN0D4fY',
      publication_date: '2021-03-21',
      language: 'fr',
    };
    renderVideoCard(video);

    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      'Video title'
    );
    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      '154,988 views'
    );
    expect(screen.getByTestId('video-card-ratings')).toHaveTextContent(
      '9 comparisons by 4 contributors'
    );
    expect(screen.queryByTestId('video-card-overall-score')).toHaveTextContent(
      '4'
    );
    expect(
      screen.queryByTestId('video-card-minmax-criterias')
    ).not.toBeInTheDocument();
  });

  it('shows video card with multiple criteria', () => {
    const video: VideoObject = {
      uid: 'yt:xSqqXN0D4fY',
      name: 'Video title',
      description: 'Video description',
      views: 154988,
      uploader: 'Channel name',
      rating_n_contributors: 4,
      rating_n_ratings: 9,
      tournesol_score: 17,
      criteria_scores: [
        {
          criteria: 'engaging',
          score: 0.9,
        },
        {
          criteria: 'pedagogy',
          score: 0.8,
        },
      ],
      duration: 120,
      video_id: 'xSqqXN0D4fY',
      publication_date: '2021-03-21',
      language: 'fr',
    };
    renderVideoCard(video);

    expect(screen.queryByTestId('video-card-overall-score')).toHaveTextContent(
      '17'
    );
    expect(screen.getByTestId('video-card-ratings')).toHaveTextContent(
      '9 comparisons by 4 contributors'
    );
    expect(screen.queryByTestId('video-card-minmax-criterias')).toBeVisible();
  });

  it('shows video metadata with null Tournesol score', () => {
    const video: VideoObject = {
      uid: 'yt:xSqqXN0D4fY',
      name: 'Video title',
      description: 'Video description',
      views: 154988,
      uploader: 'Channel name',
      rating_n_contributors: 4,
      rating_n_ratings: 9,
      tournesol_score: null,
      duration: 120,
      publication_date: '2021-03-21',
      language: 'fr',
      video_id: 'xSqqXN0D4fY',
    };
    renderVideoCard(video);

    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      'Video title'
    );
    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      '154,988 views'
    );
    expect(screen.getByTestId('video-card-ratings')).toHaveTextContent(
      '9 comparisons by 4 contributors'
    );
    expect(
      screen.queryByTestId('video-card-overall-score')
    ).not.toBeInTheDocument();
  });

  it('shows video metadata without Tournesol score', () => {
    const video: VideoObject = {
      uid: 'yt:xSqqXN0D4fY',
      name: 'Video title',
      description: 'Video description',
      views: 154988,
      uploader: 'Channel name',
      rating_n_contributors: 4,
      rating_n_ratings: 9,
      duration: 120,
      publication_date: '2021-03-21',
      language: 'fr',
      video_id: 'xSqqXN0D4fY',
    };
    renderVideoCard(video);

    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      'Video title'
    );
    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      '154,988 views'
    );
    expect(screen.getByTestId('video-card-ratings')).toHaveTextContent(
      '9 comparisons by 4 contributors'
    );
    expect(
      screen.queryByTestId('video-card-overall-score')
    ).not.toBeInTheDocument();
  });
});
