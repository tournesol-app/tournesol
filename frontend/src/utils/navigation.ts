export const absolutePollBasePath = (path: string | undefined) => {
  if (!path || path === '/') {
    return '';
  }

  return path.startsWith('/') ? path : `/${path}`;
};
