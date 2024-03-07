import { Hono } from "hono";
import { function_runs } from "./../../db/schema/function_runs";
import { vendors } from "./../../db/schema/vendors";
import { runReplicate } from "./replicate";
import { runMystic } from "./mystic";
import { getDrizzleDb } from "./db";

const app = new Hono<{ Bindings: Env }>();

app.get("/", async (c) => {
  const drizzleDb = getDrizzleDb(c);
  console.log("c.env.DB_URL", c.env.DB_URL);
  const runsResult = await drizzleDb.select().from(function_runs).run();
  const vendorsResult = await drizzleDb.select().from(vendors).run();

  return c.json({
    runs: runsResult.rows,
    vendors: vendorsResult.rows,
  });
});
app.get("/run_all", async (c) => {
  const token = c.req.query("_token");
  if (token !== c.env.WEBHOOK_SECRET) {
    return c.json({ error: "Invalid token" }, 401);
  }
  const results = await Promise.all([
    runReplicate(c.env, c.executionCtx),
    runMystic(c.env, c.executionCtx),
  ]);

  console.log(results);

  return c.json({
    results: results,
  });
});

export default {
  async scheduled(
    event: ScheduledEvent,
    env: Env,
    ctx: ExecutionContext
  ): Promise<void> {
    const results = await Promise.all([
      runReplicate(env, ctx),
      runMystic(env, ctx),
    ]);

    console.log(results);
  },
  fetch: app.fetch,
};
