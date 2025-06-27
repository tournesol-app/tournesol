/*
  Because of a regression in CRA v5, Typescript is wrongly enforced here
  See https://github.com/facebook/create-react-app/pull/11875
*/
// eslint-disable-next-line
// @ts-nocheck
import React from 'react';
import { ThemeProvider, StyledEngineProvider } from '@mui/material/styles';
import { theme } from 'src/theme';
import {
  render,
  screen,
  fireEvent,
  queryAllByTestId,
  queryByTestId,
  act,
  within,
} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RouterProvider, createMemoryRouter } from 'react-router-dom';

import { PollProvider } from 'src/hooks/useCurrentPoll';
import { PollsService } from 'src/services/openapi';
import { combineReducers, createStore } from 'redux';
import loginReducer, { initialState } from '../login/loginSlice';
import { Provider } from 'react-redux';

import SearchFilter from './SearchFilter';

describe('Filters feature', () => {
  async function renderSearchFilters(loggedIn: boolean) {
    const routes = [
      {
        path: '/search',
        element: (
          <SearchFilter
            onLanguagesChange={(langs) =>
              localStorage.setItem('languages', langs)
            }
          />
        ),
      },
    ];

    const router = createMemoryRouter(routes, {
      initialEntries: ['/search'],
      initialIndex: 0,
    });

    vi.spyOn(PollsService, 'pollsRetrieve').mockImplementation(async () => ({
      name: 'videos',
      criterias: [
        {
          name: 'criteria1',
          label: 'Criteria 1 Label',
          optional: false,
        },
        {
          name: 'criteria2',
          label: 'Criteria 2 Label',
          optional: true,
        },
        {
          name: 'criteria3',
          label: 'Criteria 3 Label',
          optional: true,
        },
      ],
    }));

    // Some context is needed by the component SearchFilter
    await act(async () => {
      const anHourInMS = 1000 * 60 * 60;
      const now = new Date();
      const anHourLater = new Date(now.getTime() + anHourInMS);
      const login = { ...initialState };
      if (loggedIn) {
        login.access_token = 'dummy_token';
        login.access_token_expiration_date = anHourLater.toString();
      }
      const mockStore = createStore(combineReducers({ token: loginReducer }), {
        token: login,
      });

      render(
        <Provider store={mockStore}>
          <StyledEngineProvider injectFirst>
            <ThemeProvider theme={theme}>
              <PollProvider>
                <RouterProvider router={router}></RouterProvider>
              </PollProvider>
            </ThemeProvider>
          </StyledEngineProvider>
        </Provider>
      );
    });

    return { router };
  }

  function clickOnShowMore(wasClosed = true) {
    const checkboxDisplayFilters = screen.queryByLabelText('show more');
    expect(checkboxDisplayFilters).not.toBeNull();

    // aria-expanded should be set to false if the filters menu was closed,
    // and true otherwise
    expect(checkboxDisplayFilters.getAttribute('aria-expanded')).toBe(
      (!wasClosed).toString()
    );

    fireEvent.click(checkboxDisplayFilters);

    // Now it should have changed
    expect(checkboxDisplayFilters.getAttribute('aria-expanded')).toBe(
      wasClosed.toString()
    );
  }

  function verifyFiltersPresence(isLoggedIn: boolean) {
    // Check date and safe filters presence
    const dateAndAdvancedFilter = document.querySelector(
      '[data-testid=search-date-and-advanced-filter]'
    );
    expect(
      queryAllByTestId(dateAndAdvancedFilter, /checkbox-choice/i)
    ).toHaveLength(isLoggedIn ? 7 : 6);

    // Check language filters presence
    const languageFilter = document.querySelector(
      '[data-testid=search-language-filter]'
    );
    expect(queryAllByTestId(languageFilter, 'autocomplete')).toHaveLength(1);

    // Check the duration filter presence
    expect(screen.getByTestId('filter-duration-lte')).toBeVisible();
    expect(screen.getByTestId('filter-duration-gte')).toBeVisible();

    // Check criteria filters presence
    expect(screen.getByLabelText('multiple criteria')).toBeVisible();
  }

  // Click on a date filter checkbox
  function clickOnDateCheckbox({
    checkbox,
  }: {
    checkbox: 'Today' | 'Week' | 'Month' | 'Year' | '';
  }) {
    const dateCheckbox = screen.queryByTestId('checkbox-choice-' + checkbox);
    expect(dateCheckbox).not.toBeNull();
    fireEvent.click(dateCheckbox);
  }

  // Select or unselect a language and verify the local storage
  function selectLanguage({
    language,
    action = 'add',
    expectInLocalStorage,
  }: {
    language: string;
    action: 'add' | 'remove';
    expectInLocalStorage: string;
  }) {
    const languageFilter = queryByTestId(document, 'search-language-filter');
    const autocomplete = queryByTestId(languageFilter, 'autocomplete');
    expect(autocomplete).not.toBeNull();
    const input = within(autocomplete).getByRole('combobox');
    expect(input).not.toBeNull();

    if (action === 'add') {
      autocomplete.focus();
      userEvent.type(input, language);
      // Select the first item
      fireEvent.keyDown(autocomplete, { key: 'ArrowDown' });
      fireEvent.keyDown(autocomplete, { key: 'Enter' });
    } else if (action === 'remove') {
      const buttons = within(autocomplete).getAllByRole('button');
      const button = buttons.find((b) => b.textContent === language);
      expect(button).not.toBeUndefined();
      const removeButton = within(button).getByTestId('CancelIcon');
      fireEvent.click(removeButton);
    }

    expect(localStorage.getItem('languages')).toEqual(expectInLocalStorage);
  }

  it('Can open and close the filters menu', async () => {
    await renderSearchFilters(true);
    // Click to open the filters menu. The checks are made inside clickOnShowMore.
    clickOnShowMore();

    // Click again to close back the filters menu
    clickOnShowMore(false);
  });

  it('Check that all the filter checkboxes and sliders are present for anonymous', async () => {
    await renderSearchFilters(false);
    clickOnShowMore();
    verifyFiltersPresence(false);
  });

  it('Check that all the filter checkboxes and sliders are present for a logged in user', async () => {
    await renderSearchFilters(true);
    clickOnShowMore();
    verifyFiltersPresence(true);
  });

  it('Can only check one date filter at once', async () => {
    const { router } = await renderSearchFilters(true);
    clickOnShowMore();

    clickOnDateCheckbox({ checkbox: 'Week' });
    expect(router.state.location.search).toEqual('?date=Week');
    clickOnDateCheckbox({ checkbox: 'Month' });
    expect(router.state.location.search).toEqual('?date=Month');
    clickOnDateCheckbox({ checkbox: 'Today' });
    expect(router.state.location.search).toEqual('?date=Today');
    clickOnDateCheckbox({ checkbox: 'Year' });
    expect(router.state.location.search).toEqual('?date=Year');

    // A second click on "This year" should not change the URL
    clickOnDateCheckbox({ checkbox: 'Year' });
    expect(router.state.location.search).toEqual('?date=Year');
    clickOnDateCheckbox({ checkbox: '' });
    expect(router.state.location.search).toEqual('?date=');
  });

  it('Can check multiple language filters at once', async () => {
    const { router } = await renderSearchFilters(true);
    clickOnShowMore();

    // Adding new languages
    selectLanguage({ language: 'language.en', expectInLocalStorage: 'en' });
    expect(router.state.location.search).toEqual('?language=en');
    selectLanguage({ language: 'language.fr', expectInLocalStorage: 'en,fr' });
    expect(router.state.location.search).toEqual(
      `?language=${encodeURIComponent('en,fr')}`
    );
    selectLanguage({
      language: 'language.de',
      expectInLocalStorage: 'en,fr,de',
    });
    expect(router.state.location.search).toEqual(
      `?language=${encodeURIComponent('en,fr,de')}`
    );

    // Removing languages
    selectLanguage({
      action: 'remove',
      language: 'language.fr',
      expectInLocalStorage: 'en,de',
    });
    expect(router.state.location.search).toEqual(
      `?language=${encodeURIComponent('en,de')}`
    );
    selectLanguage({
      action: 'remove',
      language: 'language.en',
      expectInLocalStorage: 'de',
    });
    expect(router.state.location.search).toEqual(
      `?language=${encodeURIComponent('de')}`
    );
    selectLanguage({
      action: 'remove',
      language: 'language.de',
      expectInLocalStorage: '',
    });
    expect(router.state.location.search).toEqual(`?language=`);
  });

  it('Can select a maximum duration', async () => {
    const { router } = await renderSearchFilters(true);
    clickOnShowMore();

    const filter = screen
      .getByTestId('filter-duration-lte')
      .querySelector('input');

    await act(async () => {
      fireEvent.change(filter, { target: { value: '40' } });
      // The URL should not change before the typing delay of DurationFilter
      // has passed.
      expect(router.state.location.search).toEqual('');
      await new Promise((resolve) => setTimeout(resolve, 800));
    });

    expect(router.state.location.search).toEqual('?duration_lte=40');
  });

  it('Can select a minimum duration', async () => {
    const { router } = await renderSearchFilters(true);
    clickOnShowMore();

    const filter = screen
      .getByTestId('filter-duration-gte')
      .querySelector('input');

    await act(async () => {
      fireEvent.change(filter, { target: { value: '20' } });
      // The URL should not change before the typing delay of DurationFilter
      // has passed.
      expect(router.state.location.search).toEqual('');
      await new Promise((resolve) => setTimeout(resolve, 800));
    });

    expect(router.state.location.search).toEqual('?duration_gte=20');
  });

  it('Can fold and unfold the multiple criteria', async () => {
    await renderSearchFilters(true);
    clickOnShowMore();

    // By default the criteria sliders must be hidden.
    const checkbox = screen.getByLabelText('multiple criteria');
    expect(screen.queryAllByLabelText(/neutral/i)).toHaveLength(0);
    expect(
      screen.queryByTestId('filter-criterion-slider-criteria1')
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('filter-criterion-slider-criteria2')
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('filter-criterion-slider-criteria3')
    ).not.toBeInTheDocument();

    // A click on the label must display all criteria sliders.
    fireEvent.click(checkbox);
    expect(screen.getAllByText(/neutral/i)).toHaveLength(3);
    expect(
      screen.getByTestId('filter-criterion-slider-criteria1')
    ).toBeVisible();
    expect(
      screen.getByTestId('filter-criterion-slider-criteria2')
    ).toBeVisible();
    expect(
      screen.getByTestId('filter-criterion-slider-criteria3')
    ).toBeVisible();

    // An additional click on the label must hide all criteria sliders.
    fireEvent.click(checkbox);
    expect(screen.queryAllByLabelText(/neutral/i)).toHaveLength(0);
    expect(
      screen.queryByTestId('filter-criterion-slider-criteria1')
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('filter-criterion-slider-criteria2')
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('filter-criterion-slider-criteria3')
    ).not.toBeInTheDocument();
  });
});
