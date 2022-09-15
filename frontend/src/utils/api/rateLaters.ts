import { UsersService } from 'src/services/openapi';

export const addToRateLaterList = async (pollName: string, uid: string) => {
  return UsersService.usersMeRateLaterCreate({
    pollName: pollName,
    requestBody: {
      entity: { uid: uid },
    },
  });
};
