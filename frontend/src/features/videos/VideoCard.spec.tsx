import React from 'react';
import { render, screen } from '@testing-library/react';

import { Video } from 'src/services/openapi';
import VideoCard from './VideoCard';

describe('VideoCard content', () => {
  it('shows video metadata without criterias', () => {
    const video: Video = {
      video_id: 'xSqqXN0D4fY',
      name: 'Video title',
      description: 'Video description',
      views: 154988,
      upload: 'Channel name',
      rating_n_contributors: 4,
      rating_n_ratings: 9,
    };
    render(<VideoCard video={video} />);

    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      'Video title'
    );
    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      '154988 views'
    );
    expect(screen.getByTestId('video-card-ratings')).toHaveTextContent(
      '9 comparisons by 4 contributors'
    );
    expect(
      screen.queryByTestId('video-card-overall-score')
    ).not.toBeInTheDocument();
  });

  it('shows video card with single criteria', () => {
    const video: Video = {
      video_id: 'xSqqXN0D4fY',
      name: 'Video title',
      description: 'Video description',
      views: 154988,
      upload: 'Channel name',
      rating_n_contributors: 4,
      rating_n_ratings: 9,
      criteria_scores: [
        {
          criteria: 'largely_recommended',
          score: 0.4,
          uncertainty: 0.0,
          quantile: 1.0,
        },
      ],
    };
    render(<VideoCard video={video} />);

    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      'Video title'
    );
    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      '154988 views'
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
    const video: Video = {
      video_id: 'xSqqXN0D4fY',
      name: 'Video title',
      description: 'Video description',
      views: 154988,
      upload: 'Channel name',
      rating_n_contributors: 4,
      rating_n_ratings: 9,
      criteria_scores: [
        {
          criteria: 'engaging',
          score: 0.9,
          uncertainty: 0.0,
          quantile: 1.0,
        },
        {
          criteria: 'pedagogy',
          score: 0.8,
          uncertainty: 0.0,
          quantile: 1.0,
        },
      ],
    };
    render(<VideoCard video={video} />);

    expect(screen.queryByTestId('video-card-overall-score')).toHaveTextContent(
      '17'
    );
    expect(screen.getByTestId('video-card-ratings')).toHaveTextContent(
      '9 comparisons by 4 contributors'
    );
    expect(screen.queryByTestId('video-card-minmax-criterias')).toBeVisible();
  });
});
