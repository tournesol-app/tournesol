import React from 'react';
import { MemoryRouter as Router } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';

import { LanguageEnum } from 'src/services/openapi';
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
      video_id: 'xSqqXN0D4fY',
      name: 'Video title',
      description: 'Video description',
      views: 154988,
      uploader: 'Channel name',
      rating_n_contributors: 4,
      rating_n_ratings: 9,
      duration: 120,
      publication_date: '',
      language: LanguageEnum.FR,
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

  it('shows video card with single criteria', () => {
    const video: VideoObject = {
      video_id: 'xSqqXN0D4fY',
      name: 'Video title',
      description: 'Video description',
      views: 154988,
      uploader: 'Channel name',
      rating_n_contributors: 4,
      rating_n_ratings: 9,
      criteria_scores: [
        {
          criteria: 'largely_recommended',
          score: 0.4,
        },
      ],
      duration: 4200,
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
      video_id: 'xSqqXN0D4fY',
      name: 'Video title',
      description: 'Video description',
      views: 154988,
      uploader: 'Channel name',
      rating_n_contributors: 4,
      rating_n_ratings: 9,
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
});
