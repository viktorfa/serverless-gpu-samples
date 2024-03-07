import { ofetch } from "ofetch";
import { function_runs } from "./../../db/schema/function_runs";
import { runFunctionWrapper } from "./utils";
import { getDrizzleDb } from "./db";

type MysticInputType =
  | "integer"
  | "string"
  | "fp"
  | "dictionary"
  | "boolean"
  | "none"
  | "array"
  | "pkl"
  | "file";

type MysticRunStatus =
  | "created"
  | "routing"
  | "queued"
  | "running"
  | "completed"
  | "failed"
  | "no_resources_available"
  | "unknown";

type MysticRunResponse = {
  inputs: {
    type: MysticInputType;
    value?: string | number;
    file_name?: string;
    file_path?: string;
    file_url?: string;
  }[];
  outputs: {
    type: MysticInputType;
    value?: string | number;
    file?: { name: string; path: string; url?: string; size: number };
  }[];
  error?: { type: string; message: string; traceback: string };
  id: string;
  created_at: string;
  updated_at: string;
  pipeline_id: string;
  state: MysticRunStatus;
};

export const runMystic = async (env: Env, ctx: ExecutionContext) => {
  const functionConfigs = [
    {
      version: "vikfand/hello-gpu:v5",
      gpuType: "t4",
      input: [
        {
          type: "integer",
          value: 5,
        },
      ],
      functionType: "hello_gpu",
      vendor: "mystic",
    },
    {
      version: "vikfand/hello-torch:v5",
      gpuType: "t4",
      input: [
        {
          type: "integer",
          value: 5,
        },
      ],
      functionType: "hello_torch",
      vendor: "mystic",
    },
  ];

  console.log(`Running ${functionConfigs.length} functions for Mystic.ai.`);

  const runResults = await Promise.all(
    functionConfigs.map(async (config) => {
      const result = await runFunctionWrapper<
        MysticRunResponse & { isSuccess: boolean }
      >({
        promise: runMysticWithPolling({
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

const runMysticWithPolling = async ({
  version,
  input,
  env,
}: {
  version: string;
  input: { type: string; value: string | number }[];
  env: Env;
}) => {
  const prediction = await ofetch<MysticRunResponse>(
    `https://www.mystic.ai/v4/runs`,
    {
      body: {
        inputs: input,
        pipeline: version,
        async_run: false,
        wait_for_resources: true,
      },
      headers: { Authorization: `Bearer ${env.MYSTIC_API_TOKEN}` },
      method: "POST",
    }
  );

  console.log("prediction", prediction);

  return {
    ...prediction,
    isSuccess: prediction.state === "completed",
    error: prediction.error?.message,
  };
};
