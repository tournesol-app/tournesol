import React, { createContext, useContext, useCallback, useState } from 'react';

import {
  UsersService,
  GivenVoucher,
  ReadOnlyVoucher,
} from 'src/services/openapi';

interface PersonalVouchersValue {
  createVoucher: ({ username }: { username: string }) => void;
  deleteGivenVoucher: ({ username }: { username: string }) => void;
  givenVouchers?: GivenVoucher[];
  receivedVouchers?: ReadOnlyVoucher[];
}
const Context = createContext<PersonalVouchersValue>({
  createVoucher: () => {
    throw new Error('PersonalVouchersProvider not in tree');
  },
  deleteGivenVoucher: () => {
    throw new Error('PersonalVouchersProvider not in tree');
  },
});

export const usePersonalVouchers = () => useContext(Context);

export const PersonalVouchersProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const createVoucher = useCallback(
    async ({ username }: { username: string }) => {
      const voucher = await UsersService.usersMeVouchersCreate({
        requestBody: { to: username },
      });
      setValue((value) => ({
        ...value,
        givenVouchers: [...(value.givenVouchers || []), voucher],
      }));
      return voucher;
    },
    []
  );

  const deleteGivenVoucher = useCallback(
    async ({ username }: { username: string }) => {
      await UsersService.usersMeVouchersGivenDestroy({ username });
      setValue((value) => ({
        ...value,
        givenVouchers: (value.givenVouchers || []).filter(
          ({ to }) => to !== username
        ),
      }));
    },
    []
  );

  const [value, setValue] = useState<PersonalVouchersValue>({
    createVoucher,
    deleteGivenVoucher,
  });

  React.useEffect(() => {
    const loadGivenVouchers = async () => {
      const vouchers = await UsersService.usersMeVouchersGivenList();
      setValue((value) => ({ ...value, givenVouchers: vouchers }));
    };
    const loadReceivedVouchers = async () => {
      const vouchers = await UsersService.usersMeVouchersReceivedList();
      setValue((value) => ({ ...value, receivedVouchers: vouchers }));
    };
    loadGivenVouchers();
    loadReceivedVouchers();
  }, []);

  return <Context.Provider value={value}>{children}</Context.Provider>;
};
