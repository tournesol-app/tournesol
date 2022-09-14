/*
  Because of a regression in CRA v5, Typescript is wrongly enforced here
  See https://github.com/facebook/create-react-app/pull/11875
*/
// eslint-disable-next-line
// @ts-nocheck
import React from 'react';
import { render, screen } from '@testing-library/react';
import { within } from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import { SnackbarProvider } from 'notistack';
import { act } from 'react-dom/test-utils';

import { UsersService, ApiError } from 'src/services/openapi';

import VouchersPage from './VouchersPage';

describe('VouchersPage', () => {
  const Component = () => (
    <SnackbarProvider>
      <VouchersPage />
    </SnackbarProvider>
  );

  const getUsernameInput = () =>
    screen.queryByLabelText('personalVouchers.usernameLabel');

  const submitForm = async ({ username }) => {
    const input = getUsernameInput();
    expect(input).toBeTruthy();
    await userEvent.click(input);
    await userEvent.keyboard(username);
    await userEvent.keyboard('{Enter}');
  };

  const findGivenVoucher = async (username) => {
    const container = await screen.findByTestId('given-vouchers-list');
    expect(container.getAttribute('role')).toEqual('list');
    return await within(container).findByRole('listitem', { name: username });
  };

  const findReceivedVoucher = async (username) => {
    const container = await screen.findByTestId('received-vouchers-list');
    expect(container.getAttribute('role')).toEqual('list');
    return await within(container).findByRole('listitem', { name: username });
  };

  beforeEach(() => {
    jest
      .spyOn(UsersService, 'usersMeVouchersGivenList')
      .mockImplementation(async () => [
        {
          to: 'to_username1',
          by: 'by_username',
          value: 1.0,
          is_public: true,
        },
        {
          to: 'to_username2',
          by: 'by_username',
          value: 1.0,
          is_public: true,
        },
      ]);
  });

  beforeEach(() => {
    jest
      .spyOn(UsersService, 'usersMeVouchersReceivedList')
      .mockImplementation(async () => [
        {
          to: 'current user',
          by: 'received username 1',
          value: 1.0,
          is_public: true,
        },
        {
          to: 'current user',
          by: 'received username 2',
          value: 1.0,
          is_public: true,
        },
      ]);
  });

  it('creates a voucher when the form is submitted', async () => {
    const createdVoucher = {
      to: 'someone',
      by: 'current user',
      value: 1.0,
      is_public: true,
    };
    const createVoucherServiceSpy = jest
      .spyOn(UsersService, 'usersMeVouchersCreate')
      .mockImplementation(async () => createdVoucher);

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
    const consoleErrorSpy = jest
      .spyOn(console, 'error')
      .mockImplementation(() => undefined);
    const error = new ApiError({
      url: 'some url',
      status: 400,
      statusText: 'Bad Request',
      body: { to: ['some error'] },
    });

    jest
      .spyOn(UsersService, 'usersMeVouchersCreate')
      .mockImplementation(async () => {
        throw error;
      });

    render(<Component />);
    await submitForm({ username: 'someone' });

    screen.getByText('some error');
    expect(getUsernameInput().value).toEqual('someone');
    expect(consoleErrorSpy).toHaveBeenCalledWith(error);
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
      .mockImplementation(async () => undefined);

    render(<Component />);
    const voucherElement = await findGivenVoucher('to_username1');
    const deleteButton = await within(voucherElement).findByTestId(
      'CancelIcon'
    );
    await act(() => userEvent.click(deleteButton));

    expect(destroyVoucherServiceSpy).toHaveBeenCalledWith({
      username: 'to_username1',
    });
    expect(voucherElement).not.toBeInTheDocument();
    screen.getByText('personalVouchers.givenVoucherDeleted');
  });

  it('handles error on given voucher deletion', async () => {
    const consoleErrorSpy = jest
      .spyOn(console, 'error')
      .mockImplementation(() => undefined);
    const error = new ApiError({
      url: 'some url',
      status: 404,
      statusText: 'Not Found',
      body: { detail: 'Not found.' },
    });
    const destroyVoucherServiceSpy = jest
      .spyOn(UsersService, 'usersMeVouchersGivenDestroy')
      .mockImplementation(async () => {
        throw error;
      });

    render(<Component />);
    const voucherElement = await findGivenVoucher('to_username1');
    const deleteButton = await within(voucherElement).findByTestId(
      'CancelIcon'
    );
    await act(() => userEvent.click(deleteButton));

    expect(destroyVoucherServiceSpy).toHaveBeenCalledWith({
      username: 'to_username1',
    });
    screen.findByText('Not found');
    expect(voucherElement).toBeInTheDocument();
    expect(consoleErrorSpy).toHaveBeenCalledWith(error);
  });
});
