import React from 'react';
import { render, screen } from '@testing-library/react';
import { within } from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import { SnackbarProvider } from 'notistack';
import { act } from 'react-dom/test-utils';

import {
  UsersService,
  ApiError,
  CancelablePromise,
  GivenVoucher,
  ReadOnlyVoucher,
} from 'src/services/openapi';

import VouchersPage from './VouchersPage';

describe('VouchersPage', () => {
  const Component = () => (
    <SnackbarProvider>
      <VouchersPage />
    </SnackbarProvider>
  );

  const getUsernameInput = (): HTMLInputElement => {
    const result = screen.queryByLabelText('personalVouchers.usernameLabel *');
    if (result === null) throw new Error('Username input not found');
    return result as HTMLInputElement;
  };

  const submitForm = async ({ username }: { username: string }) => {
    const input = getUsernameInput();
    await userEvent.click(input);
    await userEvent.keyboard(username);
    await userEvent.keyboard('{Enter}');
  };

  const findGivenVoucher = async (username: string) => {
    const container = await screen.findByTestId('given-vouchers-list');
    expect(container.getAttribute('role')).toEqual('list');
    return await within(container).findByRole('listitem', { name: username });
  };

  const findReceivedVoucher = async (username: string) => {
    const container = await screen.findByTestId('received-vouchers-list');
    expect(container.getAttribute('role')).toEqual('list');
    return await within(container).findByRole('listitem', { name: username });
  };

  beforeEach(() => {
    jest
      .spyOn(UsersService, 'usersMeVouchersGivenList')
      .mockImplementation((async () => [
        {
          to: 'to_username1',
          by: 'by_username',
        },
        {
          to: 'to_username2',
          by: 'by_username',
        },
      ]) as () => CancelablePromise<GivenVoucher[]>);
  });

  beforeEach(() => {
    jest
      .spyOn(UsersService, 'usersMeVouchersReceivedList')
      .mockImplementation((async () => [
        {
          to: 'current user',
          by: 'received username 1',
        },
        {
          to: 'current user',
          by: 'received username 2',
        },
      ]) as () => CancelablePromise<ReadOnlyVoucher[]>);
  });

  it('creates a voucher when the form is submitted', async () => {
    const createdVoucher = {
      to: 'someone',
      by: 'current user',
    };
    const createVoucherServiceSpy = jest
      .spyOn(UsersService, 'usersMeVouchersCreate')
      .mockImplementation(
        (async () => createdVoucher) as () => CancelablePromise<GivenVoucher>
      );

    render(<Component />);
    await act(() => submitForm({ username: 'someone' }));

    expect(createVoucherServiceSpy).toHaveBeenCalledWith({
      requestBody: { to: 'someone' },
    });
    screen.getByText('personalVouchers.voucherCreated');
    expect(getUsernameInput().value).toEqual('');
    await findGivenVoucher('someone');
  });

  it('handles error on form submit', async () => {
    const error = new ApiError(
      {
        method: 'GET',
        url: 'some url',
      },
      {
        url: 'some url',
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        body: { to: ['some error'] },
      },
      'error'
    );

    jest
      .spyOn(UsersService, 'usersMeVouchersCreate')
      .mockImplementation((async (): Promise<GivenVoucher> => {
        throw error;
      }) as () => CancelablePromise<GivenVoucher>);

    render(<Component />);
    await act(() => submitForm({ username: 'someone' }));

    /**
     * An error in the hook useNotification.displayErrorsFrom can make the
     * next statement fail.
     *
     * If we want this test to be less end-to-end and more input/output, we
     * could instead simply check if displayErrorsFrom has been called only
     * once, with the good argument.
     *
     * This way, we reduce the scope of this test to only the voucher related
     * components. It will then fail only when one of those components fails.
     *
     * NOTE: as long as we don't have any proper end-to-end tests, we should
     * keep the following line.
     */
    screen.getByText('some error');
    expect(getUsernameInput().value).toEqual('someone');
  });

  it('lists given vouchers', async () => {
    render(<Component />);
    await findGivenVoucher('to_username1');
    await findGivenVoucher('to_username2');
  });

  it('lists received vouchers', async () => {
    render(<Component />);
    await findReceivedVoucher('received username 1');
    await findReceivedVoucher('received username 2');
  });

  it('deletes a given voucher', async () => {
    const destroyVoucherServiceSpy = jest
      .spyOn(UsersService, 'usersMeVouchersGivenDestroy')
      .mockImplementation(
        (async () => undefined) as () => CancelablePromise<void>
      );

    render(<Component />);
    const voucherElement = await findGivenVoucher('to_username1');
    const deleteButton = await within(voucherElement).findByTestId(
      'CancelIcon'
    );

    await act(async () => userEvent.click(deleteButton));

    expect(destroyVoucherServiceSpy).toHaveBeenCalledWith({
      username: 'to_username1',
    });
    expect(voucherElement).not.toBeInTheDocument();
    screen.getByText('personalVouchers.givenVoucherDeleted');
  });

  it('handles error on given voucher deletion', async () => {
    const error = new ApiError(
      {
        method: 'GET',
        url: 'some url',
      },
      {
        url: 'some url',
        ok: false,
        status: 404,
        statusText: 'Not Found',
        body: { detail: 'Not found.' },
      },
      'error'
    );
    const destroyVoucherServiceSpy = jest
      .spyOn(UsersService, 'usersMeVouchersGivenDestroy')
      .mockImplementation((async (): Promise<void> => {
        throw error;
      }) as () => CancelablePromise<void>);

    render(<Component />);
    const voucherElement = await findGivenVoucher('to_username1');
    const deleteButton = await within(voucherElement).findByTestId(
      'CancelIcon'
    );
    await act(async () => userEvent.click(deleteButton));

    expect(destroyVoucherServiceSpy).toHaveBeenCalledWith({
      username: 'to_username1',
    });

    /**
     * An error in the hook useNotification.displayErrorsFrom can make the
     * next statement fail.
     *
     * If we want this test to be less end-to-end and more input/output, we
     * could instead simply check if displayErrorsFrom has been called only
     * once, with the good argument.
     *
     * This way, we reduce the scope of this test to only the voucher related
     * components. It will then fail only when one of those components fails.
     *
     * NOTE: as long as we don't have any proper end-to-end tests, we should
     * keep the following line.
     */
    screen.findByText('Not found');
    expect(voucherElement).toBeInTheDocument();
  });
});
