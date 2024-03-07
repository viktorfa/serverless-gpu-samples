CREATE TABLE `function_runs` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`created_at` integer DEFAULT CURRENT_TIMESTAMP,
	`vendor` text NOT NULL,
	`total_time_ms` integer NOT NULL,
	`start_time_ms` integer,
	`run_time_ms` integer,
	`gpu_type` text NOT NULL,
	`function_type` text NOT NULL,
	`cold_start` integer,
	`gpu_memory` integer,
	`cpu_memory` integer,
	`is_shared` integer,
	FOREIGN KEY (`vendor`) REFERENCES `vendors`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `vendors` (
	`id` text PRIMARY KEY NOT NULL,
	`created_at` integer DEFAULT CURRENT_TIMESTAMP,
	`title` text NOT NULL
);
