const { deepMerge } = require('../../src/utils');

describe('deepMerge utility', () => {
  test('should merge simple flat objects', () => {
    const target = { a: 1 };
    const source = { b: 2 };
    const result = deepMerge(target, source);
    expect(result).toEqual({ a: 1, b: 2 });
  });

  test('should overwrite primitive values', () => {
    const target = { a: 1, b: 2 };
    const source = { b: 3 };
    const result = deepMerge(target, source);
    expect(result).toEqual({ a: 1, b: 3 });
  });

  test('should deep merge nested objects', () => {
    const target = { 
      general: { vimMode: false, theme: 'dark' },
      ui: { sidebar: true }
    };
    const source = { 
      general: { vimMode: true }
    };
    const result = deepMerge(target, source);
    expect(result).toEqual({ 
      general: { vimMode: true, theme: 'dark' },
      ui: { sidebar: true }
    });
  });

  test('should create nested objects if they do not exist', () => {
    const target = { a: 1 };
    const source = { b: { c: 2 } };
    const result = deepMerge(target, source);
    expect(result).toEqual({ a: 1, b: { c: 2 } });
  });

  test('should handle source being null or undefined', () => {
    const target = { a: 1 };
    expect(deepMerge(target, null)).toEqual(target);
    expect(deepMerge(target, undefined)).toEqual(target);
  });

  test('should handle target being null or undefined', () => {
    const source = { a: 1 };
    expect(deepMerge(null, source)).toEqual(source);
    expect(deepMerge(undefined, source)).toEqual(source);
  });

  test('should not merge arrays (should overwrite them)', () => {
    const target = { list: [1, 2] };
    const source = { list: [3, 4] };
    const result = deepMerge(target, source);
    expect(result).toEqual({ list: [3, 4] });
  });
});
