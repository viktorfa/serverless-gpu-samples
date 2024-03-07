import { drizzle } from "drizzle-orm/libsql";
import { migrate } from "drizzle-orm/libsql/migrator";
import { createClient } from "@libsql/client";
import drizzleConfig from "./drizzle.config";

const turso = createClient({
  url: drizzleConfig.dbCredentials.url,
  authToken: drizzleConfig.dbCredentials.authToken,
});

const db = drizzle(turso);

migrate(db, {
  migrationsFolder: "./migrations",
});
