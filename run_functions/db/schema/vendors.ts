import { integer, sqliteTable, text } from "drizzle-orm/sqlite-core";
import { sql } from "drizzle-orm";

export const vendors = sqliteTable("vendors", {
  id: text("id").primaryKey(),
  created_at: integer("created_at", { mode: "timestamp_ms" }).default(
    sql`CURRENT_TIMESTAMP`
  ),
  title: text("title").notNull(),
});
