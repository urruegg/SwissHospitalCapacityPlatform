import { builtinEnvironments, type Environment } from 'vitest/environments';

const environment: Environment = {
  name: 'jsdom-compatible',
  transformMode: 'web',
  async setup(global, options) {
    // React Router's data router passes AbortSignal to Node's Request.
    // Keep those two web-platform constructors from the same implementation.
    const nativeAbortController = global.AbortController;
    const nativeAbortSignal = global.AbortSignal;
    const result = await builtinEnvironments.jsdom.setup(global, options);

    global.AbortController = nativeAbortController;
    global.AbortSignal = nativeAbortSignal;

    return result;
  },
};

export default environment;
