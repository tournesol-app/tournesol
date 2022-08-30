import React, { createContext, useContext, useCallback, useState } from 'react';

import { UsersService } from 'src/services/openapi';

interface PersonalVouchersValue {
  createVoucher: ({ username }: { username: string }) => void;
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
      const response = await UsersService.usersMeVouchersCreate({
        requestBody: { to: username },
      });
      return response;
    },
    []
  );
  const [value] = useState({ createVoucher });

  return <Context.Provider value={value}>{children}</Context.Provider>;
};
