ALTER TABLE function_runs ADD `status` text DEFAULT 'INITIAL';--> statement-breakpoint
ALTER TABLE function_runs ADD `error` text;