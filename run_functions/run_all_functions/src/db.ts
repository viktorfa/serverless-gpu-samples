import { drizzle } from "drizzle-orm/libsql";
import { createClient } from "@libsql/client";

let drizzleDb: ReturnType<typeof drizzle> | undefined;

export const getDrizzleDb = ({ env }: { env: Env }) => {
  if (!drizzleDb) {
    const turso = createClient({
      url: env.DB_URL,
      authToken: env.TURSO_DATABASE_AUTH_TOKEN,
    });
    drizzleDb = drizzle(turso);
  }
  return drizzleDb;
};
