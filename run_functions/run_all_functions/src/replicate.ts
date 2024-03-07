import { ofetch } from "ofetch";
import { function_runs } from "./../../db/schema/function_runs";
import { runFunctionWrapper } from "./utils";
import { getDrizzleDb } from "./db";

export const runReplicate = async (env: Env, ctx: ExecutionContext) => {
  const functionConfigs = [
    {
      version:
        "7ba7d6ce64dcaf85b0c1efb6e1168417c6c05b0b76a9217394e2a153be662dec",
      gpuType: "t4",
      input: { number: 5 },
      functionType: "hello_gpu",
      vendor: "replicate",
    },
    {
      version:
        "3b297a2624682c11dfcbfd0aaecf9eebf14f2e8164069722cc733291ad5f22a0",

      gpuType: "t4",
      input: { number: 5 },
      functionType: "hello_torch",
      vendor: "replicate",
    },
  ];

  console.log(`Running ${functionConfigs.length} functions for Replicate.`);

  const runResults = await Promise.all(
    functionConfigs.map(async (config) => {
      const result = await runFunctionWrapper<
        (ReplicateResponse | ReplicateSuccessResponse) & { isSuccess: boolean }
      >({
        promise: runReplicateWithPolling({
          version: config.version,
          input: config.input,
          env,
        }),
      });
      return { config, result };
    })
  );

  const insertValues = runResults.map(({ result, config }) => {
    if (result.isSuccess) {
      return {
        vendor: config.vendor,
        total_time_ms: result.durationMs,
        run_time_ms: result.runTimeMs,
        gpu_type: config.gpuType,
        function_type: config.functionType,
        status: "SUCCESS",
      };
    } else {
      return {
        vendor: config.vendor,
        total_time_ms: result.durationMs,
        run_time_ms: undefined,
        gpu_type: config.gpuType,
        function_type: config.functionType,
        status: "FAILURE",
        error: result.error,
      };
    }
  });

  const drizzleDb = getDrizzleDb({ env });
  const insertRunResult = await drizzleDb
    .insert(function_runs)
    .values(insertValues)
    .returning({ id: function_runs.id })
    .run();
  console.log("insertRunResult", insertRunResult);
  return insertRunResult;
};

const runReplicateWithPolling = async ({
  version,
  input,
  env,
}: {
  version: string;
  input: Record<string, number | string>;
  env: Env;
}) => {
  const prediction = await ofetch<ReplicateResponse>(
    `https://api.replicate.com/v1/predictions`,
    {
      body: {
        input,
        version,
      },
      headers: { Authorization: `Token ${env.REPLICATE_API_TOKEN}` },
      method: "POST",
    }
  );

  console.log("prediction", prediction);

  let predictionStatus = prediction;

  while (["starting", "processing"].includes(predictionStatus.status)) {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    console.log("Polling");
    predictionStatus = await ofetch<ReplicateResponse>(prediction.urls.get, {
      headers: { Authorization: `Token ${env.REPLICATE_API_TOKEN}` },
    });
  }

  return {
    ...predictionStatus,
    isSuccess: predictionStatus.status === "succeeded",
    runTimeMs: predictionStatus.metrics
      ? Math.round(predictionStatus.metrics.predict_time * 1000)
      : undefined,
  };
};
