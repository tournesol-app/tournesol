import React from 'react';
import { createMemoryHistory } from 'history';
import { Router } from 'react-router-dom';
import { render } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import { ThemeProvider } from '@mui/material/styles';
import { theme } from 'src/theme';
import {
  saveRecommendationsLanguages,
  loadRecommendationsLanguages,
} from 'src/utils/recommendationsLanguages';
import * as RecommendationApi from 'src/features/recommendation/RecommendationApi';

import VideoRecommendationPage from './VideoRecommendation';

const VideoList = () => null;
jest.mock('src/features/videos/VideoList', () => VideoList);

describe('VideoRecommendationPage', () => {
  let history: ReturnType<typeof createMemoryHistory>;
  let pushSpy: ReturnType<typeof jest.spyOn>;
  let navigatorLanguagesGetter: ReturnType<typeof jest.spyOn>;
  let getRecommendedVideosSpy: ReturnType<typeof jest.spyOn>;
  beforeEach(() => {
    history = createMemoryHistory();
    pushSpy = jest.spyOn(history, 'push');
    navigatorLanguagesGetter = jest.spyOn(window.navigator, 'languages', 'get');
    getRecommendedVideosSpy = jest
      .spyOn(RecommendationApi, 'getRecommendedVideos')
      .mockImplementation(async () => ({ count: 0, results: [] }));
  });
  const component = () => {
    render(
      <Router history={history}>
        <ThemeProvider theme={theme}>
          <VideoRecommendationPage />
        </ThemeProvider>
      </Router>
    );
  };

  it('adds the navigator languages to the query string and stores them', async () => {
    navigatorLanguagesGetter.mockReturnValue(['fr', 'en-US']);
    await act(async () => component());

    expect(pushSpy).toHaveBeenLastCalledWith({
      search: 'language=fr%2Cen',
    });
    expect(loadRecommendationsLanguages()).toEqual('fr,en');
    expect(getRecommendedVideosSpy).toHaveBeenCalledTimes(1);
    expect(getRecommendedVideosSpy).toHaveBeenLastCalledWith(
      '?language=fr%2Cen',
      expect.anything()
    );
  });

  it('adds the stored languages to the query string', async () => {
    navigatorLanguagesGetter.mockReturnValue(['fr', 'en-US']);
    saveRecommendationsLanguages('de');
    await act(async () => component());

    expect(pushSpy).toHaveBeenLastCalledWith({
      search: 'language=de',
    });
    expect(loadRecommendationsLanguages()).toEqual('de');
    expect(getRecommendedVideosSpy).toHaveBeenCalledTimes(1);
    expect(getRecommendedVideosSpy).toHaveBeenLastCalledWith(
      '?language=de',
      expect.anything()
    );
  });

  it("doesn't change the languages already in the query string", async () => {
    navigatorLanguagesGetter.mockReturnValue(['fr', 'en-US']);
    saveRecommendationsLanguages('de');
    history.push({ search: 'language=fr' });
    (history.push as jest.Mock).mockClear();
    await act(async () => component());

    expect(pushSpy).not.toHaveBeenCalled();
    expect(loadRecommendationsLanguages()).toEqual('de');
    expect(getRecommendedVideosSpy).toHaveBeenCalledTimes(1);
    expect(getRecommendedVideosSpy).toHaveBeenLastCalledWith(
      '?language=fr',
      expect.anything()
    );
  });
});
