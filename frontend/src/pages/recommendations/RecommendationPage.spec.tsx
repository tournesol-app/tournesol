/*
  Because of a regression in CRA v5, Typescript is wrongly enforced here
  See https://github.com/facebook/create-react-app/pull/11875
*/
// eslint-disable-next-line
// @ts-nocheck
import React from 'react';

import { createMemoryHistory } from 'history';
import { act } from 'react-dom/test-utils';
import { Router } from 'react-router-dom';

import { ThemeProvider } from '@mui/material/styles';
import { render } from '@testing-library/react';

import { PollProvider } from 'src/hooks/useCurrentPoll';
import RecommendationPage from 'src/pages/recommendations/RecommendationPage';
import { PollsService } from 'src/services/openapi';
import { theme } from 'src/theme';
import * as RecommendationApi from 'src/utils/api/recommendations';
import {
  saveRecommendationsLanguages,
  loadRecommendationsLanguages,
} from 'src/utils/recommendationsLanguages';

const EntityList = () => null;
jest.mock('src/features/entities/EntityList', () => EntityList);

const SearchFilter = () => null;
jest.mock('src/features/recommendation/SearchFilter', () => SearchFilter);

describe('RecommendationPage', () => {
  let history: ReturnType<typeof createMemoryHistory>;
  let historySpy: ReturnType<typeof jest.spyOn>;
  let navigatorLanguagesGetter: ReturnType<typeof jest.spyOn>;
  let getRecommendedVideosSpy: ReturnType<typeof jest.spyOn>;

  beforeEach(() => {
    history = createMemoryHistory();
    historySpy = jest.spyOn(history, 'replace');
    navigatorLanguagesGetter = jest.spyOn(window.navigator, 'languages', 'get');
    getRecommendedVideosSpy = jest
      .spyOn(RecommendationApi, 'getRecommendations')
      .mockImplementation(async () => ({ count: 0, results: [] }));

    // prevent the useCurrentPoll hook to make HTTP requests
    jest.spyOn(PollsService, 'pollsRetrieve').mockImplementation(async () => ({
      name: 'videos',
      criterias: [
        {
          name: 'largely_recommended',
          label: 'largely recommended',
          optional: false,
        },
      ],
    }));
  });

  const component = () => {
    render(
      <Router history={history}>
        <ThemeProvider theme={theme}>
          <PollProvider>
            <RecommendationPage />
          </PollProvider>
        </ThemeProvider>
      </Router>
    );
  };

  it('adds the navigator languages to the query string and stores them', async () => {
    navigatorLanguagesGetter.mockReturnValue(['fr', 'en-US']);
    await act(async () => component());

    expect(historySpy).toHaveBeenLastCalledWith({
      search: 'language=fr%2Cen',
    });
    expect(loadRecommendationsLanguages()).toEqual('fr,en');
    expect(getRecommendedVideosSpy).toHaveBeenCalledTimes(1);
    expect(getRecommendedVideosSpy).toHaveBeenLastCalledWith(
      'videos',
      20,
      '?language=fr%2Cen',
      expect.anything(),
      expect.anything()
    );
  });

  it('adds the stored languages to the query string', async () => {
    navigatorLanguagesGetter.mockReturnValue(['fr', 'en-US']);
    saveRecommendationsLanguages('de');
    await act(async () => component());

    expect(historySpy).toHaveBeenLastCalledWith({
      search: 'language=de',
    });
    expect(loadRecommendationsLanguages()).toEqual('de');
    expect(getRecommendedVideosSpy).toHaveBeenCalledTimes(1);
    expect(getRecommendedVideosSpy).toHaveBeenLastCalledWith(
      'videos',
      20,
      '?language=de',
      expect.anything(),
      expect.anything()
    );
  });

  it("doesn't change the languages already in the query string", async () => {
    navigatorLanguagesGetter.mockReturnValue(['fr', 'en-US']);
    saveRecommendationsLanguages('de');
    history.push({ search: 'language=fr' });
    await act(async () => component());

    expect(historySpy).not.toHaveBeenCalled();
    expect(loadRecommendationsLanguages()).toEqual('de');
    expect(getRecommendedVideosSpy).toHaveBeenCalledTimes(1);
    expect(getRecommendedVideosSpy).toHaveBeenLastCalledWith(
      'videos',
      20,
      '?language=fr',
      expect.anything(),
      expect.anything()
    );
  });
});
