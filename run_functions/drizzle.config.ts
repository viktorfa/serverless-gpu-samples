import type { Config } from "drizzle-kit";
import * as dotenv from "dotenv";

let dotenvPath = ".env.local";

if (process.env.NODE_ENV === "production") {
  dotenvPath = ".env.prod";
}

dotenv.config({
  path: dotenvPath,
});

console.log(`Running Turso with ${dotenvPath}`);

export default {
  schema: "./db/schema",
  out: "./migrations",
  driver: "turso",
  dbCredentials: {
    url: process.env.DB_URL!,
    authToken: process.env.TURSO_DATABASE_AUTH_TOKEN,
  },
} satisfies Config;
