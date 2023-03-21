import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import Pagination from './Pagination';
import { theme } from 'src/theme';

interface PaginationProps {
  limit: number;
  offset: number;
  count: number;
  onOffsetChange: (n: number) => void;
  widthScreen?: number;
}

const onOffsetChange = jest.fn();

const defineMatchMedia = (width: number) => {
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: width,
  });
  window.matchMedia = jest.fn().mockImplementation((query) => {
    return {
      matches: width == theme.breakpoints.values.sm ? true : false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    };
  });
};

describe('Pagination component', () => {
  const component = ({
    offset,
    limit,
    count,
    onOffsetChange,
    widthScreen,
  }: PaginationProps) => {
    defineMatchMedia(widthScreen ? widthScreen : theme.breakpoints.values.lg);
    render(
      <ThemeProvider theme={theme}>
        <Pagination
          offset={offset}
          count={count}
          limit={limit}
          onOffsetChange={onOffsetChange}
        />
      </ThemeProvider>
    );
  };

  const setup = ({
    offset,
    limit,
    count,
    onOffsetChange,
    widthScreen,
  }: PaginationProps) => {
    const rendered = component({
      offset,
      limit,
      count,
      onOffsetChange,
      widthScreen,
    });
    return { rendered };
  };

  it('displays buttons -1 and -10 as disabled when current page is first', () => {
    const paginationProps: PaginationProps = {
      offset: 0,
      limit: 1,
      count: 5,
      onOffsetChange: onOffsetChange,
    };

    setup(paginationProps);

    const prev1 = screen.getByRole('button', { name: /^< -1$/i });
    const prev10 = screen.getByRole('button', { name: /< -10/i });
    expect(prev1).toBeDisabled();
    expect(prev10).toBeDisabled();

    const next1 = screen.getByRole('button', { name: /^\+1 >$/i });
    const next10 = screen.getByRole('button', { name: /\+10 >/i });
    expect(next1).toBeEnabled();
    expect(next10).toBeEnabled();

    // The buttons -100 and +100 should not be visible.
    const minus100Button = screen.queryByRole('button', { name: /< -100/i });
    const plus100Button = screen.queryByRole('button', { name: / \+100 >/i });
    expect(minus100Button).not.toBeInTheDocument();
    expect(plus100Button).not.toBeInTheDocument();
  });

  it('displays buttons +1 and +10 as disabled when current page is last', () => {
    const paginationProps: PaginationProps = {
      offset: 4,
      limit: 1,
      count: 5,
      onOffsetChange: onOffsetChange,
    };

    setup(paginationProps);

    const prev1 = screen.getByRole('button', { name: /^< -1$/i });
    const prev10 = screen.getByRole('button', { name: /< -10/i });
    expect(prev1).toBeEnabled();
    expect(prev10).toBeEnabled();

    const next1 = screen.getByRole('button', { name: /^\+1 >$/i });
    const next10 = screen.getByRole('button', { name: /\+10 >/i });
    expect(next1).toBeDisabled();
    expect(next10).toBeDisabled();

    // The buttons -100 and +100 should not be visible.
    const minus100Button = screen.queryByRole('button', { name: /< -100/i });
    const plus100Button = screen.queryByRole('button', { name: / \+100 >/i });
    expect(minus100Button).not.toBeInTheDocument();
    expect(plus100Button).not.toBeInTheDocument();
  });

  it('displays 5 pages with limit: 20, count: 100', () => {
    const paginationProps: PaginationProps = {
      offset: 0,
      limit: 20,
      count: 100,
      onOffsetChange: onOffsetChange,
    };

    setup(paginationProps);

    // [WHEN] The PaginationComponent is configured with boundaryCount=2 and
    // siblingCount=3, we expect 5 pages to be displayed.
    const pages = screen.getAllByRole('button', { name: /page \d+/i });
    expect(pages).toHaveLength(5);

    // click on page 2
    fireEvent.click(screen.getByRole('button', { name: /page 2/i }));
    expect(paginationProps.onOffsetChange).toHaveBeenCalledWith(20);

    // click on page 4
    fireEvent.click(screen.getByRole('button', { name: /page 4/i }));
    expect(paginationProps.onOffsetChange).toHaveBeenCalledWith(60);

    // click on next 1 page button
    fireEvent.click(screen.getByRole('button', { name: /\+1 >/i }));
    expect(paginationProps.onOffsetChange).toHaveBeenCalledWith(20);

    // click on next 10 page button
    fireEvent.click(screen.getByRole('button', { name: /\+10 >/i }));
    expect(paginationProps.onOffsetChange).toHaveBeenCalledWith(80);
  });

  it('displays 12 pages with limit: 20, count: 270', () => {
    const paginationProps: PaginationProps = {
      offset: 0,
      limit: 20,
      count: 270,
      onOffsetChange: onOffsetChange,
    };

    setup(paginationProps);

    // [WHEN] The PaginationComponent is configured with boundaryCount=2 and
    // siblingCount=3, we expect 12 pages to be displayed.
    const pages = screen.getAllByRole('button', { name: /page \d+/i });
    expect(pages).toHaveLength(12);

    // click on page 10
    fireEvent.click(screen.getByRole('button', { name: /page 10/i }));
    expect(paginationProps.onOffsetChange).toHaveBeenCalledWith(180);

    // click on next 10 page button
    fireEvent.click(screen.getByRole('button', { name: /\+10 >/i }));
    expect(paginationProps.onOffsetChange).toHaveBeenCalledWith(200);
  });

  it('displays 11 pages when limit: 20, count: 615, offset: 240', () => {
    const paginationProps: PaginationProps = {
      offset: 240,
      limit: 20,
      count: 615,
      onOffsetChange: onOffsetChange,
    };

    setup(paginationProps);

    // [WHEN] The PaginationComponent is configured with boundaryCount=2 and
    // siblingCount=3, we expect 11 pages to be displayed.
    const pages = screen.getAllByRole('button', { name: /page \d+/i });
    expect(pages).toHaveLength(11);

    // check present of last page button
    const lastPageButton = screen.queryByRole('button', { name: /31/i });
    expect(lastPageButton).toBeInTheDocument();

    // check for the presence of the penultimate page button
    const lastPenultimatePageButton = screen.queryByRole('button', {
      name: /30/i,
    });
    expect(lastPenultimatePageButton).toBeInTheDocument();

    // click on page 31
    fireEvent.click(screen.getByRole('button', { name: /page 31/i }));
    expect(paginationProps.onOffsetChange).toHaveBeenCalledWith(600);
  });

  it('test navigation page buttons from 50 page', () => {
    const paginationProps: PaginationProps = {
      offset: 980,
      limit: 20,
      count: 3000,
      onOffsetChange: onOffsetChange,
    };

    setup(paginationProps);

    // Check if the -100 and +100 buttons are visible
    const minus100Button = screen.queryByRole('button', { name: /< -100/i });
    const plus100Button = screen.queryByRole('button', { name: /\+100 >/i });
    expect(minus100Button).toBeInTheDocument();
    expect(plus100Button).toBeInTheDocument();

    // click on next 100 page button from page 50
    fireEvent.click(screen.getByRole('button', { name: /\+100 >/i }));
    expect(paginationProps.onOffsetChange).toHaveBeenCalledWith(2980);

    // click on previous 100 page button from page 50
    fireEvent.click(screen.getByRole('button', { name: /< -100/i }));
    expect(paginationProps.onOffsetChange).toHaveBeenCalledWith(0);

    // click on previous 10 page button from page 50
    fireEvent.click(screen.getByRole('button', { name: /^< -10$/i }));
    expect(paginationProps.onOffsetChange).toHaveBeenCalledWith(780);

    // click on previous 1 page button from page 50
    fireEvent.click(screen.getByRole('button', { name: /^< -1$/i }));
    expect(paginationProps.onOffsetChange).toHaveBeenCalledWith(960);
  });

  describe('Screen size: sm', () => {
    it('displays 6 pages when limit: 20, count: 270', () => {
      const paginationProps: PaginationProps = {
        offset: 0,
        limit: 20,
        count: 270,
        onOffsetChange: onOffsetChange,
        widthScreen: theme.breakpoints.values.sm,
      };

      setup(paginationProps);

      // [WHEN] The PaginationComponent is configured with boundaryCount=1 and
      // siblingCount=1, we expect 6 pages to be displayed.
      const pages = screen.getAllByRole('button', { name: /page \d+/i });
      expect(pages).toHaveLength(6);

      // check that last button is page 14
      const lastPageButton = screen.queryByRole('button', { name: /14/i });
      expect(lastPageButton).toBeInTheDocument();

      const minus1Button = screen.getByRole('button', { name: /^< -1$/i });
      expect(minus1Button).toBeInTheDocument();
      const minus10Button = screen.getByRole('button', { name: /^< -10$/i });
      expect(minus10Button).toBeInTheDocument();

      const plus1Button = screen.getByRole('button', { name: /^\+1 >$/i });
      expect(plus1Button).toBeInTheDocument();
      const plus10Button = screen.getByRole('button', { name: /^\+10 >$/i });
      expect(plus10Button).toBeInTheDocument();

      // Check if the -100 and +100 buttons are not visible
      const minus100Button = screen.queryByRole('button', { name: /< -100/i });
      const plus100Button = screen.queryByRole('button', { name: / \+100 >/i });
      expect(minus100Button).not.toBeInTheDocument();
      expect(plus100Button).not.toBeInTheDocument();
    });
  });
});
