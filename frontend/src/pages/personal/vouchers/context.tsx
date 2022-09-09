import React, { createContext, useContext, useCallback, useState } from 'react';

import { UsersService, GivenVoucher } from 'src/services/openapi';

interface PersonalVouchersValue {
  createVoucher: ({ username }: { username: string }) => void;
  givenVouchers?: GivenVoucher[];
}
const Context = createContext<PersonalVouchersValue>({
  createVoucher: () => {
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

  const [value, setValue] = useState<PersonalVouchersValue>({ createVoucher });

  React.useEffect(() => {
    const loadGivenVouchers = async () => {
      const vouchers = await UsersService.usersMeVouchersGivenList();
      setValue((value) => ({ ...value, givenVouchers: vouchers }));
    };
    loadGivenVouchers();
  }, []);

  return <Context.Provider value={value}>{children}</Context.Provider>;
};
