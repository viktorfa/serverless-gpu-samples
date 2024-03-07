export const runFunctionWrapper = async <T = any>({
  promise,
}: {
  promise: Promise<
    T & { isSuccess: boolean; error?: string; runTimeMs?: number }
  >;
}): Promise<{
  result?: T;
  durationMs: number;
  runTimeMs?: number;
  isSuccess: boolean;
  error?: string;
}> => {
  const startTimeMs = Date.now();
  let result;
  try {
    result = await promise;
  } catch (e) {
    const error = e as Error;
    const endTimeMs = Date.now();
    const durationMs = endTimeMs - startTimeMs;
    console.warn("Error when invoking function.");
    console.warn(error);
    return { error: error.message, durationMs, isSuccess: false };
  }
  const endTimeMs = Date.now();
  const durationMs = endTimeMs - startTimeMs;
  return {
    result,
    durationMs,
    isSuccess: result.isSuccess,
    runTimeMs: result.runTimeMs,
    error: result.error,
  };
};
