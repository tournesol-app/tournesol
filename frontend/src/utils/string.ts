export const snakeToCamel = (str: string) => {
  // Convert `str` from snake_case to camelCase
  return str.replace(
    /(.)([-_][a-z])/g,
    (_, g1: string, g2: string) =>
      `${g1}${g2.toUpperCase().replace('-', '').replace('_', '')}`
  );
};
