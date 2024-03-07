type Env = {
  REPLICATE_API_TOKEN: string;
  MYSTIC_API_TOKEN: string;
  WEBHOOK_SECRET: string;
  DB_URL: string;
  TURSO_DATABASE_AUTH_TOKEN?: string;
};

type ReplicateResponse = {
  id: string;
  model: string;
  version: string;
  input: Record<string, number | string>;
  logs: string;
  error: string | null;
  status: "starting" | "processing" | "succeeded" | "failed" | "canceled";
  created_at: string;
  urls: {
    cancel: string;
    get: string;
  };
};

type ReplicateSuccessResponse = ReplicateResponse & {
  status: "succeeded";
  metrics: { predict_time: number };
  error: null;
};
