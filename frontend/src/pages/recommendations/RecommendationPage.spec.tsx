/*
  Because of a regression in CRA v5, Typescript is wrongly enforced here
  See https://github.com/facebook/create-react-app/pull/11875
*/
// eslint-disable-next-line
// @ts-nocheck
import React from 'react';
import * as reactRedux from 'react-redux';

import configureStore, {
  MockStoreCreator,
  MockStoreEnhanced,
} from 'redux-mock-store';
import { AnyAction } from '@reduxjs/toolkit';
import thunk, { ThunkDispatch } from 'redux-thunk';
import { createMemoryHistory } from 'history';
import { act } from 'react-dom/test-utils';
import { Router } from 'react-router-dom';

import { ThemeProvider } from '@mui/material/styles';
import { render } from '@testing-library/react';

import { initialState } from 'src/features/login/loginSlice';
import { LoginState } from 'src/features/login/LoginState.model';
import { PollProvider } from 'src/hooks/useCurrentPoll';
import RecommendationPage from 'src/pages/recommendations/RecommendationPage';
import { PollsService, TournesolUserSettings } from 'src/services/openapi';
import { theme } from 'src/theme';
import * as RecommendationApi from 'src/utils/api/recommendations';
import {
  saveRecommendationsLanguages,
  loadRecommendationsLanguages,
} from 'src/utils/recommendationsLanguages';

interface MockState {
  token: LoginState;
  settings: TournesolUserSettings;
}

vi.mock('src/features/entities/EntityList', () => {
  const EntityList = () => null;
  return {
    default: EntityList,
  };
});

vi.mock('src/features/recommendation/SearchFilter', () => {
  const SearchFilter = () => null;
  return {
    default: SearchFilter,
  };
});

describe('RecommendationPage', () => {
  let history: ReturnType<typeof createMemoryHistory>;
  let historySpy: ReturnType<typeof vi.spyOn>;
  let navigatorLanguagesGetter: ReturnType<typeof vi.spyOn>;
  let getRecommendedVideosSpy: ReturnType<typeof vi.spyOn>;

  const mockStore: MockStoreCreator<
    MockState,
    ThunkDispatch<LoginState, undefined, AnyAction>
  > = configureStore([thunk]);

  beforeEach(() => {
    history = createMemoryHistory();
    historySpy = vi.spyOn(history, 'replace');
    navigatorLanguagesGetter = vi.spyOn(window.navigator, 'languages', 'get');
    getRecommendedVideosSpy = vi
      .spyOn(RecommendationApi, 'getRecommendations')
      .mockImplementation(async () => ({ count: 0, results: [] }));

    // prevent the useCurrentPoll hook to make HTTP requests
    vi.spyOn(PollsService, 'pollsRetrieve').mockImplementation(async () => ({
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

  const component = async ({
    store,
  }: {
    store: MockStoreEnhanced<MockState>;
  }) => {
    return await act(async () => {
      Promise.resolve(
        render(
          <reactRedux.Provider store={store}>
            <Router history={history}>
              <ThemeProvider theme={theme}>
                <PollProvider>
                  <RecommendationPage />
                </PollProvider>
              </ThemeProvider>
            </Router>
          </reactRedux.Provider>
        )
      );
    });
  };

  const setup = async () => {
    const state = { token: initialState, settings: {} };
    const store = mockStore(state);
    const rendered = await component({ store: store });

    return { rendered };
  };

  it('adds the navigator languages to the query string and stores them', async () => {
    navigatorLanguagesGetter.mockReturnValue(['fr', 'en-US']);
    await setup();

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
    await setup();

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
    await setup();

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
