import React from 'react';
import { MemoryRouter, Route, Switch } from 'react-router-dom';
import { fireEvent, render, screen } from '@testing-library/react';
import { HowToVote, YouTube } from '@mui/icons-material';
import PollSelector from './PollSelector';
import { PollProvider } from 'src/hooks/useCurrentPoll';
import {
  PRESIDENTIELLE_2022_POLL_NAME,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';
import { SelectablePoll } from 'src/utils/types';

describe('change password feature', () => {
  const polls: Array<SelectablePoll> = [
    {
      name: PRESIDENTIELLE_2022_POLL_NAME,
      defaultAnonEntityActions: [],
      defaultAuthEntityActions: [],
      displayOrder: 20,
      mainCriterionName: 'be_president',
      path: '/presidentielle2022/',
      iconComponent: HowToVote,
      withSearchBar: false,
      topBarBackground:
        'linear-gradient(60deg, #8b8be8 0%, white 33%, #e16767 100%)',
    },
    {
      name: YOUTUBE_POLL_NAME,
      defaultAnonEntityActions: [],
      defaultAuthEntityActions: [],
      displayOrder: 10,
      mainCriterionName: 'largely_recommended',
      path: '/',
      iconComponent: YouTube,
      withSearchBar: true,
      topBarBackground: null,
    },
  ];

  const component = () =>
    render(
      <PollProvider>
        <MemoryRouter>
          <Switch>
            <Route path="/">
              <PollSelector polls={polls} />
            </Route>
          </Switch>
        </MemoryRouter>
      </PollProvider>
    );

  const setup = () => {
    const rendered = component();
    const logos = screen.getAllByAltText('Tournesol logo');
    const title = screen.getByText('Tournesol');
    return { logos, title, rendered };
  };

  it("doesn't display the menu by default", () => {
    setup();
    expect(screen.queryAllByRole('menuitem')).toHaveLength(0);
    expect(screen.getByTestId('ArrowDropDownIcon')).toBeInTheDocument();
  });

  it('click on the logo displays the menu', () => {
    const { logos } = setup();

    fireEvent.click(logos[0]);
    expect(screen.getAllByRole('menuitem')).toHaveLength(2);
    expect(screen.getByTestId('ArrowDropUpIcon')).toBeInTheDocument();
  });

  it('click on the title displays the menu', () => {
    const { title } = setup();

    fireEvent.click(title);
    expect(screen.getAllByRole('menuitem')).toHaveLength(2);
    expect(screen.getByTestId('ArrowDropUpIcon')).toBeInTheDocument();
  });

  it('items can be selected, and poll changed', () => {
    const { title } = setup();

    fireEvent.click(title);
    // then click on item 1
    fireEvent.click(screen.getAllByRole('menuitem')[0]);
    expect(screen.queryAllByRole('menuitem')).toHaveLength(0);

    expect(screen.getByRole('heading', { level: 6 })).toHaveTextContent(
      'poll.video'
    );

    fireEvent.click(title);
    // then click on item 2
    fireEvent.click(screen.getAllByRole('menuitem')[1]);
    expect(screen.queryAllByRole('menuitem')).toHaveLength(0);

    expect(screen.getByRole('heading', { level: 6 })).toHaveTextContent(
      'poll.presidential2022'
    );
  });
});
