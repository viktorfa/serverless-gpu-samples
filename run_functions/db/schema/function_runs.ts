import { integer, sqliteTable, text } from "drizzle-orm/sqlite-core";
import { sql } from "drizzle-orm";
import { vendors } from "./vendors";

export const function_runs = sqliteTable("function_runs", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  created_at: integer("created_at", { mode: "timestamp_ms" }).default(
    sql`CURRENT_TIMESTAMP`
  ),
  vendor: text("vendor")
    .notNull()
    .references(() => vendors.id),
  total_time_ms: integer("total_time_ms").notNull(),
  start_time_ms: integer("start_time_ms"),
  run_time_ms: integer("run_time_ms"),
  gpu_type: text("gpu_type").notNull(),
  function_type: text("function_type").notNull(),
  cold_start: integer("cold_start", { mode: "boolean" }),
  gpu_memory_mb: integer("gpu_memory"),
  cpu_memory_mb: integer("cpu_memory"),
  is_shared: integer("is_shared", { mode: "boolean" }),
  status: text("status").default("INITIAL"),
  error: text("error"),
  vendor_run_id: text("vendor_run_id"),
});
