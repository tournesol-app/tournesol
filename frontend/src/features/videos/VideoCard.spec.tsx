import React from 'react';
import { MemoryRouter as Router } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';

import { theme } from 'src/theme';
import VideoCard from './VideoCard';
import { Recommendation, TypeEnum } from 'src/services/openapi';

const renderVideoCard = (video: Recommendation) =>
  render(
    <Router>
      <ThemeProvider theme={theme}>
        <VideoCard video={video} />
      </ThemeProvider>
    </Router>
  );

describe('VideoCard content', () => {
  it('shows video metadata without criterias', () => {
    const video: Recommendation = {
      entity: {
        uid: 'yt:xSqqXN0D4fY',
        type: TypeEnum.VIDEO,
        metadata: {
          name: 'Video title',
          description: 'Video description',
          views: 154988,
          uploader: 'Channel name',
          duration: 120,
          publication_date: '2021-03-21',
          language: 'fr',
          video_id: 'xSqqXN0D4fY',
        },
      },
      collective_rating: {
        n_contributors: 4,
        n_comparisons: 9,
        tournesol_score: 0.0,
        criteria_scores: [],
        unsafe: {
          status: false,
          reasons: [],
        },
      },
      entity_contexts: [],
      recommendation_metadata: {
        total_score: 0.0,
      },
    };
    renderVideoCard(video);

    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      'Video title'
    );
    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      '155K views'
    );
    expect(screen.getByTestId('video-card-ratings')).toHaveTextContent(
      '9 comparisons by 4 contributors'
    );
    expect(
      screen.queryByTestId('video-card-overall-score')
    ).toBeInTheDocument();
  });

  it('shows video card with single criteria', () => {
    const video: Recommendation = {
      entity: {
        uid: 'yt:xSqqXN0D4fY',
        type: TypeEnum.VIDEO,
        metadata: {
          name: 'Video title',
          description: 'Video description',
          views: 154988,
          uploader: 'Channel name',
          duration: 4200,
          video_id: 'xSqqXN0D4fY',
          publication_date: '2021-03-21',
          language: 'fr',
        },
      },
      collective_rating: {
        n_contributors: 4,
        n_comparisons: 9,
        tournesol_score: 4,
        criteria_scores: [
          {
            criteria: 'largely_recommended',
            score: 0.4,
          },
        ],
        unsafe: {
          status: false,
          reasons: [],
        },
      },
      entity_contexts: [],
      recommendation_metadata: {
        total_score: 4,
      },
    };
    renderVideoCard(video);

    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      'Video title'
    );
    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      '155K views'
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
    const video: Recommendation = {
      entity: {
        uid: 'yt:xSqqXN0D4fY',
        type: TypeEnum.VIDEO,
        metadata: {
          name: 'Video title',
          description: 'Video description',
          views: 154988,
          uploader: 'Channel name',
          duration: 120,
          video_id: 'xSqqXN0D4fY',
          publication_date: '2021-03-21',
          language: 'fr',
        },
      },
      collective_rating: {
        n_contributors: 4,
        n_comparisons: 9,
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
        unsafe: {
          status: false,
          reasons: [],
        },
      },
      entity_contexts: [],
      recommendation_metadata: {
        total_score: 17,
      },
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
    const video: Recommendation = {
      entity: {
        uid: 'yt:xSqqXN0D4fY',
        type: TypeEnum.VIDEO,
        metadata: {
          name: 'Video title',
          description: 'Video description',
          views: 154988,
          uploader: 'Channel name',
          duration: 120,
          publication_date: '2021-03-21',
          language: 'fr',
          video_id: 'xSqqXN0D4fY',
        },
      },
      collective_rating: {
        n_contributors: 4,
        n_comparisons: 9,
        tournesol_score: null,
        criteria_scores: [],
        unsafe: {
          status: false,
          reasons: [],
        },
      },
      entity_contexts: [],
      recommendation_metadata: {
        total_score: 0,
      },
    };
    renderVideoCard(video);

    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      'Video title'
    );
    expect(screen.getByTestId('video-card-info')).toHaveTextContent(
      '155K views'
    );
    expect(screen.getByTestId('video-card-ratings')).toHaveTextContent(
      '9 comparisons by 4 contributors'
    );
    expect(
      screen.queryByTestId('video-card-overall-score')
    ).not.toBeInTheDocument();
  });
});
