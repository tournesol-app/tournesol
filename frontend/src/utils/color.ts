// Copied from https://stackoverflow.com/a/59387478
export const lighten = (color: string, lighten: number) => {
  const c = color.replace('#', '');
  const rgb = [
    parseInt(c.substr(0, 2), 16),
    parseInt(c.substr(2, 2), 16),
    parseInt(c.substr(4, 2), 16),
  ];
  let returnstatement = '#';
  rgb.forEach((color) => {
    returnstatement += Math.round(
      (255 - color) * (1 - Math.pow(Math.E, -lighten)) + color
    ).toString(16);
  });
  return returnstatement;
};
