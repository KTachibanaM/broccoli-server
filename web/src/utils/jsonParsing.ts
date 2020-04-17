export const parseJsonOrObject = (value: string): object => {
  try {
    return JSON.parse(value);
  } catch {
    return {};
  }
};
