import React from 'react';
import { MemoryRouter, Route, Switch } from 'react-router-dom';
import { fireEvent, render, screen } from '@testing-library/react';
import { HowToVote, YouTube } from '@mui/icons-material';
import PollSelector from './PollSelector';
import {
  PRESIDENTIELLE_2022_POLL_NAME,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';
import { SelectablePolls } from 'src/utils/types';

describe('change password feature', () => {
  const polls: SelectablePolls = [
    {
      name: PRESIDENTIELLE_2022_POLL_NAME,
      displayOrder: 20,
      path: '/presidentielle2022/',
      iconComponent: HowToVote,
      withSearchBar: false,
      topBarBackground:
        'linear-gradient(60deg, #8b8be8 0%, white 33%, #e16767 100%)',
    },
    {
      name: YOUTUBE_POLL_NAME,
      displayOrder: 10,
      path: '/',
      iconComponent: YouTube,
      withSearchBar: true,
      topBarBackground: null,
    },
  ];

  const component = () =>
    render(
      <MemoryRouter>
        <Switch>
          <Route path="/">
            <PollSelector polls={polls} />
          </Route>
        </Switch>
      </MemoryRouter>
    );

  const setup = () => {
    const rendered = component();
    const logos = screen.getAllByAltText('Tournesol logo');
    const title = screen.getByText('Tournesol');
    return { logos, title, rendered };
  };

  it('click on the logo displays the menu', async () => {
    const { logos } = setup();
    expect(screen.queryAllByRole('menuitem')).toHaveLength(0);

    fireEvent.click(logos[0]);
    expect(screen.getAllByRole('menuitem')).toHaveLength(2);
  });

  it('click on the title displays the menu', async () => {
    const { title } = setup();
    expect(screen.queryAllByRole('menuitem')).toHaveLength(0);

    fireEvent.click(title);
    expect(screen.getAllByRole('menuitem')).toHaveLength(2);
  });

  it('the menu is closed after a click on an item', async () => {
    const { title } = setup();
    expect(screen.queryAllByRole('menuitem')).toHaveLength(0);

    fireEvent.click(title);
    // then click on item 1
    fireEvent.click(screen.getAllByRole('menuitem')[0]);
    expect(screen.queryAllByRole('menuitem')).toHaveLength(0);

    fireEvent.click(title);
    // then click on item 2
    fireEvent.click(screen.getAllByRole('menuitem')[1]);
    expect(screen.queryAllByRole('menuitem')).toHaveLength(0);
  });
});
