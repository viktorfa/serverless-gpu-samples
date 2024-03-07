import { drizzle } from "drizzle-orm/libsql";
import { createClient } from "@libsql/client";
import { vendors } from "./db/schema/vendors";

const turso = createClient({
  url: "libsql://localhost:8080?tls=0",
});

const db = drizzle(turso);

db.select()
  .from(vendors)
  .run()
  .then((result) => {
    console.log(result);
  });
